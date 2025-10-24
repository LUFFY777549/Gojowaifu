import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery
)
from TEAMZYRO import ZYRO as bot, user_collection

# ----------------- BONUS AMOUNTS -----------------
DAILY_COINS = 100
WEEKLY_COINS = 1500


# ----------------- MAIN BONUS MENU -----------------
@bot.on_message(filters.command("bonus"))
async def bonus_menu(_, message: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎁 Daily Claim", callback_data="daily_claim")],
            [InlineKeyboardButton("📅 Weekly Claim", callback_data="weekly_claim")],
            [InlineKeyboardButton("❌ Close", callback_data="close_bonus")]
        ]
    )
    await message.reply_text(
        "✨ ʙᴏɴᴜꜱ ᴍᴇɴᴜ ✨\n\nChoose one of the options below:",
        reply_markup=keyboard
    )


# ----------------- BONUS HANDLER -----------------
@bot.on_callback_query(filters.regex("^(daily_claim|weekly_claim|close_bonus)$"))
async def bonus_handler(_, query: CallbackQuery):
    user_id = query.from_user.id

    # Always answer callback first to prevent "button expired"
    await query.answer()

    user = await user_collection.find_one({"id": user_id})
    if not user:
        user = {
            "id": user_id,
            "balance": 0,
            "last_daily_claim": None,
            "last_weekly_claim": None,
        }
        await user_collection.insert_one(user)

    # Reusable keyboard
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎁 Daily Claim", callback_data="daily_claim")],
            [InlineKeyboardButton("📅 Weekly Claim", callback_data="weekly_claim")],
            [InlineKeyboardButton("❌ Close", callback_data="close_bonus")]
        ]
    )

    # ---------- DAILY CLAIM ----------
    if query.data == "daily_claim":
        last_daily = user.get("last_daily_claim")
        now = datetime.utcnow()

        if last_daily and (now - last_daily) < timedelta(days=1):
            remaining = timedelta(days=1) - (now - last_daily)
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            return await query.message.edit_text(
                f"⏳ You already claimed your daily bonus!\n\nNext bonus in **{hours}h {minutes}m {seconds}s**",
                reply_markup=keyboard
            )

        await user_collection.update_one(
            {"id": user_id},
            {
                "$inc": {"balance": DAILY_COINS},
                "$set": {"last_daily_claim": now}
            },
            upsert=True
        )

        updated = await user_collection.find_one({"id": user_id})
        balance = int(updated.get("balance", 0))

        return await query.message.edit_text(
            f"✅ You successfully claimed your **Daily Bonus!**\n\n💰 +{DAILY_COINS} coins added\n🔹 New Balance: {balance}",
            reply_markup=keyboard
        )

    # ---------- WEEKLY CLAIM ----------
    elif query.data == "weekly_claim":
        last_weekly = user.get("last_weekly_claim")
        now = datetime.utcnow()

        if last_weekly and (now - last_weekly) < timedelta(weeks=1):
            remaining = timedelta(weeks=1) - (now - last_weekly)
            days, remainder = divmod(int(remaining.total_seconds()), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            return await query.message.edit_text(
                f"⏳ You already claimed your weekly bonus!\n\nNext bonus in **{days}d {hours}h {minutes}m {seconds}s**",
                reply_markup=keyboard
            )

        await user_collection.update_one(
            {"id": user_id},
            {
                "$inc": {"balance": WEEKLY_COINS},
                "$set": {"last_weekly_claim": now}
            },
            upsert=True
        )

        updated = await user_collection.find_one({"id": user_id})
        balance = int(updated.get("balance", 0))

        return await query.message.edit_text(
            f"✅ You successfully claimed your **Weekly Bonus!**\n\n💰 +{WEEKLY_COINS} coins added\n🔹 New Balance: {balance}",
            reply_markup=keyboard
        )

    # ---------- CLOSE MENU ----------
    elif query.data == "close_bonus":
        try:
            await query.message.delete()
            await query.answer("❌ Closed menu")
        except:
            await query.answer("❌ Already closed")


print("✅ Bonus command loaded successfully.")