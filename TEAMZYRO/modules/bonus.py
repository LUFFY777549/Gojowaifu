import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters, types as t
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from TEAMZYRO import ZYRO as bot, user_collection

# Bonus amounts
DAILY_COINS = 100
WEEKLY_COINS = 1500


# /bonus command
@bot.on_message(filters.command("bonus"))
async def bonus_menu(_, message: t.Message):
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
            await query.answer("Already claimed ⏳", show_alert=True)
            return await query.message.edit_text(
                f"⏳ Daily already claimed!\n\nNext bonus in {hours}h {minutes}m {seconds}s"
            )

        await user_collection.update_one(
            {"id": user_id},
            {"$inc": {"balance": DAILY_COINS}, "$set": {"last_daily_claim": datetime.utcnow()}},
            upsert=True
        )
        updated = await user_collection.find_one({"id": user_id})
        balance = int(updated.get("balance", 0))

        await query.answer("✅ Claimed", show_alert=False)
        return await query.message.edit_text(
            f"✅ Daily Bonus claimed!\n\n💰 +{DAILY_COINS} coins\n🔹 Balance: {balance}"
        )

    # WEEKLY
    elif query.data == "weekly_claim":
        last_weekly = user.get("last_weekly_claim")
        if last_weekly and (datetime.utcnow() - last_weekly) < timedelta(weeks=1):
            remaining = timedelta(weeks=1) - (datetime.utcnow() - last_weekly)
            days, remainder = divmod(int(remaining.total_seconds()), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            await query.answer("Already claimed ⏳", show_alert=True)
            return await query.message.edit_text(
                f"⏳ Weekly already claimed!\n\nNext bonus in {days}d {hours}h {minutes}m"
            )

        await user_collection.update_one(
            {"id": user_id},
            {"$inc": {"balance": WEEKLY_COINS}, "$set": {"last_weekly_claim": datetime.utcnow()}},
            upsert=True
        )
        updated = await user_collection.find_one({"id": user_id})
        balance = int(updated.get("balance", 0))

        await query.answer("✅ Claimed", show_alert=False)
        return await query.message.edit_text(
            f"✅ Weekly Bonus claimed!\n\n💰 +{WEEKLY_COINS} coins\n🔹 Balance: {balance}"
        )

    # CLOSE
    elif query.data == "close_bonus":
        try:
            await query.message.delete()
            await query.answer("❌ Closed", show_alert=False)
        except:
            await query.answer("❌ Already closed", show_alert=False)
