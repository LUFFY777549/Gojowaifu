from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from TEAMZYRO import group_user_totals_collection, OWNER_ID, app

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    """
    Check if the user is an admin or owner of the chat.
    Returns True if the user is an admin or owner, False otherwise.
    """
    if user_id == OWNER_ID:
        return True

    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        print(f"[is_admin Error] {e}")
        return False

@app.on_message(filters.command("ctime") & filters.group)
async def set_ctime(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if user is admin or owner
    is_admin_user = await is_admin(client, chat_id, user_id)

    if not is_admin_user:
        await message.reply_text("⚠️ Only group admins or the bot owner can use this command!")
        return

    # Parse command argument
    try:
        ctime = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply_text("⚠️ Please provide a number (e.g., /ctime 80).")
        return

    # Validate ctime based on permissions
    if user_id == OWNER_ID:
        if not 1 <= ctime <= 200:
            await message.reply_text("⚠️ Bot owner can set ctime between 1 and 200.")
            return
    else:
        if not 80 <= ctime <= 200:
            await message.reply_text("⚠️ Admins can set ctime between 80 and 200.")
            return

    # Update ctime in MongoDB
    try:
        await group_user_totals_collection.update_one(
            {"group_id": str(chat_id)},
            {"$set": {"ctime": ctime}},
            upsert=True
        )
        await message.reply_text(f"✅ Message count threshold set to {ctime} for this group.")
    except Exception as e:
        await message.reply_text(f"⚠️ Failed to update ctime: {e}")
        print(f"[MongoDB Error] {e}")