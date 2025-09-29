from TEAMZYRO import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import html, random, uuid
from datetime import datetime, timedelta

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

# ---------------- PAY COMMAND (Improved) ---------------- #
@ app.on_message(filters.command("pay") & ~filters.edited)
async def pay_command(client: Client, message: Message):
    sender_id = message.from_user.id
    args = message.text.split()

    # 1) Reply-to-user case: `/pay <amount>` as reply
    recipient_id = None
    amount = None

    if message.reply_to_message and len(args) >= 2:
        # /pay 100 (reply to user's message)
        try:
            amount = int(args[1])
        except:
            return await message.reply_text("❌ Usage: reply to a user and send `/pay <amount>`\nOr use `/pay <amount> @username`")
        recipient = message.reply_to_message.from_user
        recipient_id = recipient.id

    else:
        # Non-reply: try to parse /pay <amount> @username  OR /pay @username <amount>
        # Expect at least 3 tokens: ['/pay', x, y]
        if len(args) < 3:
            return await message.reply_text("❌ Usage:\n/pay <amount> @username\nor\n/pay @username <amount>\nor reply to a user's message with `/pay <amount>`")

        # Remove command token and examine the next two tokens
        token1 = args[1]
        token2 = args[2]

        # Determine which token is amount
        if token1.lstrip('-').isdigit():  # token1 is amount
            try:
                amount = int(token1)
            except:
                return await message.reply_text("❌ Invalid amount.")
            target = token2
        elif token2.lstrip('-').isdigit():  # token2 is amount
            try:
                amount = int(token2)
            except:
                return await message.reply_text("❌ Invalid amount.")
            target = token1
        else:
            return await message.reply_text("❌ Could not parse. Provide an amount and a username or reply to a user's message.")

        # Normalize username (allow both @username or numeric id)
        if target.startswith("@"):
            target = target[1:]

        # Try resolving user (username -> user object). If numeric id provided, use it.
        try:
            if target.isdigit():
                recipient_id = int(target)
            else:
                user_obj = await client.get_users(target)  # can accept username or user id string
                recipient_id = user_obj.id
        except Exception as e:
            return await message.reply_text(f"❌ Could not find user `{html.escape(target)}`. Make sure username is correct or try by replying to the user's message.", parse_mode="markdown")

    # Validate amount and recipient
    if amount is None or recipient_id is None:
        return await message.reply_text("❌ Error parsing command. Usage:\n/pay <amount> @username\nor reply to a user's message with `/pay <amount>`")

    if amount <= 0:
        return await message.reply_text("❌ Amount must be greater than 0.")

    if recipient_id == sender_id:
        return await message.reply_text("❌ You cannot pay yourself.")

    # Check sender balance
    sender_balance = await get_balance(sender_id)
    if sender_balance < amount:
        return await message.reply_text(f"❌ Insufficient balance. Your balance: {sender_balance} coins")

    # Create transaction
    txn_id = str(uuid.uuid4())
    created_at = datetime.utcnow()

    await txn_collection.insert_one({
        "txn_id": txn_id,
        "sender": sender_id,
        "recipient": recipient_id,
        "amount": amount,
        "status": "pending",
        "created_at": created_at
    })

    # Build confirmation buttons
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"pay:{txn_id}:confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"pay:{txn_id}:cancel")
            ]
        ]
    )

    # Show preview message (mention recipient)
    try:
        recipient_mention = f"<a href='tg://user?id={recipient_id}'>recipient</a>"
        await message.reply_text(
            f"⚠️ Confirm payment of <b>{amount}</b> coins to {recipient_mention}?\n\nTransaction ID: <code>{txn_id}</code>\n(Expires in 10 minutes)",
            reply_markup=keyboard,
            parse_mode="html"
        )
    except:
        # fallback plain text
        await message.reply_text(
            f"⚠️ Confirm payment of {amount} coins to user `{recipient_id}`?\n\nTransaction ID: `{txn_id}`\n(Expires in 10 minutes)",
            reply_markup=keyboard,
            parse_mode="markdown"
        )

# ---------------- PAY CALLBACK HANDLER ---------------- #
@ app.on_callback_query(filters.regex(r"^pay:"))
async def pay_callback(client: Client, cq):
    try:
        data = cq.data  # e.g. "pay:txn_uuid:confirm"
        parts = data.split(":")
        if len(parts) != 3:
            return await cq.answer("⚠️ Invalid callback.", show_alert=True)

        _, txn_id, action = parts

        txn = await txn_collection.find_one({"txn_id": txn_id})
        if not txn or txn.get("status") != "pending":
            return await cq.answer("❌ Transaction expired or already processed.", show_alert=True)

        # Expiry check (10 minutes)
        created_at = txn.get("created_at")
        if created_at and isinstance(created_at, datetime):
            if datetime.utcnow() - created_at > timedelta(minutes=10):
                await txn_collection.update_one({"txn_id": txn_id}, {"$set": {"status": "expired"}})
                try:
                    await cq.message.edit_text("❌ Transaction expired (timeout).")
                except:
                    pass
                return await cq.answer("❌ Transaction expired.", show_alert=True)

        # Only sender can confirm/cancel
        if cq.from_user.id != txn["sender"]:
            return await cq.answer("⚠️ Only the transaction initiator can confirm/cancel.", show_alert=True)

        if action == "cancel":
            await txn_collection.update_one({"txn_id": txn_id}, {"$set": {"status": "cancelled"}})
            try:
                await cq.message.edit_text("❌ Payment cancelled by sender.")
            except:
                pass
            return await cq.answer("Cancelled ✅")

        if action == "confirm":
            sender = txn["sender"]
            recipient = txn["recipient"]
            amount = int(txn["amount"])

            # Re-check balance atomically (best-effort)
            sender_balance = await get_balance(sender)
            if sender_balance < amount:
                await txn_collection.update_one({"txn_id": txn_id}, {"$set": {"status": "failed_insufficient"}})
                return await cq.answer("❌ Insufficient balance.", show_alert=True)

            # Perform balance transfer
            await user_collection.update_one({"id": sender}, {"$inc": {"balance": -amount}})
            await user_collection.update_one({"id": recipient}, {"$inc": {"balance": amount}}, upsert=True)
            await txn_collection.update_one({"txn_id": txn_id}, {"$set": {"status": "done", "completed_at": datetime.utcnow()}})

            # Edit message to success
            try:
                recipient_mention = f"<a href='tg://user?id={recipient}'>recipient</a>"
                await cq.message.edit_text(f"✅ Paid <b>{amount}</b> coins to {recipient_mention}!\nTransaction ID: <code>{txn_id}</code>", parse_mode="html")
            except:
                await cq.message.edit_text(f"✅ Paid {amount} coins to user `{recipient}`!\nTransaction ID: `{txn_id}`", parse_mode="markdown")
            return await cq.answer("✅ Payment successful!")

    except Exception as e:
        print("PAY CALLBACK ERROR:", e)
        try:
            return await cq.answer("⚠️ Something went wrong.", show_alert=True)
        except:
            return
