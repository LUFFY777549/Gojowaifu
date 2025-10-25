import os
import random
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from TEAMZYRO import app, user_collection
from TEAMZYRO.unit.zyro_help import HELP_DATA
from pyrogram.errors import PeerIdInvalid

# 🔹 Start Media (Add only working links or local file paths)
START_MEDIA = [
    "https://files.catbox.moe/9bhirj.jpg"
]

# 🔹 Optional Log Channel ID
GLOG = os.getenv("GLOG", "-1002946070634")

# 🔹 Function to Calculate Uptime
START_TIME = time.time()


def get_uptime():
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


# 🔹 Function to Generate Private Start Message & Buttons
async def generate_start_message(client, message):
    bot_user = await client.get_me()
    bot_name = bot_user.first_name
    ping = round(time.time() - message.date.timestamp(), 2)
    uptime = get_uptime()

    caption = f"""🍃 ɢʀᴇᴇᴛɪɴɢs, ɪ'ᴍ {bot_name} 🫧, ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ!
╭━━━━━━━╾❁✦❁╼━━━━━━━╮
⟡ ɪ ᴀᴍ ʏᴏᴜʀ ᴡᴀɪғᴜ ɢᴇɴɪᴇ!  
    sᴜᴍᴍᴏɴ ᴄᴜᴛᴇ ᴡᴀɪғᴜs  
    ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ ✧

⟡ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ  
    & ᴛᴀᴘ /help ғᴏʀ ᴄᴏᴍᴍᴀɴᴅs
╰━━━━━━━╾❁✦❁╼━━━━━━━╯
➺ ᴘɪɴɢ: {ping} ms
➺ ᴜᴘᴛɪᴍᴇ: {uptime}"""

    buttons = [
        [InlineKeyboardButton("⋆ᴀᴅᴅ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ⋆", url=f"https://t.me/{bot_user.username}?startgroup=true")],
        [InlineKeyboardButton("❍sᴜᴘᴘᴏʀᴛ❍", url="https://t.me/AlphaBot_Support"),
         InlineKeyboardButton("❍ᴄʜᴀɴɴᴇʟ❍", url="https://t.me/Alpha_X_Updates")],
        [InlineKeyboardButton("⋆ʜᴇʟᴘ⋆", callback_data="open_help")],
        [InlineKeyboardButton("✦ʟᴏʀᴅ✦", url="http://t.me/Uzumaki_X_Naruto_6")]
    ]

    return caption, buttons


# 🔹 Function to Generate Group Start Message & Buttons
async def generate_group_start_message(client):
    bot_user = await client.get_me()
    caption = f"🍃 ɪ'ᴍ {bot_user.first_name} 🫧\nɪ sᴘᴀᴡɴ ᴡᴀɪғᴜs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ғᴏʀ ᴜsᴇʀs ᴛᴏ ɢʀᴀʙ.\nᴜsᴇ /help ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏ."
    buttons = [
        [
            InlineKeyboardButton("◦ᴀᴅᴅ ᴍᴇ◦", url=f"https://t.me/{bot_user.username}?startgroup=true"),
            InlineKeyboardButton("◦sᴜᴘᴘᴏʀᴛ◦", url="https://t.me/AlphaXBot_Support"),
        ]
    ]
    return caption, buttons


# 🔹 Private Start Command Handler
@app.on_message(filters.command("start") & filters.private)
async def start_private_command(client, message):
    # Save user data only if not exists
    existing_user = await user_collection.find_one({"id": message.from_user.id})
    if not existing_user:
        user_data = {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "start_time": time.time()
        }
        await user_collection.insert_one(user_data)

    caption, buttons = await generate_start_message(client, message)
    media = random.choice(START_MEDIA)

    # 🔧 Safe Logging Message
    try:
        if GLOG:
            await app.send_message(
                chat_id=int(GLOG),
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username or 'None'}",
            )
    except PeerIdInvalid:
        print(f"[⚠️ WARNING] GLOG ID {GLOG} invalid or bot not in chat. Skipping log.")
    except Exception as e:
        print(f"[❌ ERROR] Failed to send log message: {e}")

    # 🔹 Safe Media Sending
    try:
        if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            await message.reply_photo(photo=media, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        elif media.lower().endswith(('.mp4', '.mov', '.mkv')):
            await message.reply_video(video=media, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            # fallback if invalid media found
            await message.reply_photo(photo="https://files.catbox.moe/9bhirj.jpg", caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        print(f"[❌ ERROR] Failed to send start media: {e}")
        await message.reply_photo(
            photo="https://files.catbox.moe/9bhirj.jpg",
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# 🔹 Group Start Command Handler
@app.on_message(filters.command("start") & filters.group)
async def start_group_command(client, message):
    caption, buttons = await generate_group_start_message(client)
    media = random.choice(START_MEDIA)
    try:
        if media.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            await message.reply_photo(photo=media, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        elif media.lower().endswith(('.mp4', '.mov', '.mkv')):
            await message.reply_video(video=media, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await message.reply_photo(photo="https://files.catbox.moe/9bhirj.jpg", caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        print(f"[❌ ERROR] Failed to send group start media: {e}")
        await message.reply_text(caption)


# 🔹 Help Menu System
def find_help_modules():
    buttons = []
    for module_name, module_data in HELP_DATA.items():
        button_name = module_data.get("HELP_NAME", module_name.title())
        buttons.append(InlineKeyboardButton(button_name, callback_data=f"help_{module_name}"))
    return [buttons[i:i + 3] for i in range(0, len(buttons), 3)]


@app.on_callback_query(filters.regex("^open_help$"))
async def show_help_menu(client, query: CallbackQuery):
    buttons = find_help_modules()
    buttons.append([InlineKeyboardButton("⬅ Back", callback_data="back_to_home")])
    await query.message.edit_text(
        "*ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ғᴏʀ ʜᴇʟᴘ:*\n\nᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ /",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(r"^help_(.+)"))
async def show_help(client, query: CallbackQuery):
    module_name = query.data.split("_", 1)[1]
    module_data = HELP_DATA.get(module_name, {})
    help_text = module_data.get("HELP", "Is module ka koi help nahi hai.")
    buttons = [[InlineKeyboardButton("⬅ Back", callback_data="open_help")]]
    await query.message.edit_text(
        f"**{module_name.upper()} HELP:**\n\n{help_text}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("^back_to_home$"))
async def back_to_home(client, query: CallbackQuery):
    caption, buttons = await generate_start_message(client, query.message)
    await query.message.edit_text(caption, reply_markup=InlineKeyboardMarkup(buttons))