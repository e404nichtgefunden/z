import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = '8010517053:AAExq84JVA-8b01oF66fJ4LZgLrgHlGR2Os'
ADMIN_USER_ID = 7316824198

allowed_users = set()
allowed_groups = set()
current_dir = os.path.expanduser("~")

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_dir
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    command = update.message.text.strip()

    # Admin-only commands
    if user_id == ADMIN_USER_ID:
        if command.startswith("adduser "):
            uid = command[8:].strip()
            if uid.isdigit():
                allowed_users.add(int(uid))
                await update.message.reply_text(f"User {uid} added.")
            return

        if command.startswith("deluser "):
            uid = command[8:].strip()
            if uid.isdigit() and int(uid) in allowed_users:
                allowed_users.remove(int(uid))
                await update.message.reply_text(f"User {uid} removed.")
            return

        if command.startswith("addgroup "):
            gid = command[9:].strip()
            if gid.isdigit():
                allowed_groups.add(int(gid))
                await update.message.reply_text(f"Group {gid} added.")
            return

        if command.startswith("delgroup "):
            gid = command[9:].strip()
            if gid.isdigit() and int(gid) in allowed_groups:
                allowed_groups.remove(int(gid))
                await update.message.reply_text(f"Group {gid} removed.")
            return

        if command.startswith("addbot "):
            token = command[7:].strip()
            if token:
                filename = f"bot_{token[:8]}.py"
                with open(filename, 'w') as f:
                    f.write(f"""import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = '{token}'
current_dir = os.path.expanduser("~")

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_dir
    command = update.message.text.strip()
    if command.startswith("./"):
        file_path = os.path.join(current_dir, command[2:].split()[0])
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=current_dir,
                    timeout=600
                )
                output = result.stdout.strip() + "\\n" + result.stderr.strip()
                output = output.strip() or "root@bot:~#"
            except Exception as e:
                output = f"Error: {{str(e)}}"
            for i in range(0, len(output), 4000):
                await update.message.reply_text(output[i:i+4000])
        else:
            await update.message.reply_text("File tidak ditemukan atau tidak dapat dieksekusi.")
    else:
        await update.message.reply_text("Perintah tidak diizinkan.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_command))

if __name__ == '__main__':
    print("BOT READY.")
    app.run_polling()
""")
                await update.message.reply_text(f"Bot baru dibuat: {filename}")
            return

    # Access control
    if chat_type in ['group', 'supergroup'] and chat_id not in allowed_groups:
        await update.message.reply_text("Group not allowed.")
        return
    if chat_type == 'private' and user_id != ADMIN_USER_ID and user_id not in allowed_users:
        await update.message.reply_text("Kamu siapa?")
        return

    # Allowed users can only execute commands starting with './'
    if command.startswith("./"):
        file_path = os.path.join(current_dir, command[2:].split()[0])
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=current_dir,
                    timeout=600
                )
                output = result.stdout.strip() + "\n" + result.stderr.strip()
                output = output.strip() or "root@bot:~#"
            except Exception as e:
                output = f"Error: {str(e)}"
            for i in range(0, len(output), 4000):
                await update.message.reply_text(output[i:i+4000])
        else:
            await update.message.reply_text("File tidak ditemukan atau tidak dapat dieksekusi.")
    else:
        await update.message.reply_text("Perintah tidak diizinkan.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_command))

if __name__ == '__main__':
    print("SUPERBOT MAIN PROCESS READY.")
    app.run_polling()
