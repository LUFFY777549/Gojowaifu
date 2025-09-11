import random
import math
import asyncio
import uuid
from datetime import datetime
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from TEAMZYRO import ZYRO as bot, user_collection

# ---------------- Helpers ---------------- #

def tiny(text: str) -> str:
    """Return styled text in uppercase (tiny-caps effect)."""
    try:
        return str(text).upper()
    except:
        return text

# ---------------- In-memory state ---------------- #
# single-player games keyed by user_id (int)
active_games = {}

# multiplayer pending challenges keyed by cid (str)
pending_challenges = {}

# active multiplayer games keyed by cid (str)
active_mgames = {}

# ---------------- Utility ---------------- #

def gen_mines(total_cells: int, mines_count: int):
    """Return a list of mine indices."""
    return random.sample(range(total_cells), mines_count)

def mines_count_by_size(size: int):
    """Default mines for given sizes (customizable)."""
    if size == 5:
        return 5
    if size == 9:
        return 15
    if size == 12:
        return 25
    # fallback
    return max(5, size)

# ---------------- Single-player persistence helpers ---------------- #

async def save_game(user_id: int, game: dict):
    """Save single-player to DB cache and in-memory."""
    await user_collection.update_one({"id": user_id}, {"$set": {"active_game": game}}, upsert=True)
    active_games[user_id] = game

async def load_game(user_id: int):
    """Load single-player from memory or DB."""
    if user_id in active_games:
        return active_games[user_id]
    user = await user_collection.find_one({"id": user_id})
    if user and "active_game" in user:
        active_games[user_id] = user["active_game"]
        return active_games[user_id]
    return None

async def delete_game(user_id: int):
    """Delete single-player game."""
    active_games.pop(user_id, None)
    await user_collection.update_one({"id": user_id}, {"$unset": {"active_game": ""}})

# ---------------- Single-player: /mines (5x5 board) ---------------- #

@bot.on_message(filters.command("mines"))
async def start_mines(client, message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 3:
        return await message.reply(tiny("USAGE: /MINES [COINS] [BOMBS]"))

    try:
        bet = int(args[1])
        bombs = int(args[2])
    except Exception:
        return await message.reply(tiny("⚠ INVALID NUMBERS"))

    if bombs < 2 or bombs > 20:
        return await message.reply(tiny("⚠ BOMBS MUST BE BETWEEN 2 AND 20"))

    user = await user_collection.find_one({"id": user_id})
    balance = user.get("balance", 0) if user else 0
    if balance < bet:
        return await message.reply(tiny("🚨 NOT ENOUGH COINS"))

    # Deduct bet
    await user_collection.update_one({"id": user_id}, {"$inc": {"balance": -bet}}, upsert=True)

    size = 5
    total = size * size
    mine_positions = gen_mines(total, bombs)
    game = {
        "mode": "single",
        "bet": bet,
        "bombs": bombs,
        "size": size,
        "mine_positions": mine_positions,
        "clicked": [],
        "multiplier": 1.0,
        "started_at": datetime.utcnow().isoformat()
    }

    await save_game(user_id, game)

    keyboard = [
        [InlineKeyboardButton("❓", callback_data=f"s:{i*size+j}") for j in range(size)]
        for i in range(size)
    ]
    keyboard.append([InlineKeyboardButton("💸 CASH OUT", callback_data="s:cash")])

    await message.reply(
        tiny(f"🎮 MINES GAME STARTED!\nBET: {bet}  BOMBS: {bombs}  MULTIPLIER: 1.00X"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@bot.on_callback_query(filters.regex(r"^s:\d+$"))
async def single_tile_press(client, cq):
    await cq.answer()
    user_id = cq.from_user.id
    try:
        pos = int(cq.data.split(":")[1])
    except Exception:
        return await cq.answer(tiny("⚠ INVALID BUTTON"), show_alert=True)

    game = await load_game(user_id)
    if not game or game.get("mode") != "single":
        return await cq.answer(tiny("⚠ NO ACTIVE GAME"), show_alert=True)

    if pos in game["clicked"]:
        return await cq.answer(tiny("ALREADY OPENED"), show_alert=True)

    game["clicked"].append(pos)

    # if mine
    if pos in game["mine_positions"]:
        await delete_game(user_id)
        size = game["size"]
        keyboard = []
        for i in range(size):
            row = []
            for j in range(size):
                idx = i*size + j
                if idx in game["mine_positions"]:
                    row.append(InlineKeyboardButton("💣", callback_data="s:ign"))
                elif idx in game["clicked"]:
                    row.append(InlineKeyboardButton("✅", callback_data="s:ign"))
                else:
                    row.append(InlineKeyboardButton("❎", callback_data="s:ign"))
            keyboard.append(row)

        return await cq.message.edit_text(
            tiny(f"💥 BOOM! MINE HIT.\nLOST: {game['bet']} COINS"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # safe
    game["multiplier"] = round(game["multiplier"] + 0.05, 2)
    potential_win = math.floor(game["bet"] * game["multiplier"])
    await save_game(user_id, game)

    # update view
    size = game["size"]
    keyboard = []
    for i in range(size):
        row = []
        for j in range(size):
            idx = i*size + j
            if idx in game["clicked"]:
                row.append(InlineKeyboardButton("✅", callback_data="s:ign"))
            else:
                row.append(InlineKeyboardButton("❓", callback_data=f"s:{idx}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("💸 CASH OUT", callback_data="s:cash")])

    await cq.message.edit_text(
        tiny(f"🎮 MINES GAME\nBET: {game['bet']}  BOMBS: {game['bombs']}  MULTIPLIER: {game['multiplier']:.2f}X  POTENTIAL: {potential_win}"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@bot.on_callback_query(filters.regex(r"^s:cash$"))
async def single_cashout(client, cq):
    await cq.answer()
    user_id = cq.from_user.id
    game = await load_game(user_id)
    if not game or game.get("mode") != "single":
        return await cq.answer(tiny("⚠ NO ACTIVE GAME"), show_alert=True)

    await delete_game(user_id)
    earned = math.floor(game["bet"] * game["multiplier"])
    await user_collection.update_one({"id": user_id}, {"$inc": {"balance": earned}}, upsert=True)
    user = await user_collection.find_one({"id": user_id})
    new_balance = user.get("balance", 0)

    size = game["size"]
    keyboard = []
    for i in range(size):
        row = []
        for j in range(size):
            idx = i*size + j
            if idx in game["mine_positions"]:
                row.append(InlineKeyboardButton("💣", callback_data="s:ign"))
            elif idx in game["clicked"]:
                row.append(InlineKeyboardButton("✅", callback_data="s:ign"))
            else:
                row.append(InlineKeyboardButton("❎", callback_data="s:ign"))
        keyboard.append(row)

    msg = await cq.message.edit_text(
        tiny(f"✅ CASHED OUT!\nWON: {earned} COINS\nMULTIPLIER: {game['multiplier']:.2f}X\nBALANCE: {new_balance}"),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await asyncio.sleep(5)
    try:
        await msg.delete()
    except:
        pass

@bot.on_callback_query(filters.regex(r"^s:ign$"))
async def single_ignore(client, cq):
    await cq.answer()
    # nothing

# ---------------- Multiplayer: /mgame challenge flow ----------------

@bot.on_message(filters.command("mgame"))
async def mgame_command(client, message):
    """
    Usage:
        /mgame [bet] [@username]
    Or: reply to a user's message with /mgame [bet]
    """
    challenger = message.from_user
    args = message.text.split()
    if len(args) < 2 and not message.reply_to_message:
        return await message.reply(tiny("USAGE: /MGAME [BET] [@USER OR REPLY]"))

    try:
        bet = int(args[1]) if len(args) >= 2 else None
    except Exception:
        return await message.reply(tiny("⚠ INVALID BET AMOUNT"))

    # resolve opponent
    opponent_id = None
    opponent_name = None
    if len(args) >= 3:
        mention = args[2]
        try:
            u = await client.get_users(mention)
            opponent_id = u.id
            opponent_name = u.first_name
        except Exception:
            opponent_id = None
    elif message.reply_to_message:
        opponent_id = message.reply_to_message.from_user.id
        opponent_name = message.reply_to_message.from_user.first_name

    if opponent_id is None:
        return await message.reply(tiny("⚠ COULD NOT RESOLVE OPPONENT. TAG OR REPLY TO A USER."))

    # check balances
    chal_user = await user_collection.find_one({"id": challenger.id})
    opp_user = await user_collection.find_one({"id": opponent_id})
    if (chal_user.get("balance", 0) if chal_user else 0) < bet:
        return await message.reply(tiny("🚨 YOU DONT HAVE ENOUGH COINS TO CHALLENGE"))
    if (opp_user.get("balance", 0) if opp_user else 0) < bet:
        return await message.reply(tiny("🚨 OPPONENT DOES NOT HAVE ENOUGH COINS"))

    # create challenge id
    cid = uuid.uuid4().hex[:8]
    pending_challenges[cid] = {
        "cid": cid,
        "challenger": challenger.id,
        "opponent": opponent_id,
        "bet": bet,
        "created_at": datetime.utcnow().isoformat()
    }

    kb = [
        [InlineKeyboardButton("✅ ACCEPT", callback_data=f"mg:acc:{cid}"),
         InlineKeyboardButton("❌ DECLINE", callback_data=f"mg:rej:{cid}")]
    ]

    # send challenge to opponent
    try:
        await client.send_message(
            opponent_id,
            tiny(f"🎮 YOU HAVE BEEN CHALLENGED BY {challenger.first_name}\nBET: {bet} COINS EACH\nCLICK TO ACCEPT OR DECLINE"),
            reply_markup=InlineKeyboardMarkup(kb)
        )
    except Exception:
        pending_challenges.pop(cid, None)
        return await message.reply(tiny("⚠ COULD NOT SEND CHALLENGE TO OPPONENT (PRIVATE MESSAGES MAY BE CLOSED)."))

    await message.reply(tiny(f"CHALLENGE SENT TO {opponent_name} (ID {cid})"))

@bot.on_callback_query(filters.regex(r"^mg:rej:[0-9a-f]{8}$"))
async def mg_reject_handler(client, cq):
    await cq.answer()
    cid = cq.data.split(":")[2]
    chal = pending_challenges.get(cid)
    if not chal:
        return await cq.answer(tiny("⚠ CHALLENGE NOT FOUND"), show_alert=True)
    if cq.from_user.id != chal["opponent"]:
        return await cq.answer(tiny("THIS IS NOT FOR YOU"), show_alert=True)

    pending_challenges.pop(cid, None)
    try:
        await cq.message.edit_text(tiny("CHALLENGE DECLINED"))
    except:
        pass
    try:
        await client.send_message(chal["challenger"], tiny(f"YOUR CHALLENGE {cid} WAS DECLINED"))
    except:
        pass

@bot.on_callback_query(filters.regex(r"^mg:acc:[0-9a-f]{8}$"))
async def mg_accept_handler(client, cq):
    await cq.answer()
    cid = cq.data.split(":")[2]
    chal = pending_challenges.get(cid)
    if not chal:
        return await cq.answer(tiny("⚠ CHALLENGE NOT FOUND"), show_alert=True)
    if cq.from_user.id != chal["opponent"]:
        return await cq.answer(tiny("THIS IS NOT FOR YOU"), show_alert=True)

    # show size selection
    kb = [
        [InlineKeyboardButton("5 x 5", callback_data=f"mg:size:{cid}:5")],
        [InlineKeyboardButton("9 x 9", callback_data=f"mg:size:{cid}:9")],
        [InlineKeyboardButton("12 x 12", callback_data=f"mg:size:{cid}:12")],
    ]
    try:
        await cq.message.edit_text(tiny("SELECT BOARD SIZE"), reply_markup=InlineKeyboardMarkup(kb))
    except:
        pass

@bot.on_callback_query(filters.regex(r"^mg:size:[0-9a-f]{8}:\d+$"))
async def mg_size_selected(client, cq):
    await cq.answer()
    parts = cq.data.split(":")
    try:
        cid = parts[2]
        size = int(parts[3])
    except Exception:
        return await cq.answer(tiny("⚠ INVALID SELECTION"), show_alert=True)

    chal = pending_challenges.get(cid)
    if not chal:
        return await cq.answer(tiny("⚠ CHALLENGE EXPIRED"), show_alert=True)

    challenger_id = chal["challenger"]
    opponent_id = chal["opponent"]
    bet = chal["bet"]

    # re-check balances
    chal_user = await user_collection.find_one({"id": challenger_id})
    opp_user = await user_collection.find_one({"id": opponent_id})
    if (chal_user.get("balance", 0) if chal_user else 0) < bet:
        pending_challenges.pop(cid, None)
        return await cq.answer(tiny("CHALLENGER INSUFFICIENT FUNDS"), show_alert=True)
    if (opp_user.get("balance", 0) if opp_user else 0) < bet:
        pending_challenges.pop(cid, None)
        return await cq.answer(tiny("OPPONENT INSUFFICIENT FUNDS"), show_alert=True)

    # deduct bets
    await user_collection.update_one({"id": challenger_id}, {"$inc": {"balance": -bet}}, upsert=True)
    await user_collection.update_one({"id": opponent_id}, {"$inc": {"balance": -bet}}, upsert=True)

    # create game
    total_cells = size * size
    mines_count = mines_count_by_size(size)
    mine_positions = gen_mines(total_cells, mines_count)

    game = {
        "cid": cid,
        "mode": "multi",
        "players": [challenger_id, opponent_id],
        "bet": bet,
        "size": size,
        "bombs": mines_count,
        "mine_positions": mine_positions,
        "clicked": [],
        "turn": challenger_id,  # challenger starts
        "started_at": datetime.utcnow().isoformat()
    }

    active_mgames[cid] = game
    pending_challenges.pop(cid, None)

    # build keyboard
    def build_board_kb(g):
        sz = g["size"]
        kb = []
        for i in range(sz):
            row = []
            for j in range(sz):
                idx = i*sz + j
                row.append(InlineKeyboardButton("❓", callback_data=f"mp:{cid}:{idx}"))
            kb.append(row)
        return kb

    kb = build_board_kb(game)

    # try to notify both players; edit accept message and send to challenger
    try:
        await cq.message.edit_text(
            tiny(f"🎮 MINES DUEL STARTED!\nBET: {bet} EACH  POOL: {bet*2}\nSIZE: {size}x{size}  BOMBS: {mines_count}\nTURN: {game['turn']}"),
            reply_markup=InlineKeyboardMarkup(kb)
        )
    except:
        pass

    try:
        # send a message to challenger too
        await client.send_message(game["players"][0],
                                  tiny(f"🎮 MINES DUEL STARTED!\nBET: {bet} EACH  POOL: {bet*2}\nSIZE: {size}x{size}  BOMBS: {mines_count}\nTURN: {game['turn']}"),
                                  reply_markup=InlineKeyboardMarkup(kb))
    except:
        pass

@bot.on_callback_query(filters.regex(r"^mp:[0-9a-f]{8}:\d+$"))
async def mp_tile_handler(client, cq):
    await cq.answer()
    try:
        _, cid, pos_str = cq.data.split(":")
        pos = int(pos_str)
    except Exception:
        return await cq.answer(tiny("⚠ INVALID BUTTON"), show_alert=True)

    game = active_mgames.get(cid)
    if not game:
        return await cq.answer(tiny("⚠ NO ACTIVE MULTIPLAYER GAME"), show_alert=True)

    user_id = cq.from_user.id
    if user_id not in game["players"]:
        return await cq.answer(tiny("THIS IS NOT YOUR GAME"), show_alert=True)

    if user_id != game["turn"]:
        return await cq.answer(tiny("NOT YOUR TURN"), show_alert=True)

    if pos in game["clicked"]:
        return await cq.answer(tiny("ALREADY OPENED"), show_alert=True)

    game["clicked"].append(pos)

    # if mine -> other player wins
    if pos in game["mine_positions"]:
        players = game["players"]
        winner = players[1] if players[0] == user_id else players[0]
        pool = game["bet"] * 2
        # pay winner
        await user_collection.update_one({"id": winner}, {"$inc": {"balance": pool}}, upsert=True)

        # reveal board
        sz = game["size"]
        keyboard = []
        for i in range(sz):
            row = []
            for j in range(sz):
                idx = i*sz + j
                if idx in game["mine_positions"]:
                    row.append(InlineKeyboardButton("💣", callback_data=f"mpx:{cid}:ign"))
                elif idx in game["clicked"]:
                    row.append(InlineKeyboardButton("✅", callback_data=f"mpx:{cid}:ign"))
                else:
                    row.append(InlineKeyboardButton("❎", callback_data=f"mpx:{cid}:ign"))
            keyboard.append(row)

        # announce result (use user ids in message; you can resolve names if needed)
        text = tiny(f"💥 MINE HIT!\nWINNER: {winner}  WON: {pool} COINS")
        try:
            await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass

        # notify both players privately (best-effort)
        for p in game["players"]:
            try:
                await client.send_message(p, tiny(f"GAME {cid} ENDED. WINNER: {winner} WON {pool} COINS"))
            except:
                pass

        # cleanup
        active_mgames.pop(cid, None)

        # auto-delete the chat message after 5 seconds (best-effort)
        await asyncio.sleep(5)
        try:
            await cq.message.delete()
        except:
            pass

        return

    # safe tile: flip turn
    players = game["players"]
    game["turn"] = players[1] if players[0] == user_id else players[0]

    # rebuild keyboard showing opened tiles
    sz = game["size"]
    keyboard = []
    for i in range(sz):
        row = []
        for j in range(sz):
            idx = i*sz + j
            if idx in game["clicked"]:
                row.append(InlineKeyboardButton("✅", callback_data=f"mpx:{cid}:ign"))
            else:
                row.append(InlineKeyboardButton("❓", callback_data=f"mp:{cid}:{idx}"))
        keyboard.append(row)

    status = tiny(f"🎮 MINES DUEL\nBET: {game['bet']} EACH  POOL: {game['bet']*2}\nSIZE: {sz}x{sz}  BOMBS: {game['bombs']}\nTURN: {game['turn']}")

    # edit current message
    try:
        await cq.message.edit_text(status, reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        pass

    # notify both players of updated board (best-effort)
    for p in game["players"]:
        try:
            await client.send_message(p, status, reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass

@bot.on_callback_query(filters.regex(r"^mpx:[0-9a-f]{8}:ign$"))
async def mp_ignore_buttons(client, cq):
    await cq.answer()
    # ignore revealed/disabled presses

# ---------------- End of file ---------------- #
