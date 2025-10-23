import time
from pyrogram import filters
from TEAMZYRO import app, sudo_users

@app.on_message(filters.command("ping") & filters.user(sudo_users))
async def ping(client, message):
    # Start timer
    start_time = time.time()

    # Send initial message
    sent_msg = await message.reply_text("Pong!")

    # Calculate elapsed time
    end_time = time.time()
    elapsed_time = round((end_time - start_time) * 1000, 3)

    # Edit message with ping
    await sent_msg.edit_text(f"Pong! {elapsed_time} ms")


# Optional: Handle non-sudo users
@app.on_message(filters.command("ping") & ~filters.user(sudo_users))
async def ping_non_sudo(client, message):
    await message.reply_text("❌ This command is only for Sudo users!")