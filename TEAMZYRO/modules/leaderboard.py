import os
import random
import html
from pyrogram import Client, filters
from pyrogram.types import Message

from TEAMZYRO import (
    app,
    PHOTO_URL,
    OWNER_ID,
    user_collection,
    top_global_groups_collection,
    group_user_totals_collection,
    sudo_users as SUDO_USERS
)

# --------------------- GLOBAL LEADERBOARD ---------------------
@app.on_message(filters.command("TopGroups"))
async def global_leaderboard(client: Client, message: Message):
    # Fetch top 10 groups by guess count
    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    if not leaderboard_data:
        return await message.reply_text("⚠ No groups found in leaderboard!")

    leaderboard_message = "<b>🌟 Top 10 Groups Who Guessed Most Characters</b>\n\n"

    for i, group in enumerate(leaderboard_data, start=1):
        group_name = html.escape(group.get('group_name', 'Unknown'))
        if len(group_name) > 15:
            group_name = group_name[:15] + '...'
        count = group.get('count', 0)
        leaderboard_message += f"{i}. <b>{group_name}</b> ➾ <b>{count}</b>\n"

    photo_url = random.choice(PHOTO_URL)
    await message.reply_photo(photo=photo_url, caption=leaderboard_message, parse_mode='html')


# --------------------- GROUP TOP USERS ---------------------
@app.on_message(filters.command("ctop"))
async def ctop(client: Client, message: Message):
    chat_id = message.chat.id

    cursor = group_user_totals_collection.aggregate([
        {"$match": {"group_id": chat_id}},
        {"$project": {
            "username": 1,
            "first_name": 1,
            "character_count": "$count"
        }},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    if not leaderboard_data:
        return await message.reply_text("⚠ No users found in this group!")

    leaderboard_message = "<b>🌟 Top 10 Users Who Guessed Most Characters in This Group</b>\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username')
        first_name = html.escape(user.get('first_name', 'Unknown'))
        if len(first_name) > 15:
            first_name = first_name[:15] + '...'
        character_count = user.get('character_count', 0)

        if username:
            leaderboard_message += f'{i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'
        else:
            leaderboard_message += f'{i}. <b>{first_name}</b> ➾ <b>{character_count}</b>\n'

    photo_url = random.choice(PHOTO_URL)
    await message.reply_photo(photo=photo_url, caption=leaderboard_message, parse_mode='html')


# --------------------- STATS ---------------------
@app.on_message(filters.command("st"))
async def stats(client: Client, message: Message):
    user_count = await user_collection.count_documents({})
    group_ids = await group_user_totals_collection.distinct('group_id')
    group_count = len(group_ids)

    await message.reply_text(
        f"📊 <b>Bot Statistics:</b>\n\n"
        f"👤 Total Users: {user_count}\n"
        f"👥 Total Groups: {group_count}",
        parse_mode="html"
    )


# --------------------- SEND USERS DOCUMENT ---------------------
@app.on_message(filters.command("list"))
async def send_users_document(client: Client, message: Message):
    if message.from_user.id not in SUDO_USERS:
        return await message.reply_text("❌ Only Sudo users can use this command!")

    cursor = user_collection.find({})
    users = [doc async for doc in cursor]

    if not users:
        return await message.reply_text("⚠ No users found!")

    user_list_text = "\n".join([html.escape(user.get("first_name", "Unknown")) for user in users])

    file_path = "users.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(user_list_text)

    with open(file_path, "rb") as f:
        await message.reply_document(document=f, caption="📄 List of all users.")

    os.remove(file_path)


# --------------------- SEND GROUPS DOCUMENT ---------------------
@app.on_message(filters.command("groups"))
async def send_groups_document(client: Client, message: Message):
    if message.from_user.id not in SUDO_USERS:
        return await message.reply_text("❌ Only Sudo users can use this command!")

    cursor = top_global_groups_collection.find({})
    groups = [doc async for doc in cursor]

    if not groups:
        return await message.reply_text("⚠ No groups found!")

    group_list_text = "\n".join([html.escape(group.get("group_name", "Unknown")) for group in groups])

    file_path = "groups.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(group_list_text)

    with open(file_path, "rb") as f:
        await message.reply_document(document=f, caption="📄 List of all groups.")

    os.remove(file_path)