import os
import time
import subprocess

BOT_SCRIPT = "stx1.py"

while True:
    try:
        print("[INFO] Menjalankan bot...")
        process = subprocess.Popen(["python3", BOT_SCRIPT])
        process.wait()
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat menjalankan bot: {e}")
    
    print("[WARNING] Bot berhenti. Mengulang dalam 5 detik...")
    time.sleep(5)
