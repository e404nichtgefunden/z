# === superbot_fixed.py ===

import os
import subprocess
import signal
import json
import time
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Constants
MAIN_BOT_PATH = '/root/z/superbot.py'
LOG_FILE = '/root/z/bot_activity.log'
STATE_FILE = '/root/z/running_bots.json'
USERS_FILE = '/root/z/allowed_users.json'
GROUPS_FILE = '/root/z/allowed_groups.json'
START_TIME = time.time()

# Initial config
running_processes = {}
allowed_users = set()
allowed_groups = set()
ADMIN_USER_IDS = [7316824198]

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

def log_action(msg):
    print(msg)
    logging.info(msg)

def save_state():
    with open(STATE_FILE, 'w') as f:
        json.dump(running_processes, f)

def load_state():
    global running_processes
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try:
                running_processes = json.load(f)
            except:
                running_processes = {}

def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump(list(allowed_users), f)

def load_users():
    global allowed_users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try:
                allowed_users = set(json.load(f))
            except:
                allowed_users = set()

def save_groups():
    with open(GROUPS_FILE, 'w') as f:
        json.dump(list(allowed_groups), f)

def load_groups():
    global allowed_groups
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'r') as f:
            try:
                allowed_groups = set(json.load(f))
            except:
                allowed_groups = set()

def is_process_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except:
        return False

async def restart_bot(script):
    if script in running_processes:
        try:
            os.kill(running_processes[script], signal.SIGKILL)
        except:
            pass
        del running_processes[script]

    if os.path.isfile(script):
        proc = subprocess.Popen(["python3", script])
        running_processes[script] = proc.pid
        log_action(f"[AUTO-RESTART] Restarted {script} (PID: {proc.pid})")
        save_state()
        return proc.pid
    return None

async def heartbeat():
    while True:
        await asyncio.sleep(60)
        to_restart = []
        for script, pid in list(running_processes.items()):
            if not is_process_alive(pid):
                to_restart.append(script)
        for script in to_restart:
            await restart_bot(script)

def format_uptime():
    delta = int(time.time() - START_TIME)
    hours, rem = divmod(delta, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours}h {minutes}m {seconds}s"

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    command = update.message.text.strip()

    if chat_type in ['group', 'supergroup'] and chat_id not in allowed_groups and not command.startswith("./stx"):
        await update.message.reply_text("This group is not allowed to use the bot.")
        return

    if user_id not in ADMIN_USER_IDS and user_id not in allowed_users and not command.startswith("./stx"):
        await update.message.reply_text("Access denied.")
        return

    log_action(f"[COMMAND] {user_id}@{chat_id} > {command}")

    if user_id in ADMIN_USER_IDS:
        if command.startswith("adduser "):
            new_id = command[8:].strip()
            if new_id.isdigit():
                allowed_users.add(int(new_id))
                save_users()
                await update.message.reply_text(f"User {new_id} added.")
            else:
                await update.message.reply_text("Invalid user ID.")
            return

        if command.startswith("deluser "):
            rem_id = command[8:].strip()
            if rem_id.isdigit() and int(rem_id) in allowed_users:
                allowed_users.remove(int(rem_id))
                save_users()
                await update.message.reply_text(f"User {rem_id} removed.")
            else:
                await update.message.reply_text("User not found.")
            return

        if command.startswith("addgroup "):
            gid = command[9:].strip()
            if gid.isdigit():
                allowed_groups.add(int(gid))
                save_groups()
                await update.message.reply_text(f"Group {gid} added.")
            else:
                await update.message.reply_text("Invalid group ID.")
            return

        if command.startswith("delgroup "):
            gid = command[9:].strip()
            if gid.isdigit() and int(gid) in allowed_groups:
                allowed_groups.remove(int(gid))
                save_groups()
                await update.message.reply_text(f"Group {gid} removed.")
            else:
                await update.message.reply_text("Group not found.")
            return

        if command == "listuser":
            msg = "Allowed Users:\n" + "\n".join(str(u) for u in allowed_users)
            await update.message.reply_text(msg)
            return

        if command == "listgroup":
            msg = "Allowed Groups:\n" + "\n".join(str(g) for g in allowed_groups)
            await update.message.reply_text(msg)
            return

        if command.startswith("deploy "):
            token = command[7:].strip()
            script_path = f"/root/z/bot_{token[:8]}.py"
            with open(script_path, "w") as f:
                f.write(open(MAIN_BOT_PATH).read().replace("BOT_TOKEN = ''", f"BOT_TOKEN = '{token}'"))
            await restart_bot(script_path)
            await update.message.reply_text(f"Deployed and started bot: {token[:8]}")
            return

        if command == "runtime":
            await update.message.reply_text(f"Bot uptime: {format_uptime()}")
            return

        if command == "bantuan":
            help_text = (
                "Perintah Admin:\n"
                "- adduser <id> - deluser <id> - listuser\n"
                "- addgroup <id> - delgroup <id> - listgroup\n"            
                "- deploy <token> - runtime - bantuan\n"
                "Khusus Admin: gunakan 'cmd:' sebelum command terminal\n"
                "Khusus allowed user/group: gunakan './stx ip port durasi thread'"
            )
            await update.message.reply_text(help_text)
            return

        if command.startswith("cmd "):
            shell_cmd = command[4:].strip()
            try:
                result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, timeout=600)
                output = result.stdout.strip() + "\n" + result.stderr.strip()
            except Exception as e:
                output = f"Error: {str(e)}"
            output = output.strip() or "Command executed."
            for i in range(0, len(output), 4000):
                await update.message.reply_text(output[i:i+4000])
            return

    if command.startswith("./stx"):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=600)
            output = result.stdout.strip() + "\n" + result.stderr.strip()
        except Exception as e:
            output = f"Error: {str(e)}"
        output = output.strip() or "Command executed."
        for i in range(0, len(output), 4000):
            await update.message.reply_text(output[i:i+4000])
        return

    await update.message.reply_text("Unknown command or not allowed here.")

# MAIN
BOT_TOKEN = '8010517053:AAExq84JVA-8b01oF66fJ4LZgLrgHlGR2Os'
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_command))

async def main():
    log_action("SUPERBOT is running...")
    load_state()
    load_users()
    load_groups()
    asyncio.create_task(heartbeat())
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
