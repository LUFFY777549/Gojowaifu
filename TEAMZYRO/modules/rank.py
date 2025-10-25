from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import asyncio
import html
from TEAMZYRO import app, user_collection, top_global_groups_collection

PHOTO_URL = ["https://files.catbox.moe/9j8e6b.jpg"]

MAX_CAPTION_LENGTH = 1024

# ----------------- Helper Functions ----------------- #
def build_user_leaderboard(data):
    caption = "<b>ᴛᴏᴘ 10 ᴜsᴇʀs ᴡɪᴛʜ ᴍᴏsᴛ ᴄʜᴀʀᴀᴄᴛᴇʀs</b>\n\n"
    for i, user in enumerate(data, start=1):
        user_id = user.get('id', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))
        if len(first_name) > 15:
            first_name = first_name[:15] + "..."
        character_count = len(user.get('characters', []))
        new_line = f'{i}. <a href="tg://user?id={user_id}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'
        if len(caption) + len(new_line) <= MAX_CAPTION_LENGTH:
            caption += new_line
        else:
            caption += "..."
            break
    return caption

def build_group_leaderboard(data):
    caption = "<b>ᴛᴏᴘ 10 ɢʀᴏᴜᴘs ᴡʜᴏ ɢᴜssᴇᴅ ᴍᴏsᴛ ᴄʜᴀʀᴀᴄᴛᴇʀs</b>\n\n"
    for i, group in enumerate(data, start=1):
        group_name = html.escape(group.get('group_name', 'Unknown'))
        if len(group_name) > 15:
            group_name = group_name[:15] + "..."
        count = group['count']
        new_line = f'{i}. <b>{group_name}</b> ➾ <b>{count}</b>\n'
        if len(caption) + len(new_line) <= MAX_CAPTION_LENGTH:
            caption += new_line
        else:
            caption += "..."
            break
    return caption

def build_coin_leaderboard(data):
    caption = "<b>ᴛᴏᴘ 10 ᴜsᴇʀs ᴡɪᴛʜ ᴍᴏsᴛ ᴄᴏɪɴs</b>\n\n"
    for i, user in enumerate(data, start=1):
        user_id = user.get('id', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))
        if len(first_name) > 15:
            first_name = first_name[:15] + "..."
        coins = user.get('coins', 0)
        new_line = f'{i}. <a href="tg://user?id={user_id}"><b>{first_name}</b></a> ➾ <b>{coins}</b>\n'
        if len(caption) + len(new_line) <= MAX_CAPTION_LENGTH:
            caption += new_line
        else:
            caption += "..."
            break
    return caption

def get_buttons(active_button):
    buttons = [
        [
            InlineKeyboardButton("ᴛᴏᴘ🥀" if active_button == "top" else "Top", callback_data="top"),
            InlineKeyboardButton("ᴛᴏᴘ ɢʀᴏᴜᴘ🥀" if active_button == "top_group" else "Top Group", callback_data="top_group")
        ],
        [
            InlineKeyboardButton("ᴍᴛᴏᴘ🥀" if active_button == "mtop" else "MTOP", callback_data="mtop")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

# ----------------- /rank Command ----------------- #
@app.on_message(filters.command("rank"))
async def rank(client, message):
    cursor = user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "characters": 1})
    leaderboard_data = await cursor.to_list(length=None)
    leaderboard_data.sort(key=lambda x: len(x.get('characters', [])), reverse=True)
    leaderboard_data = leaderboard_data[:10]

    caption = build_user_leaderboard(leaderboard_data)

    await message.reply_photo(
        photo=random.choice(PHOTO_URL),
        caption=caption,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=get_buttons("top")
    )

# ----------------- Callback Queries ----------------- #
@app.on_callback_query(filters.regex("^top$"))
async def top_callback(client, callback_query):
    await asyncio.sleep(0.3)
    cursor = user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "characters": 1})
    leaderboard_data = await cursor.to_list(length=None)
    leaderboard_data.sort(key=lambda x: len(x.get('characters', [])), reverse=True)
    leaderboard_data = leaderboard_data[:10]

    caption = build_user_leaderboard(leaderboard_data)

    try:
        await callback_query.edit_message_caption(
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=get_buttons("top")
        )
    except Exception as e:
        await callback_query.answer(f"❌ Button expired! Try /rank again.", show_alert=True)

@app.on_callback_query(filters.regex("^top_group$"))
async def top_group_callback(client, callback_query):
    await asyncio.sleep(0.3)
    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    caption = build_group_leaderboard(leaderboard_data)

    try:
        await callback_query.edit_message_caption(
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=get_buttons("top_group")
        )
    except Exception as e:
        await callback_query.answer(f"❌ Button expired! Try /rank again.", show_alert=True)

@app.on_callback_query(filters.regex("^mtop$"))
async def mtop_callback(client, callback_query):
    await asyncio.sleep(0.3)
    cursor = user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "coins": 1})
    leaderboard_data = await cursor.to_list(length=None)
    leaderboard_data.sort(key=lambda x: x.get('coins', 0), reverse=True)
    leaderboard_data = leaderboard_data[:10]

    caption = build_coin_leaderboard(leaderboard_data)

    try:
        await callback_query.edit_message_caption(
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=get_buttons("mtop")
        )
    except Exception as e:
        await callback_query.answer(f"❌ Button expired! Try /rank again.", show_alert=True)