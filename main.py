import time
import logging
import requests
import json
import random
import itertools
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate
import pyfiglet  
import sys

# Inisialisasi colorama agar warna otomatis reset setelah setiap cetakan
init(autoreset=True)

logging.basicConfig(filename="activity.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def log_message(level, message):
    current_time = get_current_time()
    full_message = f"[{current_time}] {message}"

    colors = {
        "info": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    }
    
    color = colors.get(level, Fore.WHITE)
    icons = {
        "info": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    print(color + icons.get(level, "ℹ️") + " " + full_message)
    
    if level == "info":
        logging.info(full_message)
    elif level == "warning":
        logging.warning(full_message)
    elif level == "error":
        logging.error(full_message)
        exit(1)

def tampilkan_banner():
    banner = pyfiglet.figlet_format("BOT DIALOG")
    print(Fore.CYAN + banner)

def countdown(waktu_mulai_menit):
    total_detik = waktu_mulai_menit * 60
    while total_detik > 0:
        if total_detik > 60:
            log_message("info", f"⏳ Memulai dalam {total_detik // 60} menit...")
            time.sleep(60)
        else:
            for i in range(total_detik, 0, -1):
                sys.stdout.write(f"\r⌛ Memulai dalam {i} detik" + "." * (i % 4))
                sys.stdout.flush()
                time.sleep(1)
            break
    print()
    log_message("info", "🚀 Mulai sekarang!")

def animasi_spinner(pesan, durasi=3):
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    for _ in range(durasi * 5):
        sys.stdout.write(f"\r🔄 {pesan} {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write("\r" + " " * (len(pesan) + 5) + "\r")

def validasi_token(nama_token, token):
    headers = {"Authorization": token}
    try:
        animasi_spinner(f"Memvalidasi Token {nama_token}")
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if response.status_code == 200:
            log_message("info", f"✅ Token {nama_token} valid.")
            return True
        else:
            log_message("error", f"❌ Token {nama_token} tidak valid! (Status Code: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        log_message("error", f"❌ Kesalahan saat memvalidasi token {nama_token}: {e}")
        return False

def mengetik(channel_id, token):
    headers = {'Authorization': token}
    try:
        for _ in range(3):
            sys.stdout.write("\r💬 Bot sedang mengetik" + "." * (_ % 4))
            sys.stdout.flush()
            time.sleep(1)
        print()
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/typing", headers=headers)
        if response.status_code in [200, 204]:
            log_message("info", "✍️ Typing indicator dikirim.")
    except requests.exceptions.RequestException as e:
        log_message("error", f"❌ Error saat mengirim typing indicator: {e}")

def kirim_pesan(channel_id, nama_token, token, pesan, message_reference=None):
    headers = {'Authorization': token}
    payload = {'content': pesan}
    if message_reference:
        payload['message_reference'] = {'message_id': message_reference}
    
    try:
        mengetik(channel_id, token)
        time.sleep(2)

        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", json=payload, headers=headers)

        if response.status_code == 200:
            message_id = response.json().get('id')
            sys.stdout.write("\r📩 " + Fore.GREEN + f"[{nama_token}] Pesan dikirim: '{pesan}' (Message ID: {message_id})\n")
            return message_id
        elif response.status_code == 429:
            retry_after = int(response.json().get("retry_after", 1))
            for i in range(retry_after, 0, -1):
                sys.stdout.write(f"\r⚠️ Rate limit! Tunggu {i} detik" + "." * (i % 4))
                sys.stdout.flush()
                time.sleep(1)
            print()
            return kirim_pesan(channel_id, nama_token, token, pesan, message_reference)
        else:
            log_message("error", f"❌ [{nama_token}] Gagal mengirim pesan: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message("error", f"❌ Error saat mengirim pesan: {e}")

def main():
    tampilkan_banner()

    try:
        with open("dialog.txt", "r", encoding="utf-8") as f:
            dialog_list = json.load(f)
        if not dialog_list:
            raise ValueError("File dialog.txt kosong.")

        with open("token.txt", "r") as f:
            tokens = []
            for line in f.readlines():
                parts = line.strip().split(":")
                if len(parts) != 4:
                    raise ValueError("Format token.txt salah! Gunakan: nama_token:token:min_interval:max_interval")
                nama_token, token, min_interval, max_interval = parts
                tokens.append((nama_token, token, int(min_interval), int(max_interval)))

        if len(tokens) < 2:
            raise ValueError("File token harus berisi minimal 2 akun.")

        # **Validasi Token**
        for nama_token, token, _, _ in tokens:
            if not validasi_token(nama_token, token):
                return  

        channel_id = input(Fore.CYAN + "Masukkan ID channel: " + Style.RESET_ALL).strip()
        if not channel_id.isdigit():
            raise ValueError("Channel ID harus angka.")

        waktu_mulai_menit = int(input(Fore.CYAN + "Masukkan waktu mulai dalam menit (0 untuk langsung mulai): " + Style.RESET_ALL))
        if waktu_mulai_menit < 0:
            raise ValueError("Waktu mulai tidak boleh negatif.")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        log_message("error", f"❌ Error: {e}")
        return

    if waktu_mulai_menit > 0:
        countdown(waktu_mulai_menit)

    log_message("info", "🚀 Memulai percakapan otomatis...")

    log_message("info", "🎉 Percakapan selesai.")

if __name__ == "__main__":
    main()
