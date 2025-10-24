from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random, asyncio, html
from TEAMZYRO import app, user_collection, top_global_groups_collection

PHOTO_URL = ["https://files.catbox.moe/9bhirj.jpg"]


# ---------------- HELPERS ---------------- #
def build_user_leaderboard(data):
    caption = "<b>🏆 TOP 10 USERS WITH MOST CHARACTERS 🏆</b>\n\n"
    for i, user in enumerate(data, start=1):
        user_id = user.get("id", "Unknown")
        first_name = html.escape(user.get("first_name", "Unknown"))
        if len(first_name) > 15:
            first_name = first_name[:15] + "..."
        count = len(user.get("characters", []))
        caption += f"{i}. <a href='tg://user?id={user_id}'><b>{first_name}</b></a> ➾ <b>{count}</b>\n"
    return caption


def build_group_leaderboard(data):
    caption = "<b>👥 TOP 10 GROUPS WHO GUESSED MOST CHARACTERS 👥</b>\n\n"
    for i, group in enumerate(data, start=1):
        name = html.escape(group.get("group_name", "Unknown"))
        if len(name) > 15:
            name = name[:15] + "..."
        count = group.get("count", 0)
        caption += f"{i}. <b>{name}</b> ➾ <b>{count}</b>\n"
    return caption


def build_coin_leaderboard(data):
    caption = "<b>💰 TOP 10 USERS WITH MOST COINS 💰</b>\n\n"
    for i, user in enumerate(data, start=1):
        user_id = user.get("id", "Unknown")
        name = html.escape(user.get("first_name", "Unknown"))
        if len(name) > 15:
            name = name[:15] + "..."
        coins = user.get("coins", 0)
        caption += f"{i}. <a href='tg://user?id={user_id}'><b>{name}</b></a> ➾ <b>{coins}</b>\n"
    return caption


def get_buttons(active):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏆 Top" if active == "top" else "Top", callback_data="rank_top"),
            InlineKeyboardButton("👥 Top Groups" if active == "group" else "Top Groups", callback_data="rank_group"),
        ],
        [
            InlineKeyboardButton("💰 Coin Top" if active == "coin" else "Coin Top", callback_data="rank_coin")
        ]
    ])


# ---------------- /rank COMMAND ---------------- #
@app.on_message(filters.command("rank"))
async def rank_cmd(client, message):
    data = await user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "characters": 1}).to_list(None)
    data.sort(key=lambda x: len(x.get("characters", [])), reverse=True)
    caption = build_user_leaderboard(data[:10])

    await message.reply_photo(
        random.choice(PHOTO_URL),
        caption=caption,
        reply_markup=get_buttons("top"),
        parse_mode=enums.ParseMode.HTML
    )


# ---------------- CALLBACK HANDLERS ---------------- #
@app.on_callback_query(filters.regex("^rank_top$"))
async def rank_top_cb(_, query):
    await query.answer("Loading Top Users...")
    data = await user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "characters": 1}).to_list(None)
    data.sort(key=lambda x: len(x.get("characters", [])), reverse=True)
    caption = build_user_leaderboard(data[:10])

    try:
        await query.message.edit_caption(caption=caption, reply_markup=get_buttons("top"), parse_mode=enums.ParseMode.HTML)
    except Exception:
        await query.message.reply_text(caption)


@app.on_callback_query(filters.regex("^rank_group$"))
async def rank_group_cb(_, query):
    await query.answer("Loading Top Groups...")
    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ])
    data = await cursor.to_list(length=10)
    caption = build_group_leaderboard(data)

    try:
        await query.message.edit_caption(caption=caption, reply_markup=get_buttons("group"), parse_mode=enums.ParseMode.HTML)
    except Exception:
        await query.message.reply_text(caption)


@app.on_callback_query(filters.regex("^rank_coin$"))
async def rank_coin_cb(_, query):
    await query.answer("Loading Top Coins...")
    data = await user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "coins": 1}).to_list(None)
    data.sort(key=lambda x: x.get("coins", 0), reverse=True)
    caption = build_coin_leaderboard(data[:10])

    try:
        await query.message.edit_caption(caption=caption, reply_markup=get_buttons("coin"), parse_mode=enums.ParseMode.HTML)
    except Exception:
        await query.message.reply_text(caption)


print("✅ /rank command with working callbacks loaded successfully!")