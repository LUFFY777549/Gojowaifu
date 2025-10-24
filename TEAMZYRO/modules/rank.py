from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random, asyncio, html
from TEAMZYRO import app, user_collection, top_global_groups_collection

PHOTO_URL = ["https://files.catbox.moe/9bhirj.jpg"]

# ----------------- Helper Builders ----------------- #
def build_user_leaderboard(data):
    caption = "<b>🏆 TOP 10 USERS WITH MOST CHARACTERS 🏆</b>\n\n"
    for i, user in enumerate(data, start=1):
        user_id = user.get('id', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))
        if len(first_name) > 15:
            first_name = first_name[:15] + "..."
        character_count = len(user.get('characters', []))
        caption += f"{i}. <a href='tg://user?id={user_id}'><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n"
    return caption

def build_group_leaderboard(data):
    caption = "<b>🏆 TOP 10 GROUPS WHO GUESSED MOST CHARACTERS 🏆</b>\n\n"
    for i, group in enumerate(data, start=1):
        group_name = html.escape(group.get('group_name', 'Unknown'))
        if len(group_name) > 15:
            group_name = group_name[:15] + "..."
        count = group['count']
        caption += f"{i}. <b>{group_name}</b> ➾ <b>{count}</b>\n"
    return caption

def build_coin_leaderboard(data):
    caption = "<b>💰 TOP 10 USERS WITH MOST COINS 💰</b>\n\n"
    for i, user in enumerate(data, start=1):
        user_id = user.get('id', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))
        if len(first_name) > 15:
            first_name = first_name[:15] + "..."
        coins = user.get('coins', 0)
        caption += f"{i}. <a href='tg://user?id={user_id}'><b>{first_name}</b></a> ➾ <b>{coins}</b>\n"
    return caption

def get_buttons(active):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🏆 Top" if active == "top" else "Top",
                callback_data="top"
            ),
            InlineKeyboardButton(
                "👥 Top Groups" if active == "top_group" else "Top Groups",
                callback_data="top_group"
            ),
        ],
        [
            InlineKeyboardButton(
                "💰 Coin Top" if active == "mtop" else "Coin Top",
                callback_data="mtop"
            )
        ]
    ])


# ----------------- /rank Command ----------------- #
@app.on_message(filters.command("rank"))
async def rank(client, message):
    cursor = user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "characters": 1})
    leaderboard = await cursor.to_list(length=None)
    leaderboard.sort(key=lambda x: len(x.get('characters', [])), reverse=True)
    leaderboard = leaderboard[:10]

    caption = build_user_leaderboard(leaderboard)
    buttons = get_buttons("top")

    await message.reply_photo(
        photo=random.choice(PHOTO_URL),
        caption=caption,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=buttons
    )


# ----------------- Callback Query Handlers ----------------- #
async def edit_leaderboard(callback_query, caption, active_tab):
    try:
        await callback_query.edit_message_caption(
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=get_buttons(active_tab)
        )
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback_query.answer("Already showing this!", show_alert=False)
        else:
            await callback_query.answer(f"⚠️ {str(e)[:100]}", show_alert=True)


@app.on_callback_query(filters.regex("^top$"))
async def top_callback(client, callback_query):
    await callback_query.answer("⏳ Loading leaderboard...", show_alert=False)
    await asyncio.sleep(0.2)

    cursor = user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "characters": 1})
    leaderboard = await cursor.to_list(length=None)
    leaderboard.sort(key=lambda x: len(x.get('characters', [])), reverse=True)
    leaderboard = leaderboard[:10]

    caption = build_user_leaderboard(leaderboard)
    await edit_leaderboard(callback_query, caption, "top")


@app.on_callback_query(filters.regex("^top_group$"))
async def top_group_callback(client, callback_query):
    await callback_query.answer("⏳ Loading top groups...", show_alert=False)
    await asyncio.sleep(0.2)

    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    leaderboard = await cursor.to_list(length=10)

    caption = build_group_leaderboard(leaderboard)
    await edit_leaderboard(callback_query, caption, "top_group")


@app.on_callback_query(filters.regex("^mtop$"))
async def mtop_callback(client, callback_query):
    await callback_query.answer("⏳ Loading coin leaderboard...", show_alert=False)
    await asyncio.sleep(0.2)

    cursor = user_collection.find({}, {"_id": 0, "id": 1, "first_name": 1, "coins": 1})
    leaderboard = await cursor.to_list(length=None)
    leaderboard.sort(key=lambda x: x.get('coins', 0), reverse=True)
    leaderboard = leaderboard[:10]

    caption = build_coin_leaderboard(leaderboard)
    await edit_leaderboard(callback_query, caption, "mtop")