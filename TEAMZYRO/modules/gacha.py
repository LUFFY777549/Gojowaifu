import random
from pyrogram import filters
from TEAMZYRO import app, user_collection, waifu_collection

# ----------------------------- CONFIG -----------------------------
GACHA_COST = 1000  # Minimum coins per summon

# Rarity chances (in %)
RARITY_CHANCES = {
    "Common": 60,
    "Rare": 25,
    "Epic": 10,
    "Legendary": 5,
}

RARITY_EMOJIS = {
    "Common": "⚪",
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟡",
}

# ---------------------------- HELPERS -----------------------------
def get_random_rarity():
    """Return a rarity based on chances."""
    rand = random.randint(1, 100)
    total = 0
    for rarity, chance in RARITY_CHANCES.items():
        total += chance
        if rand <= total:
            return rarity
    return "Common"

# --------------------------- COMMAND ------------------------------
@app.on_message(filters.command("gacha"))
async def gacha_summon(client, message):
    user_id = message.from_user.id
    args = message.text.split()

    # ------------------ USAGE CHECK ------------------
    if len(args) < 2 or not args[1].isdigit():
        return await message.reply_text(
            "❌ Usage: `/gacha <amount>`\nExample: `/gacha 1000`", quote=True
        )

    amount = int(args[1])
    if amount < GACHA_COST:
        return await message.reply_text(
            f"❌ Minimum {GACHA_COST} coins required per summon!", quote=True
        )

    # ------------------ FETCH USER ------------------
    user = await user_collection.find_one({"id": user_id})
    if not user:
        # Create user if not exists
        user = {"id": user_id, "balance": 1000, "waifus": []}
        await user_collection.insert_one(user)

    balance = user.get("balance", 0)
    if balance < amount:
        return await message.reply_text(
            "❌ You don't have enough balance!", quote=True
        )

    # ------------------ DEDUCT BALANCE ------------------
    await user_collection.update_one({"id": user_id}, {"$inc": {"balance": -amount}})

    # ------------------ RANDOM WAIFU ------------------
    rarity = get_random_rarity()

    waifu_list = await waifu_collection.aggregate([
        {"$match": {"rarity": rarity}},
        {"$sample": {"size": 1}}
    ]).to_list(length=1)

    if not waifu_list:
        return await message.reply_text(
            "⚠ No waifus available for this rarity. Admin must add some!", quote=True
        )

    waifu = waifu_list[0]

    # ------------------ SAVE TO USER INVENTORY ------------------
    if "waifus" not in user:
        user["waifus"] = []

    await user_collection.update_one(
        {"id": user_id},
        {"$push": {"waifus": waifu}}
    )

    # ------------------ SEND RESULT ------------------
    await message.reply_photo(
        waifu["image_url"],
        caption=(
            f"✨ **You summoned a waifu!**\n\n"
            f"👩 **Name:** {waifu['name']}\n"
            f"🎬 **Anime:** {waifu['anime']}\n"
            f"{RARITY_EMOJIS.get(rarity, '⚪')} **Rarity:** {rarity}\n"
            f"💰 **Cost:** {amount} coins"
        ),
        has_spoiler=True
    )