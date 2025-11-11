import asyncio
import os
import subprocess
import shutil
import datetime
from pyrogram import filters, types
from pyrogram.handlers import MessageHandler

# Assuming BADMUSIC and config are correctly imported from the main application structure
# from BADMUSIC import app, config
# from BADMUSIC.core.lang import lang
# Since I don't have access to the full project structure, I will use placeholder names
# If the app object is not defined, this will fail at runtime, but I must keep the original imports.

from BADMUSIC import app, config
from BADMUSIC import lang

# Global state dictionary to track user conversations
user_states = {}

# Fixed repo URL
REPO_URL = "https://github.com/masoombalak88/BADMUSIC.git"

# Steps for hosting
STEPS = [
    "API_ID",
    "API_HASH",
    "MONGO_URL",
    "OWNER_ID",
    "STRING_SESSION",
    "LOGGER_ID",
    "BOT_TOKEN"
]

@app.on_message(filters.command(["host"]) & app.sudoers)
@lang.language()
async def start_host_command(_, m: types.Message):
    user_id = m.from_user.id
    if user_id in user_states:
        await m.reply_text("❌ You already have an ongoing hosting process. Use /cancel to start new.")
        return
    
    user_states[user_id] = {
        "step": 0,
        "data": {},
        "instance_dir": None
    }
    
    await m.reply_text(
        "🚀 **Bot Hosting Started!**\n\n"
        "I'll guide you step by step. Send the values one by one.\n\n"
        f"**Step 1: Send your API_ID** (Get from https://my.telegram.org)"
    )

# Cancel command
@app.on_message(filters.command(["cancel"]) & app.sudoers)
async def cancel_host(_, m: types.Message):
    user_id = m.from_user.id
    if user_id not in user_states:
        await m.reply_text("❌ No ongoing hosting process.")
        return
    
    # Cleanup if directory exists
    if user_states[user_id]["instance_dir"]:
        # Using shutil.rmtree to recursively delete the directory
        shutil.rmtree(user_states[user_id]["instance_dir"], ignore_errors=True)
    
    del user_states[user_id]
    await m.reply_text("✅ Hosting process cancelled and cleaned up.")

# Handler for collecting inputs
@app.on_message(filters.private & filters.text & ~filters.command(["host", "cancel"]))
async def collect_host_input(client, m: types.Message):
    user_id = m.from_user.id
    if user_id not in user_states:
        return  # Ignore if not in hosting process or not a private message
    
    state = user_states[user_id]
    current_step = state["step"]
    
    # Ensure we don't try to access an index out of bounds
    if current_step >= len(STEPS):
        # This should ideally not happen if logic is correct, but safe to check
        await m.reply_text("✅ All steps completed! Processing...")
        await finalize_hosting(user_id, m)
        return
        
    step_name = STEPS[current_step]
    
    # Store the input
    state["data"][step_name] = m.text.strip()
    
    # Move to next step
    if current_step + 1 < len(STEPS):
        next_step = current_step + 1
        state["step"] = next_step
        next_name = STEPS[next_step]
        await m.reply_text(f"✅ **{step_name}** saved!\n\n**Step {next_step + 1}: Send your {next_name}**")
    else:
        # All data collected, proceed to hosting
        await m.reply_text(f"✅ **{step_name}** saved! All data collected, commencing hosting process...")
        state["step"] = -1 # Mark as processing
        await finalize_hosting(user_id, m)

async def finalize_hosting(user_id: int, m: types.Message):
    state = user_states[user_id]
    data = state["data"]
    
    # Validation
    api_id = data.get("API_ID")
    api_hash = data.get("API_HASH")
    mongo_url = data.get("MONGO_URL")
    owner_id = data.get("OWNER_ID")
    string_session = data.get("STRING_SESSION")
    logger_id = data.get("LOGGER_ID")
    bot_token = data.get("BOT_TOKEN")
    
    if not all([api_id, api_hash, mongo_url, owner_id, string_session, logger_id, bot_token]):
        await m.reply_text("❌ Missing data. Restart with /host.")
        return
    
    # Updated validation to handle negative IDs for OWNER_ID and LOGGER_ID
    try:
        api_id_int = int(api_id)
        owner_id_int = int(owner_id)
        logger_id_int = int(logger_id)
    except ValueError:
        await m.reply_text("❌ Invalid API_ID, OWNER_ID, or LOGGER_ID. Must be integers.")
        return
    
    if api_id_int < 0:
        await m.reply_text("❌ API_ID cannot be negative.")
        return
    
    if not bot_token.startswith("bot"):
        await m.reply_text("❌ Invalid BOT_TOKEN. Must start with 'bot'.")
        return
    if not mongo_url.startswith("mongodb://"):
        await m.reply_text("❌ Invalid MONGO_URL. Must start with 'mongodb://'.")
        return
    
    # Create unique directory
    instance_dir = f"hosted_bot_{user_id}_{int(datetime.datetime.now().timestamp())}"
    state["instance_dir"] = instance_dir
    os.makedirs(instance_dir, exist_ok=True)
    
    try:
        # Clone repo
        await m.reply_text(f"🔄 Cloning **{REPO_URL}** to `{instance_dir}`...")
        clone_cmd = ["git", "clone", REPO_URL, instance_dir]
        process = await asyncio.create_subprocess_exec(
            *clone_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Git clone failed:\n{stderr.decode()}")
        
        # Create .env file
        env_path = os.path.join(instance_dir, ".env")
        with open(env_path, "w") as f:
            f.write(f"""API_ID={api_id}
API_HASH={api_hash}
BOT_TOKEN={bot_token}
SESSION={string_session}
MONGO_URL={mongo_url}
OWNER_ID={owner_id}
LOGGER_ID={logger_id}
UPSTREAM_BRANCH=main""")
        
        await m.reply_text("📄 `.env` file created with your details.")
        
        # Install dependencies
        await m.reply_text("📦 Installing dependencies from `requirements.txt`...")
        pip_cmd = ["pip3", "install", "-r", "requirements.txt"]
        
        pip_process = await asyncio.create_subprocess_exec(
            *pip_cmd, cwd=instance_dir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        pip_stdout, pip_stderr = await pip_process.communicate()
        
        if pip_process.returncode != 0:
            raise Exception(f"Dependency installation failed:\n{pip_stderr.decode()}")
        
        await m.reply_text("✅ Dependencies installed!")
        
        # Start bot in background
        await m.reply_text("🚀 Starting your bot instance in the background (using `nohup`)...")
        start_cmd = f"cd {instance_dir} && nohup python3 -m BADMUSIC &> bot.log &"
        os.system(start_cmd)
        
        # Wait and check log
        await asyncio.sleep(5)
        log_path = os.path.join(instance_dir, "bot.log")
        log_tail = "Log file not found or empty after 5 seconds."
        
        if os.path.exists(log_path):
            try:
                with open(log_path, "r") as log_f:
                    log_tail = log_f.read(1000)
            except Exception as log_read_error:
                log_tail = f"Could not read log file: {log_read_error}"
        
        # Success message
        success_msg = f"""
✅ **Your Bot Hosted Successfully!**

📁 **Instance Directory**: `{instance_dir}`
🔗 **Repo**: {REPO_URL}
📄 **Configuration**: `.env` file created.
▶️ **Bot Status**: Started in background.

**Recent Log Snippet (first 1000 chars):**
<pre>{log_tail}</pre>
"""
        await m.reply_text(success_msg)
    
    except Exception as e:
        await m.reply_text(f"❌ Hosting failed:\n<code>{e}</code>")
    
    finally:
        # Clean up user state after completion or failure
        if user_id in user_states:
            del user_states[user_id]
