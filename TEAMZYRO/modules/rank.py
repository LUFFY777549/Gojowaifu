from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random, asyncio, html
from TEAMZYRO import app, user_collection, top_global_groups_collection

PHOTO_URL = ["https://files.catbox.moe/9bhirj.jpg"]

MAX_CAPTION_LENGTH = 1024

# /rank command handler
@app.on_message(filters.command("rank"))
async def rank(_, message):
    # Fetch data for users (characters)
    user_stats = await user_collection.find().sort("characters", -1).limit(10).to_list(length=10)
    rank_text = "TOP 10 USERS WITH MOST CHARACTERS\n"
    for index, user in enumerate(user_stats, start=1):
        username = user.get("username", "Unknown")
        characters = user.get("characters", 0)
        new_line = f"{index}. {username} => {characters}\n"
        if len(rank_text) + len(new_line) <= MAX_CAPTION_LENGTH:
            rank_text += new_line
        else:
            rank_text += "..."  # Indicate truncation
            break

    # Fetch data for groups
    group_stats = await top_global_groups_collection.find().sort("characters", -1).limit(10).to_list(length=10)
    rank_text_group = "TOP 10 GROUPS WHO GUSSED MOST CHARACTERS\n"
    for index, group in enumerate(group_stats, start=1):
        group_name = group.get("name", "Unknown")
        characters = group.get("characters", 0)
        new_line = f"{index}. {group_name} => {characters}\n"
        if len(rank_text_group) + len(new_line) <= MAX_CAPTION_LENGTH:
            rank_text_group += new_line
        else:
            rank_text_group += "..."  # Indicate truncation
            break

    # Fetch data for coins
    coin_stats = await user_collection.find().sort("coins", -1).limit(10).to_list(length=10)
    rank_text_coins = "TOP 10 USERS WITH MOST COINS\n"
    for index, user in enumerate(coin_stats, start=1):
        username = user.get("username", "Unknown")
        coins = user.get("coins", 0)
        new_line = f"{index}. {username} => {coins}\n"
        if len(rank_text_coins) + len(new_line) <= MAX_CAPTION_LENGTH:
            rank_text_coins += new_line
        else:
            rank_text_coins += "..."  # Indicate truncation
            break

    # Inline keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("TOP 🌸", callback_data="top_users")],
        [InlineKeyboardButton("TOP GROUP 🌸", callback_data="top_groups")],
        [InlineKeyboardButton("MTOP 🌸", callback_data="top_coins")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send initial message with user stats
    await app.send_photo(
        chat_id=message.chat.id,
        photo=random.choice(PHOTO_URL),
        caption=rank_text,
        reply_markup=reply_markup
    )

# Callback handler for button clicks
@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "top_users":
        user_stats = await user_collection.find().sort("characters", -1).limit(10).to_list(length=10)
        rank_text = "TOP 10 USERS WITH MOST CHARACTERS\n"
        for index, user in enumerate(user_stats, start=1):
            username = user.get("username", "Unknown")
            characters = user.get("characters", 0)
            new_line = f"{index}. {username} => {characters}\n"
            if len(rank_text) + len(new_line) <= MAX_CAPTION_LENGTH:
                rank_text += new_line
            else:
                rank_text += "..."  # Indicate truncation
                break
        await callback_query.message.edit_caption(caption=rank_text)
    
    elif data == "top_groups":
        group_stats = await top_global_groups_collection.find().sort("characters", -1).limit(10).to_list(length=10)
        rank_text = "TOP 10 GROUPS WHO GUSSED MOST CHARACTERS\n"
        for index, group in enumerate(group_stats, start=1):
            group_name = group.get("name", "Unknown")
            characters = group.get("characters", 0)
            new_line = f"{index}. {group_name} => {characters}\n"
            if len(rank_text) + len(new_line) <= MAX_CAPTION_LENGTH:
                rank_text += new_line
            else:
                rank_text += "..."  # Indicate truncation
                break
        await callback_query.message.edit_caption(caption=rank_text)
    
    elif data == "top_coins":
        coin_stats = await user_collection.find().sort("coins", -1).limit(10).to_list(length=10)
        rank_text = "TOP 10 USERS WITH MOST COINS\n"
        for index, user in enumerate(coin_stats, start=1):
            username = user.get("username", "Unknown")
            coins = user.get("coins", 0)
            new_line = f"{index}. {username} => {coins}\n"
            if len(rank_text) + len(new_line) <= MAX_CAPTION_LENGTH:
                rank_text += new_line
            else:
                rank_text += "..."  # Indicate truncation
                break
        await callback_query.message.edit_caption(caption=rank_text)
    
    await callback_query.answer()