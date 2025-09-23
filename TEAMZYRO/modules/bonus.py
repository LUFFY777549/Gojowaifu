import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters, types as t
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from TEAMZYRO import ZYRO as bot, user_collection
import uuid

# Bonus amounts
DAILY_COINS = 100
WEEKLY_COINS = 1500

# /bonus command
@bot.on_message(filters.command("bonus"))
async def bonus_menu(_, message: t.Message):
    uid = str(uuid.uuid4())  # unique session ID for buttons
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🎁 Daily Claim", callback_data=f"bonus:{uid}:daily")],
            [InlineKeyboardButton("📅 Weekly Claim", callback_data=f"bonus:{uid}:weekly")],
            [InlineKeyboardButton("❌ Close", callback_data=f"bonus:{uid}:close")]
        ]
    )
    await message.reply_text("✨ ʙᴏɴᴜꜱ ᴍᴇɴᴜ ✨\n\nChoose one of the options below:", reply_markup=keyboard)


# Callback only for bonus buttons
@bot.on_callback_query(filters.regex("^(daily_claim|weekly_claim|close_bonus)$"))
async def bonus_handler(_, query: t.CallbackQuery):
    user_id = query.from_user.id
    user = await user_collection.find_one({"id": user_id})

    if not user:
        user = {
            "id": user_id,
            "balance": 0,
            "last_daily_claim": None,
            "last_weekly_claim": None,
        }
        await user_collection.insert_one(user)

    # DAILY
    if query.data == "daily_claim":
        last_daily = user.get("last_daily_claim")
        if last_daily and (datetime.utcnow() - last_daily) < timedelta(days=1):
            remaining = timedelta(days=1) - (datetime.utcnow() - last_daily)
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            return await query.answer(
                f"⏳ Already claimed! Next in {hours}h {minutes}m {seconds}s",
                show_alert=True
            )

        await user_collection.update_one(
            {"id": user_id},
            {"$inc": {"balance": DAILY_COINS}, "$set": {"last_daily_claim": datetime.utcnow()}},
            upsert=True
        )
        updated = await user_collection.find_one({"id": user_id})
        balance = int(updated.get("balance", 0))

        return await query.answer(
            f"✅ Daily Bonus claimed!\n💰 +{DAILY_COINS} coins\n\n🔹 Balance: {balance}",
            show_alert=True
        )

    # WEEKLY
    elif query.data == "weekly_claim":
        last_weekly = user.get("last_weekly_claim")
        if last_weekly and (datetime.utcnow() - last_weekly) < timedelta(weeks=1):
            remaining = timedelta(weeks=1) - (datetime.utcnow() - last_weekly)
            days, remainder = divmod(int(remaining.total_seconds()), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            return await query.answer(
                f"⏳ Already claimed! Next in {days}d {hours}h {minutes}m",
                show_alert=True
            )

        await user_collection.update_one(
            {"id": user_id},
            {"$inc": {"balance": WEEKLY_COINS}, "$set": {"last_weekly_claim": datetime.utcnow()}},
            upsert=True
        )
        updated = await user_collection.find_one({"id": user_id})
        balance = int(updated.get("balance", 0))

        return await query.answer(
            f"✅ Weekly Bonus claimed!\n💰 +{WEEKLY_COINS} coins\n\n🔹 Balance: {balance}",
            show_alert=True
        )

    # CLOSE
    elif query.data == "close_bonus":
        try:
            await query.message.delete()
        except:
            pass
        return await query.answer("❌ Closed", show_alert=False)
        
