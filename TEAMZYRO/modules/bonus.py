import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from TEAMZYRO import ZYRO as bot, user_collection

DAILY_COINS = 100
WEEKLY_COINS = 1500


# ---------------- HELPER: BUTTON BUILDER ---------------- #
async def build_bonus_keyboard(user_id: int):
    user = await user_collection.find_one({"id": user_id})
    now = datetime.utcnow()
    daily_status = "AVAILABLE"
    weekly_status = "AVAILABLE"

    if user:
        last_daily = user.get("last_daily_claim")
        last_weekly = user.get("last_weekly_claim")

        if last_daily and (now - last_daily) < timedelta(days=1):
            daily_status = "CLAIMED"
        if last_weekly and (now - last_weekly) < timedelta(weeks=1):
            weekly_status = "CLAIMED"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🎁 Daily ({daily_status})", callback_data="daily_claim")],
        [InlineKeyboardButton(f"📅 Weekly ({weekly_status})", callback_data="weekly_claim")],
        [InlineKeyboardButton("❌ Close", callback_data="close_bonus")]
    ])


# ---------------- COMMAND: /bonus ---------------- #
@bot.on_message(filters.command("bonus"))
async def bonus_menu(_, message: Message):
    user_id = message.from_user.id
    user = await user_collection.find_one({"id": user_id})

    now = datetime.utcnow()
    daily_info = "✅ Available now!"
    weekly_info = "✅ Available now!"

    if user:
        last_daily = user.get("last_daily_claim")
        last_weekly = user.get("last_weekly_claim")

        if last_daily and (now - last_daily) < timedelta(days=1):
            remaining = timedelta(days=1) - (now - last_daily)
            h, rem = divmod(int(remaining.total_seconds()), 3600)
            m, _ = divmod(rem, 60)
            daily_info = f"⏳ Next in {h}h {m}m"

        if last_weekly and (now - last_weekly) < timedelta(weeks=1):
            remaining = timedelta(weeks=1) - (now - last_weekly)
            d, rem = divmod(int(remaining.total_seconds()), 86400)
            h, _ = divmod(rem, 3600)
            weekly_info = f"⏳ Next in {d}d {h}h"

    keyboard = await build_bonus_keyboard(user_id)
    await message.reply_text(
        f"✨ **BONUS MENU** ✨\n\n"
        f"🎁 Daily Bonus: {daily_info}\n"
        f"📅 Weekly Bonus: {weekly_info}\n\n"
        f"Choose one of the options below 👇",
        reply_markup=keyboard
    )


# ---------------- CALLBACK HANDLER ---------------- #
@bot.on_callback_query(filters.regex("^(daily_claim|weekly_claim|close_bonus)$"))
async def bonus_handler(_, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data
    now = datetime.utcnow()

    await query.answer("Processing...", show_alert=False)

    # Get or create user
    user = await user_collection.find_one({"id": user_id})
    if not user:
        user = {"id": user_id, "balance": 0, "last_daily_claim": None, "last_weekly_claim": None}
        await user_collection.insert_one(user)

    # ---------------- DAILY CLAIM ---------------- #
    if data == "daily_claim":
        last_daily = user.get("last_daily_claim")
        if last_daily and (now - last_daily) < timedelta(days=1):
            await query.answer("You already claimed today!", show_alert=True)
        else:
            await user_collection.update_one(
                {"id": user_id},
                {"$inc": {"balance": DAILY_COINS}, "$set": {"last_daily_claim": now}},
                upsert=True
            )
            new_user = await user_collection.find_one({"id": user_id})
            balance = int(new_user.get("balance", 0))

            await query.message.reply_text(
                f"🎉 **Congratulations!**\nYou claimed your **Daily Bonus!**\n\n"
                f"💰 +{DAILY_COINS} Coins\n💎 Total Balance: {balance}"
            )

        # Update buttons (CLAIMED)
        new_keyboard = await build_bonus_keyboard(user_id)
        await query.message.edit_reply_markup(reply_markup=new_keyboard)
        return

    # ---------------- WEEKLY CLAIM ---------------- #
    if data == "weekly_claim":
        last_weekly = user.get("last_weekly_claim")
        if last_weekly and (now - last_weekly) < timedelta(weeks=1):
            await query.answer("You already claimed weekly bonus!", show_alert=True)
        else:
            await user_collection.update_one(
                {"id": user_id},
                {"$inc": {"balance": WEEKLY_COINS}, "$set": {"last_weekly_claim": now}},
                upsert=True
            )
            new_user = await user_collection.find_one({"id": user_id})
            balance = int(new_user.get("balance", 0))

            await query.message.reply_text(
                f"🎉 **Congratulations!**\nYou claimed your **Weekly Bonus!**\n\n"
                f"💰 +{WEEKLY_COINS} Coins\n💎 Total Balance: {balance}"
            )

        # Update buttons (CLAIMED)
        new_keyboard = await build_bonus_keyboard(user_id)
        await query.message.edit_reply_markup(reply_markup=new_keyboard)
        return

    # ---------------- CLOSE ---------------- #
    if data == "close_bonus":
        try:
            await query.message.delete()
            await query.answer("Closed", show_alert=False)
        except:
            await query.answer("Already closed", show_alert=False)
        return


print("✅ Bonus system with status buttons loaded successfully.")