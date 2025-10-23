from TEAMZYRO import *
import random
import asyncio
import time
from telegram import Update
from telegram.ext import CallbackContext

log = "-1002946070634"

rarity_map = {
    1: "⚪️ Low",
    2: "🟠 Medium",
    3: "🔴 High",
    4: "🎩 Special Edition",
    5: "🪽 Elite Edition",
    6: "🪐 Exclusive",
    7: "💞 Valentine",
    8: "🎃 Halloween",
    9: "❄️ Winter",
    10: "🏖 Summer",
    11: "🎗 Royal",
    12: "💸 Luxury Edition",
    13: "🍃 echhi",
    14: "🌧️ Rainy Edition",
    15: "🎍 Festival"
}

RARITY_WEIGHTS = {
    "⚪️ Low": (40, True),
    "🟠 Medium": (20, True),
    "🔴 High": (12, True),
    "🎩 Special Edition": (8, True),
    "🪽 Elite Edition": (6, True),
    "🪐 Exclusive": (4, True),
    "💞 Valentine": (2, True),
    "🎃 Halloween": (2, True),
    "❄️ Winter": (2, True),
    "🏖 Summer": (2, True),
    "🎗 Royal": (2, True),
    "💸 Luxury Edition": (2, True)
}

async def delete_message(chat_id, message_id, context):
    await asyncio.sleep(300)  # 5 minutes
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    # Fetch all characters
    all_characters = list(await collection.find({}).to_list(length=None))

    if not all_characters:
        await context.bot.send_message(chat_id, "No characters found in the database.")
        return

    # Map rarity properly
    for char in all_characters:
        # priority to integer stored rarity_number from upload.py
        rid = char.get("rarity_number")  
        if rid and isinstance(rid, int) and rid in rarity_map:
            char["rarity_str"] = rarity_map[rid]
        elif isinstance(char.get("rarity"), str):
            char["rarity_str"] = char["rarity"]
        else:
            char["rarity_str"] = "Unknown"

    # Filter allowed rarities
    allowed_rarities = [k for k, v in RARITY_WEIGHTS.items() if v[1]]
    available_characters = [c for c in all_characters if c["rarity_str"] in allowed_rarities]

    if not available_characters:
        await context.bot.send_message(chat_id, "No characters with allowed rarities found.")
        return

    # Weighted random selection
    cumulative_weights = []
    cumulative_weight = 0
    for character in available_characters:
        cumulative_weight += RARITY_WEIGHTS.get(character["rarity_str"], (1, False))[0]
        cumulative_weights.append(cumulative_weight)

    rand = random.uniform(0, cumulative_weight)
    selected_character = None
    for i, character in enumerate(available_characters):
        if rand <= cumulative_weights[i]:
            selected_character = character
            break

    if not selected_character:
        selected_character = random.choice(available_characters)

    # Store last character
    last_characters[chat_id] = selected_character
    last_characters[chat_id]["timestamp"] = time.time()

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    # Send video or photo
    if "vid_url" in selected_character and selected_character["vid_url"]:
        sent_message = await context.bot.send_video(
            chat_id=chat_id,
            video=selected_character["vid_url"],
            caption=f"""✨ A {selected_character['rarity_str']} Character Appears! ✨
🔍 Use /guess to claim this mysterious character!
💫 Hurry, before someone else snatches them!""",
            parse_mode="Markdown"
        )
    else:
        sent_message = await context.bot.send_photo(
            chat_id=chat_id,
            photo=selected_character["img_url"],
            caption=f"""✨ A {selected_character['rarity_str']} Character Appears! ✨
🔍 Use /guess to claim this mysterious character!
💫 Hurry, before someone else snatches them!""",
            parse_mode="Markdown"
        )

    # Delete message after 5 mins
    asyncio.create_task(delete_message(chat_id, sent_message.message_id, context))