# (c) CW4RR10R | @AbirHasan2005

import os
import uuid
import shutil
import logging
import asyncio
import traceback
from pyrogram import Client, filters
from core.creds import Credentials
from core.sessionname import SESSION_NAME
from core.database import Database
from telegraph import upload_file
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

## --- Logger --- ##
logging.basicConfig(level=logging.INFO)


## --- Bot --- ##
Mo_tech_yt = Client(
    SESSION_NAME,
    bot_token=Credentials.BOT_TOKEN,
    api_id=Credentials.API_ID,
    api_hash=Credentials.API_HASH,
)


## --- Sub Configs --- ##
db = Database(Credentials.MONGODB_URI, SESSION_NAME)
broadcast_ids = {}
home_text = None
if Credentials.HOME_MSG:
    home_text = Credentials.HOME_MSG
else:
    home_text = """
Hai [{}](tg://user?id={})

`I'm a simple Telegraph Uploader bot`.`I can convert under 5MB media or file to telegra.ph links`.

👲 ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : [ʙx ʙᴏᴛᴢ](https://telegram.me/BX_Botz)
"""
about_text = None
if Credentials.ABOUT_MSG:
    about_text = Credentials.ABOUT_MSG
else:
    about_text = """
➠ **Bot** : Telegraph Uploader

➠ **Creator** : [ᴍʜᴅ ᴍᴜꜰᴀz](https://telegram.me/Mufaz123)

➠ **Channel** : @BX_Botz

➠ **Source** : [Click here](https://t.me/nokiyirunnoippokitum)

➠ **Language** : [Python](https://python.org/)

➠ **Library** : [Pyrogram v1.2.0](https://pyrogram.org/)

➠ **Server** : [Heroku](https://heroku.com/)
"""
if Credentials.HOME_MSG:
    help_text = Credentials.HELP_MSG
else:
    help_text = """
➠ `Just give me a media under 5MB`
➠ `Then I will download it`
➠ `I will then upload it to the telegra.ph link`
"""
async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"

## --- Start Handler --- ##
@Mo_tech_yt.on_message(filters.command(["start"]) & filters.private, group=1)
async def start(client, message):
    await message.reply_text(Hai [{}](tg://user?id={})

`I'm a simple Telegraph Uploader bot`.`I can convert under 5MB media or file to telegra.ph links`.

👲 ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : [ʙx ʙᴏᴛᴢ](https://telegram.me/BX_Botz)
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🤖Bot Updates", url="https://telegram.dog/BX_Botz"),
                    InlineKeyboardButton("👥Support Group", url="https://telegram.dog/BxSupport")
                ],
                [
                    InlineKeyboardButton("⚙️Help", callback_data="help"),
                    InlineKeyboardButton("🔰About", callback_data="about")
                ]
            ]
        ),
        parse_mode="html",
        disable_web_page_preview=True
    )

## --- help Handler --- ##
@Mo_tech_yt.on_message(filters.command("help"))
async def help(client, message):
   await message.reply_text(
       "➠ `Just give me a media under 5MB`\n\n➠ `Then I will download it`\n\n➠ `I will then upload it to the telegra.ph link`",
       reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🤖Bot Updates", url="https://telegram.dog/BX_Botz"),
                    InlineKeyboardButton("👥Support Group", url="https://telegram.dog/BxSupport")
                ],
                [
                    InlineKeyboardButton("🏠Home", callback_data="home"),
                    InlineKeyboardButton("🔰About", callback_data="about")
                ]
            ]
        ),
        parse_mode="html",
        disable_web_page_preview=True
    )

@Mo_tech_yt.on_message(filters.private & filters.command("status") & filters.user(Credentials.ADMIN))
async def sts(bot, cmd):
    total_users = await db.total_users_count()
    await cmd.reply_text(text=f"**Total Users in DB:** `{total_users}`", parse_mode="Markdown")


@Mo_tech_yt.on_message(filters.private & filters.command("broadcast") & filters.user(Credentials.ADMIN) & filters.reply)
async def broadcast_(c, m):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text = f"Broadcast initiated! You will be notified with log file when all the users are notified."
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total = total_users,
        current = done,
        failed = failed,
        success = success
    )
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(
                user_id = int(user['id']),
                message = broadcast_msg
            )
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(
                        current = done,
                        failed = failed,
                        success = success
                    )
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time()-start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    await aiofiles.os.remove('broadcast.txt')


@Mo_tech_yt.on_message(filters.private & (filters.photo | filters.document))
async def getimage(client, message):
    if message.document:
        if not message.document.file_name.endswith(".jpg"):
            return
    tmp = os.path.join("downloads", str(message.chat.id))
    if not os.path.isdir(tmp):
        os.makedirs(tmp)
    img_path = os.path.join(tmp, str(uuid.uuid4()) + ".jpg")
    dwn = await message.reply_text("🅳︎🅾︎🆆︎🅽︎🅻︎🅾︎🅰︎🅳︎🅸︎🅽︎🅶︎....", True)
    img_path = await client.download_media(message=message, file_name=img_path)
    await dwn.edit_text("🆄︎🅿︎🅻︎🅾︎🅰︎🅳︎🅸︎🅽︎🅶︎....")
    try:
        response = upload_file(img_path)
    except Exception as error:
        await dwn.edit_text(f"Oops, Something went wrong!\n\n**Error:** {error}")
        return
    await dwn.edit_text(f"https://telegra.ph{response[0]}")
    shutil.rmtree(tmp, ignore_errors=True)

## --- Custom Callback Filter --- ##
def dynamic_data_filter(data):
    async def func(flt, _, query):
        return flt.data == query.data
    return filters.create(func, data=data)

@Mo_tech_yt.on_callback_query(dynamic_data_filter("about"))
async def about_meh(_, query):
    buttons = [
        [
           InlineKeyboardButton("⚙️Help", callback_data="help"),
           InlineKeyboardButton("🏠Home", callback_data="home"),
           InlineKeyboardButton("🔐Close", callback_data="closeit")
        ]
    ]
    await query.message.edit(
        about_text,
        parse_mode="markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    await query.answer()

@Mo_tech_yt.on_callback_query(dynamic_data_filter("help"))
async def help_meh(_, query):
    buttons = [
        [
           InlineKeyboardButton("📣Channel", url="https://telegram.dog/BX_Botz"),
           InlineKeyboardButton("👥Group", url="https://telegram.dog/BxSupport"),
           InlineKeyboardButton("💡Bot List", url="https://t.me/BX_Botz/31")
        ],
        [
           InlineKeyboardButton("⚙️About", callback_data="about"),
           InlineKeyboardButton("🏠Home", callback_data="home"),
           InlineKeyboardButton("🔐Close", callback_data="closeit")
        ]
    ]
    await query.message.edit(
        help_text,
        parse_mode="markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    await query.answer()

@Mo_tech_yt.on_callback_query(dynamic_data_filter("home"))
async def go_to_home(_, query):
    buttons = [
        [
                    InlineKeyboardButton("🤖 Bot Updates", url="https://telegram.dog/BX_Botz"),
                    InlineKeyboardButton("👥Support Group", url="https://telegram.dog/BxSupport")
                ],
                [
                    InlineKeyboardButton("⚙️Help", callback_data="help"),
                    InlineKeyboardButton("🔰About", callback_data="about")
        ]
    ]
    await query.message.edit(
        home_text.format(query.message.chat.first_name, query.message.chat.id),
        parse_mode="markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()

@Mo_tech_yt.on_callback_query(dynamic_data_filter("closeit"))
async def closeme(_, query):
    await query.message.delete()
    await query.answer()


Mo_tech_yt.run()
