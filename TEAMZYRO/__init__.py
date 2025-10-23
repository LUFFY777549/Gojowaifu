# ------------------------------ IMPORTS ---------------------------------
import logging
import os
from telegram.ext import Application
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client, filters as f

# --------------------------- LOGGING SETUP ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)

logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.ERROR)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)

# ---------------------------- CONSTANTS ---------------------------------
api_id = os.getenv("API_ID", "21218274")
api_hash = os.getenv("API_HASH", "3474a18b61897c672d315fb330edb213")
TOKEN = os.getenv("TOKEN", "7442709602:AAH2MLkbFmtGjeBOSIN8DOPq8y-o6gfGkIc")
GLOG = os.getenv("GLOG", "-1002946070634")
CHARA_CHANNEL_ID = os.getenv("CHARA_CHANNEL_ID", "-1002691911300")
SUPPORT_CHAT_ID = os.getenv("SUPPORT_CHAT_ID", "-1002691911300")
mongo_url = os.getenv("MONGO_URL", "mongodb+srv://sufyan532011:5042@auctionbot.5ms20.mongodb.net/?retryWrites=true&w=majority&appName=AuctionBot")

MUSJ_JOIN = os.getenv("MUSJ_JOIN", "https://t.me/AlphaXBot_Support")

# Modified to support both image and video URLs
START_MEDIA = os.getenv("START_MEDIA", "https://files.catbox.moe/3kd6oq.jpg,https://files.catbox.moe/nkg2ly.jpg,https://files.catbox.moe/0zvwpt.jpg,https://files.catbox.moe/z7d8i6.jpg").split(',')

PHOTO_URL = [
    os.getenv("PHOTO_URL_1", "https://files.catbox.moe/f5njbm.jpg"),
    os.getenv("PHOTO_URL_2", "https://files.catbox.moe/3saw6n.jpg")
]

STATS_IMG = ["https://files.catbox.moe/0zvwpt.jpg"]

SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/AlphaXBot_Support")
UPDATE_CHAT = os.getenv("UPDATE_CHAT", "https://t.me/Alpha_X_Updates")
SUDO = list(map(int, os.getenv("SUDO", "7576729648").split(',')))
OWNER_ID = int(os.getenv("OWNER_ID", "7576729648"))

# --------------------- TELEGRAM BOT CONFIGURATION -----------------------
command_filter = f.create(lambda _, __, message: message.text and message.text.startswith("/"))
application = Application.builder().token(TOKEN).build()
ZYRO = Client("Shivu", api_id=api_id, api_hash=api_hash, bot_token=TOKEN)

# -------------------------- DATABASE SETUP ------------------------------
ddw = AsyncIOMotorClient(mongo_url)
db = ddw['hinata_waifu']

# Collections
user_totals_collection = db['gaming_totals']
group_user_totals_collection = db['gaming_group_total']
top_global_groups_collection = db['gaming_global_groups']
pm_users = db['gaming_pm_users']
destination_collection = db['gamimg_user_collection']
destination_char = db['gaming_anime_characters']
questions_collection = db["questions"]
group_collection = db["groups"]
waifu_collection = db["waifus"]
mines_collection = db["mines_games"]
multi_collection = db["multi_mines"]
txn_collection = db["transactions"]

# -------------------------- GLOBAL VARIABLES ----------------------------
app = ZYRO
sudo_users = SUDO
collection = destination_char
user_collection = destination_collection

# --------------------------- STRIN ---------------------------------------
locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}
last_user = {}
warned_users = {}
user_cooldowns = {}
user_nguess_progress = {}
user_guess_progress = {}
normal_message_counts = {}  

# -------------------------- POWER SETUP --------------------------------
from TEAMZYRO.unit.zyro_ban import *
from TEAMZYRO.unit.zyro_sudo import *
from TEAMZYRO.unit.zyro_react import *
from TEAMZYRO.unit.zyro_log import *
from TEAMZYRO.unit.zyro_send_img import *
from TEAMZYRO.unit.zyro_rarity import *
# ------------------------------------------------------------------------

async def PLOG(text: str):
    await app.send_message(
       chat_id=GLOG,
       text=text
   )

# ---------------------------- END OF CODE ------------------------------
