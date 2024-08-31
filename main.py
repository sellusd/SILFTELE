from pyrogram import Client, filters
from pyrogram.errors import FloodWait, MessageNotModified, MessageIdInvalid
from time import sleep, strftime, gmtime, time
from os import remove, makedirs
from os.path import join, isdir
from random import randint
import config

# استخدام القيم الخاصة بك
session_name = "example"
api_id = 21218666
api_hash = "351a32f1937b179b9ca47d9c5217883e"
channel_id = -1002170437771
last_messages_amount = 50

app = Client(session_name, api_id, api_hash)

if not isdir("downloads"):
    makedirs("downloads")

async def msg_info(msg):
    media_type = ""
    ttl = 0
    if hasattr(msg.photo, "ttl_seconds"):
        if msg.photo.ttl_seconds:
            media_type = "photo"
            ttl = msg.photo.ttl_seconds
    elif hasattr(msg.video, "ttl_seconds"):
        if msg.video.ttl_seconds:
            media_type = "video"
            ttl = msg.video.ttl_seconds

    if media_type:
        full_name = msg.from_user.first_name + (f' {msg.from_user.last_name}' if msg.from_user.last_name else '')
        sender = f"[{full_name}](tg://user?id={msg.from_user.id})"
        sending_time = f"{strftime('%x %X', gmtime(msg.date.timestamp()))}"
        return sender, media_type, sending_time, ttl
    else:
        return None, None, None, None

async def save_media(msg, sender, media_type, sending_time, ttl):
    try:
        mes = await app.send_message(channel_id, f"{sender} sent {media_type}, {sending_time}, {ttl}s\n__Uploading...__")
        file_type = ("jpg" if media_type == "photo" else "mp4")
        file_name = f"{msg.from_user.id}{time()*10000000}{randint(1, 10000000)}.{file_type}"
        await app.download_media(msg, file_name)
        mention = f"{sender}, {sending_time}, {ttl}s"
        with open(join("downloads", file_name), "rb") as att:
            if media_type == "photo":
                await app.send_photo(channel_id, att, mention)
            elif media_type == "video":
                await app.send_video(channel_id, att, mention)
        remove(join("downloads", file_name))
        await mes.delete()
    except FloodWait as e:
        sleep(e.x)
    except MessageIdInvalid:
        pass

@app.on_message(filters.command(["ass-hack", "asshack", "ah"], prefixes="!") & filters.me)
async def on_command(_, msg):
    try:
        if msg.text in ("!ass-hack", "!asshack", "!ah"):
            msg = await msg.edit(f"```{msg.text}```\n**Searching for self-destructing media...**")
            success = False
            my_id = (await app.get_me()).id
            dialogs = await app.get_dialogs()
            for dialog in dialogs:
                if dialog.chat.type == "private" and dialog.chat.id != my_id:
                    for mes in await app.get_history(dialog.chat.id, limit=last_messages_amount):
                        sender, media_type, sending_time, ttl = await msg_info(mes)
                        if sender:
                            success = True
                            msg = await msg.edit(f"{msg.text}\n￫ {sender} sent {media_type}, {sending_time}, {ttl}s")
                            await save_media(mes, sender, media_type, sending_time, ttl)

            if not success:
                await msg.edit(f"{msg.text}\n**Nobody sent something :c**")
            else:
                await msg.edit(f"{msg.text}\n**Done!**")

    except FloodWait as e:
        sleep(e.x)
    except MessageIdInvalid:
        pass

@app.on_message(filters.private & ~filters.me & (filters.photo | filters.video))
async def in_background(_, msg):
    try:
        sender, media_type, sending_time, ttl = await msg_info(msg)
        if sender:
            await save_media(msg, sender, media_type, sending_time, ttl)
    except FloodWait as e:
        sleep(e.x)
    except MessageIdInvalid:
        pass

app.run()
