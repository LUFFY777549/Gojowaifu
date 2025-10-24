from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from TEAMZYRO import user_collection  # ← direct import from TEAMZYRO/__init__.py

DAILY_REWARD = 100
WEEKLY_REWARD = 500


# -------------------------- COOLDOWN CHECKER -------------------------- #
async def can_claim_bonus(user_id: int, bonus_type: str, cooldown_hours: int):
    """Check if user can claim bonus (based on cooldown)."""
    user = await user_collection.find_one({'id': user_id})
    now = datetime.utcnow()

    if not user:
        return True

    last_claim = user.get(f'last_{bonus_type}_bonus')
    if not last_claim:
        return True

    diff = now - last_claim
    return diff.total_seconds() >= cooldown_hours * 3600


# -------------------------- UPDATE BONUS TIME ------------------------- #
async def update_bonus_time(user_id: int, bonus_type: str):
    """Update user's last claim time."""
    now = datetime.utcnow()
    await user_collection.update_one(
        {'id': user_id},
        {'$set': {f'last_{bonus_type}_bonus': now}},
        upsert=True
    )


# -------------------------- UPDATE BALANCE ---------------------------- #
async def add_balance(user_id: int, amount: int):
    """Increase user balance."""
    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': amount}},
        upsert=True
    )


# -------------------------- BONUS COMMAND ----------------------------- #
@Client.on_message(filters.command("bonus"))
async def bonus_handler(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌻 Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton("📅 Weekly Bonus", callback_data="weekly_bonus")],
        [InlineKeyboardButton("❌ Close", callback_data="bonus_close")]
    ])
    await message.reply("🎁 Choose your bonus:", reply_markup=keyboard)


# -------------------------- CALLBACK HANDLER -------------------------- #
@Client.on_callback_query(filters.regex("^(daily_bonus|weekly_bonus|bonus_close)$"))
async def bonus_callback(client, callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    if data == "bonus_close":
        await callback.message.delete()
        return

    # Define reward and cooldown
    if data == "daily_bonus":
        bonus_type = "daily"
        reward = DAILY_REWARD
        cooldown = 24
    elif data == "weekly_bonus":
        bonus_type = "weekly"
        reward = WEEKLY_REWARD
        cooldown = 168

    # Check eligibility
    if await can_claim_bonus(user_id, bonus_type, cooldown):
        await update_bonus_time(user_id, bonus_type)
        await add_balance(user_id, reward)
        await callback.answer(
            f"✅ You received {reward} waifu coins!",
            show_alert=True
        )
    else:
        await callback.answer(
            "⛔ Already claimed! Try later.",
            show_alert=True
        )