import random, asyncio, os, requests, string
from asyncio import TimeoutError
from web.utils.file_properties import get_hash
from pyrogram import Client, filters, enums
from info import *
from utils import get_size
from .fsub import get_fsub
from Script import script
from database.users_db import db
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

@Client.on_message((filters.private) & (filters.document | filters.video | filters.audio) , group=4)
async def private_receive_handler(c: Client, m: Message):
    file_id = m.document or m.video or m.audio
    try:  # This is the outer try block
        msg = await m.copy(
            chat_id=BIN_CHANNEL,
            caption=f"**File Name:** {file_id.file_name}\n\n**Requested By:** {m.from_user.mention}")
        
        stream = f"{URL}watch/{str(msg.id)}?hash={get_hash(msg)}"
        download = f"{URL}{str(msg.id)}?hash={get_hash(msg)}"
        file_name = file_id.file_name.replace("_", " ").replace(".mp4", "").replace(".mkv", "").replace(".", " ")
        size=get_size(file_id.file_size)
        
        a = await msg.reply_text(
            text=f"ʀᴇǫᴜᴇꜱᴛᴇᴅ ʙʏ : [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nUꜱᴇʀ ɪᴅ : {m.from_user.id}\nStream ʟɪɴᴋ : {stream}",
            disable_web_page_preview=True, quote=True
        )

     #  await m.delete()  # Delete the original message after processing
        
        if FSUB:
            is_participant = await get_fsub(c, m)
            if not is_participant:
               return
                
        ban_chk = await db.is_banned(int(m.from_user.id))
        if ban_chk == True:
            return await m.reply(BAN_ALERT)
        
        k = await m.reply_text(
            text=script.CAPTION_TXT.format(file_name, size, stream, download),
            quote=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎞️ sᴛʀᴇᴀᴍ ᴏɴʟɪɴᴇ 🎞️", url=stream),
                 InlineKeyboardButton("💾 ɪɴsᴛᴀɴᴛ ᴅᴏᴡɴʟᴏᴀᴅ 💾", url=download)]
            ])
        )
        
        # Wait for 6 hours (21600 seconds)
#       await asyncio.sleep(21600)  # Sleep for 6 hours

        # After 6 hours, delete `log_msg`, `a`, and `k`
   #    try:
         #  await log_msg.delete()
         #  await a.delete()
        #   await k.delete()
      # except Exception as e:
          # print(f"Error during deletion: {e}")

    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=BIN_CHANNEL, text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`", disable_web_page_preview=True)

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

@Client.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo)  & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in BAN_CHNL:
        print("chat trying to get straming link is found in BAN_CHNL,so im not going to give stram link")
        return
    ban_chk = await db.is_banned(int(broadcast.chat.id))
    if (int(broadcast.chat.id) in BANNED_CHANNELS) or (ban_chk == True):
        await bot.leave_chat(broadcast.chat.id)
        return
    try:  # This is the outer try block
        msg = await broadcast.forward(chat_id=BIN_CHANNEL)
        stream = f"{URL}watch/{str(msg.id)}?hash={get_hash(msg)}"
        download = f"{URL}{str(msg.id)}?hash={get_hash(msg)}"

        await msg.reply_text(
            text=f"**Channel Name:** `{broadcast.chat.title}`\n**CHANNEL ID:** `{broadcast.chat.id}`\n**Rᴇǫᴜᴇsᴛ ᴜʀʟ:** {stream}",
            quote=True
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎞️ sᴛʀᴇᴀᴍ ᴏɴʟɪɴᴇ 🎞️", url=stream),
                 InlineKeyboardButton("💾 ɪɴsᴛᴀɴᴛ ᴅᴏᴡɴʟᴏᴀᴅ 💾", url=download)]
            ])
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=BIN_CHANNEL,
                            text=f"GOT FLOODWAIT OF {str(w.x)}s FROM {broadcast.chat.title}\n\n**CHANNEL ID:** `{str(broadcast.chat.id)}`",
                            disable_web_page_preview=True)
    except Exception as e:
        await bot.send_message(chat_id=BIN_CHANNEL, text=f"**#ERROR_TRACKEBACK:** `{e}`", disable_web_page_preview=True)
        print(f"Cᴀɴ'ᴛ Eᴅɪᴛ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ!\nEʀʀᴏʀ:  **Give me edit permission in updates and bin Channel!{e}**")

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP
