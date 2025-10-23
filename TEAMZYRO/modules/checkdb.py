from pyrogram import filters
from TEAMZYRO import app
from pymongo import MongoClient
from pyrogram.types import Message

MONGO_URL = "mongodb+srv://sufyan532011:5042@auctionbot.5ms20.mongodb.net/?retryWrites=true&w=majority&appName=AuctionBot"
mongo = MongoClient(MONGO_URL)
db = mongo["waifu_bot"]
users = db["users"]

@app.on_message(filters.command("checkdb"))
async def check_db(client, message: Message):
    user_id = message.from_user.id
    data = users.find_one({"_id": user_id}) or users.find_one({"user_id": user_id}) or users.find_one({"id": user_id})

    if data:
        await message.reply(f"📦 Found your data:\n```{data}```", quote=True)
    else:
        await message.reply("❌ No data found in DB!", quote=True)
