import random, asyncio, os, requests, string
from asyncio import TimeoutError
from web.utils.file_properties import get_hash
from pyrogram import Client, filters, enums
from info import *
from utils import get_size
from .fsub import get_fsub
from Script import script
from database.users_db import db
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote

@Client.on_message((filters.private) & (filters.document | filters.video | filters.audio), group=4)
async def private_receive_handler(c: Client, m: Message):
    file_id = m.document or m.video or m.audio
    try:
        msg = await m.copy(
            chat_id=BIN_CHANNEL,
            caption=f"**File Name:** {file_id.file_name}\n\n**Requested By:** {m.from_user.mention}"
        )

        stream = f"{URL.rstrip('/')}/watch/{quote(str(msg.id))}?hash={quote(get_hash(msg))}"
        download = f"{URL.rstrip('/')}/{quote(str(msg.id))}?hash={quote(get_hash(msg))}"

        # Validate URLs
        if not stream.startswith("https") or not download.startswith("https"):
            await m.reply_text("❌ Invalid stream or download link generated.")
            return

        file_name = file_id.file_name.replace("_", " ").replace(".mp4", "").replace(".mkv", "").replace(".", " ")
        size = get_size(file_id.file_size)

        a = await msg.reply_text(
            text=f"Requested by: [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n"
                 f"User ID: {m.from_user.id}\n"
                 f"Stream link: {stream}",
            disable_web_page_preview=True, quote=True
        )

        await m.delete()  # Delete the original message after processing
        
        if FSUB:
            is_participant = await get_fsub(c, m)
            if not is_participant:
                return
                
        ban_chk = await db.is_banned(int(m.from_user.id))
        if ban_chk:
            return await m.reply(BAN_ALERT)
        
        k = await m.reply_text(
            text=script.CAPTION_TXT.format(file_name, size, stream, download),
            quote=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• Stream •", url=stream),
                 InlineKeyboardButton("• Download •", url=download)]
            ])
        )
        
        # Wait for 6 hours (21600 seconds)
        await asyncio.sleep(21600)

        # After 6 hours, delete messages
        try:
            await msg.delete()
            await a.delete()
            await k.delete()
        except Exception as e:
            print(f"Error during deletion: {e}")

    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=BIN_CHANNEL,
            text=f"FloodWait triggered: {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n"
                 f"**User ID:** `{str(m.from_user.id)}`",
            disable_web_page_preview=True
        )


@Client.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in BAN_CHNL:
        print("Blocked channel trying to get streaming link, skipping...")
        return

    ban_chk = await db.is_banned(int(broadcast.chat.id))
    if (int(broadcast.chat.id) in BANNED_CHANNELS) or (ban_chk == True):
        await bot.leave_chat(broadcast.chat.id)
        return

    try:
        msg = await broadcast.forward(chat_id=BIN_CHANNEL)
        stream = f"{URL.rstrip('/')}/watch/{quote(str(msg.id))}?hash={quote(get_hash(msg))}"
        download = f"{URL.rstrip('/')}/{quote(str(msg.id))}?hash={quote(get_hash(msg))}"

        await msg.reply_text(
            text=f"**Channel Name:** `{broadcast.chat.title}`\n"
                 f"**Channel ID:** `{broadcast.chat.id}`\n"
                 f"**Request URL:** {stream}",
            quote=True
        )

        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Stream", url=stream),
                 InlineKeyboardButton("Download", url=download)]
            ])
        )

    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(
            chat_id=BIN_CHANNEL,
            text=f"FloodWait triggered: {str(w.x)}s from {broadcast.chat.title}\n\n"
                 f"**Channel ID:** `{str(broadcast.chat.id)}`",
            disable_web_page_preview=True
        )
    except Exception as e:
        await bot.send_message(
            chat_id=BIN_CHANNEL,
            text=f"**#ERROR_TRACEBACK:** `{e}`",
            disable_web_page_preview=True
        )
        print(f"Error: Give me edit permission in updates and bin Channel!\nDetails: {e}")
        
