from TEAMZYRO import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import html, random
import uuid

# ---------------- BALANCE HELPER ---------------- #
async def get_balance(user_id):
    user_data = await user_collection.find_one({'id': user_id}, {'balance': 1})
    if user_data:
        return user_data.get('balance', 0)
    return 0

# ---------------- BALANCE IMAGES ---------------- #
BALANCE_IMAGES = [
    "https://files.catbox.moe/3saw6n.jpg",
    "https://files.catbox.moe/3ilay5.jpg",
    "https://files.catbox.moe/i28al7.jpg",
    "https://files.catbox.moe/k7t6y7.jpg",
    "https://files.catbox.moe/h0ftuw.jpg",
    "https://files.catbox.moe/syanmk.jpg",
    "https://files.catbox.moe/shslw1.jpg",
    "https://files.catbox.moe/xokoit.jpg",
    "https://files.catbox.moe/6w5fl4.jpg"
]

# ---------------- BALANCE COMMAND ---------------- #
@app.on_message(filters.command("balance"))
async def balance(client: Client, message: Message):
    user_id = message.from_user.id
    user_balance = await get_balance(user_id)

    caption = (
        f"👤 {html.escape(message.from_user.first_name)}\n"
        f"💰 Balance: ||{user_balance} coins||"
    )

    photo_url = random.choice(BALANCE_IMAGES)

    await message.reply_photo(
        photo=photo_url,
        caption=caption,
        has_spoiler=True   # photo bhi spoiler me hoga
    )

# ---------------- PAY COMMAND ---------------- #
@app.on_message(filters.command("pay"))
async def pay(client, message):
    sender_id = message.from_user.id
    args = message.command

    if len(args) < 3:
        return await message.reply_text("Usage: /pay <amount> <@username/user_id>")

    try:
        amount = int(args[1])
    except:
        return await message.reply_text("❌ Invalid amount")

    # Recipient ID (simplified for demo)
    recipient_id = int(args[2]) if args[2].isdigit() else None
    if not recipient_id:
        return await message.reply_text("❌ Recipient not found")

    # Make txn ID
    txn_id = str(uuid.uuid4())

    # Save txn in DB
    await txn_collection.insert_one({
        "txn_id": txn_id,
        "sender": sender_id,
        "recipient": recipient_id,
        "amount": amount,
        "status": "pending"
    })

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"pay:{txn_id}:confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"pay:{txn_id}:cancel")
        ]
    ])

    await message.reply_text(
        f"⚠️ Confirm {amount} coins payment?",
        reply_markup=buttons
    )


# Callback handler
@app.on_callback_query(filters.regex(r"^pay:"))
async def pay_callback(client, cq):
    try:
        _, txn_id, action = cq.data.split(":")

        txn = await txn_collection.find_one({"txn_id": txn_id})
        if not txn or txn["status"] != "pending":
            return await cq.answer("❌ Transaction expired!", show_alert=True)

        if cq.from_user.id != txn["sender"]:
            return await cq.answer("⚠️ Not your transaction!", show_alert=True)

        if action == "cancel":
            await txn_collection.update_one({"txn_id": txn_id}, {"$set": {"status": "cancelled"}})
            await cq.message.edit_text("❌ Payment cancelled.")
            return await cq.answer("Cancelled ✅")

        if action == "confirm":
            # Balance check & update
            if await get_balance(txn["sender"]) < txn["amount"]:
                return await cq.answer("❌ Insufficient balance!", show_alert=True)

            await user_collection.update_one({"id": txn["sender"]}, {"$inc": {"balance": -txn["amount"]}})
            await user_collection.update_one({"id": txn["recipient"]}, {"$inc": {"balance": txn["amount"]}}, upsert=True)
            await txn_collection.update_one({"txn_id": txn_id}, {"$set": {"status": "done"}})

            await cq.message.edit_text(
                f"✅ Paid {txn['amount']} coins to {txn['recipient']}!"
            )
            return await cq.answer("✅ Payment successful!")

    except Exception as e:
        print("CALLBACK ERROR:", e)
        return await cq.answer("⚠️ Error!", show_alert=True)
