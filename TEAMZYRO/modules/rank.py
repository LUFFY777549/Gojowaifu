from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random, asyncio, html
from TEAMZYRO import app, user_collection, top_global_groups_collection

PHOTO_URL = ["https://files.catbox.moe/9bhirj.jpg"]

# /rank command handler for users
@app.on_message(filters.command("rank") & ~filters.edited)
async def rank_users(_, message):
    user_stats = await user_collection.find().sort("characters", -1).limit(10).to_list(length=10)
    rank_text = "TOP 10 USERS WITH MOST CHARACTERS\n"
    for index, user in enumerate(user_stats, start=1):
        username = user.get("username", "Unknown")
        characters = user.get("characters", 0)
        rank_text += f"{index}. {username} => {characters}\n"
    
    await app.send_photo(
        chat_id=message.chat.id,
        photo=random.choice(PHOTO_URL),
        caption=rank_text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Top", callback_data="top_users")]]
        )
    )

# /rank command handler for groups
@app.on_message(filters.command("rank") & ~filters.edited)
async def rank_groups(_, message):
    group_stats = await top_global_groups_collection.find().sort("characters", -1).limit(10).to_list(length=10)
    rank_text = "TOP 10 GROUPS WHO GUSSED MOST CHARACTERS\n"
    for index, group in enumerate(group_stats, start=1):
        group_name = group.get("name", "Unknown")
        characters = group.get("characters", 0)
        rank_text += f"{index}. {group_name} => {characters}\n"
    
    await app.send_photo(
        chat_id=message.chat.id,
        photo=random.choice(PHOTO_URL),
        caption=rank_text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Top Group", callback_data="top_groups")]]
        )
    )

# /rank command handler for coins
@app.on_message(filters.command("rank") & ~filters.edited)
async def rank_coins(_, message):
    user_stats = await user_collection.find().sort("coins", -1).limit(10).to_list(length=10)
    rank_text = "TOP 10 USERS WITH MOST COINS\n"
    for index, user in enumerate(user_stats, start=1):
        username = user.get("username", "Unknown")
        coins = user.get("coins", 0)
        rank_text += f"{index}. {username} => {coins}\n"
    
    await app.send_photo(
        chat_id=message.chat.id,
        photo=random.choice(PHOTO_URL),
        caption=rank_text,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Top", callback_data="top_coins")]]
        )
    )