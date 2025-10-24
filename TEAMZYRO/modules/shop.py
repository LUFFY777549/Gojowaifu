from pyrogram import filters
from pyrogram.types import Message
from TEAMZYRO import ZYRO as bot, user_collection


@bot.on_message(filters.command("pay"))
async def pay_coins(_, message: Message):
    sender = message.from_user
    args = message.text.split()

    # Case 1: Reply with /pay <amount>
    if message.reply_to_message and len(args) == 2:
        receiver = message.reply_to_message.from_user
        try:
            amount = int(args[1])
        except ValueError:
            return await message.reply_text("❌ Invalid amount. Example: `/pay 100`", quote=True)

    # Case 2: /pay @username <amount>
    elif len(args) == 3:
        receiver_username = args[1]
        try:
            amount = int(args[2])
        except ValueError:
            return await message.reply_text("❌ Invalid amount. Example: `/pay @username 100`", quote=True)

        # Fetch receiver from database
        receiver = await bot.get_users(receiver_username)
    else:
        return await message.reply_text(
            "❌ Usage:\n"
            "`/pay @username <amount>`\n"
            "or reply to a user with `/pay <amount>`",
            quote=True
        )

    # Self check
    if receiver.id == sender.id:
        return await message.reply_text("❌ You can’t pay yourself!", quote=True)

    # Fetch sender and receiver from DB
    sender_data = await user_collection.find_one({"id": sender.id})
    receiver_data = await user_collection.find_one({"id": receiver.id})

    if not sender_data:
        sender_data = {"id": sender.id, "balance": 0}
        await user_collection.insert_one(sender_data)

    if not receiver_data:
        receiver_data = {"id": receiver.id, "balance": 0}
        await user_collection.insert_one(receiver_data)

    sender_balance = int(sender_data.get("balance", 0))

    if sender_balance < amount:
        return await message.reply_text("❌ Not enough balance to complete this payment.", quote=True)

    # Transfer coins
    await user_collection.update_one({"id": sender.id}, {"$inc": {"balance": -amount}})
    await user_collection.update_one({"id": receiver.id}, {"$inc": {"balance": amount}})

    # Fetch updated balances
    new_sender = await user_collection.find_one({"id": sender.id})
    new_receiver = await user_collection.find_one({"id": receiver.id})

    sender_balance = new_sender.get("balance", 0)
    receiver_balance = new_receiver.get("balance", 0)

    # Notify sender
    await message.reply_text(
        f"✅ You sent **{amount}** coins to "
        f"<a href='tg://user?id={receiver.id}'>{receiver.first_name}</a> 💸\n"
        f"💰 Your new balance: **{sender_balance}**",
        quote=True,
        disable_web_page_preview=True
    )

    # Try to notify receiver
    try:
        await bot.send_message(
            receiver.id,
            f"💰 You received **{amount}** coins from "
            f"<a href='tg://user?id={sender.id}'>{sender.first_name}</a> 💎\n"
            f"💳 Your new balance: **{receiver_balance}**",
            disable_web_page_preview=True
        )
    except:
        pass  # Ignore if receiver has no chat started with bot


print("✅ /pay command loaded successfully!")
