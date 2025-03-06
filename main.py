import time
import logging
import requests
import json
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from tabulate import tabulate
import pyfiglet  

# Inisialisasi colorama agar warna otomatis reset setelah setiap cetakan
init(autoreset=True)

logging.basicConfig(filename="activity.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def log_message(level, message):
    """Mencetak pesan dengan warna dan mencatat ke log file"""
    current_time = get_current_time()
    full_message = f"[{current_time}] {message}"

    colors = {
        "info": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED
    }
    
    color = colors.get(level, Fore.WHITE)
    print(color + full_message)
    
    if level == "info":
        logging.info(full_message)
    elif level == "warning":
        logging.warning(full_message)
    elif level == "error":
        logging.error(full_message)
        exit(1)

def tampilkan_banner():
    """Menampilkan banner dengan pyfiglet"""
    banner = pyfiglet.figlet_format("BOT DIALOG")
    print(Fore.CYAN + banner)

def format_waktu(sisa_detik):
    """Format waktu menjadi jam, menit, detik"""
    waktu = str(timedelta(seconds=sisa_detik))
    return waktu

def tampilkan_bar(progress, total):
    """Membuat progress bar dengan panjang 30 karakter"""
    panjang_bar = 30
    filled_length = int(panjang_bar * progress / total)
    bar = "█" * filled_length + "▒" * (panjang_bar - filled_length)
    return f"[{bar}]"

def countdown(waktu_mulai_menit):
    total_detik = waktu_mulai_menit * 60

    if waktu_mulai_menit >= 60:
        jam = waktu_mulai_menit // 60
        menit = waktu_mulai_menit % 60
        log_message("info", f"\n🕒 Memulai dalam {jam} jam {menit} menit...\n")

    while total_detik > 0:
        waktu_str = format_waktu(total_detik)
        bar = tampilkan_bar(total_detik, waktu_mulai_menit * 60)

        print(Fore.CYAN + f"\r⏳ {bar} {waktu_str} lagi...", end="", flush=True)

        if total_detik > 600:  # Jika lebih dari 10 menit, update setiap 5 menit
            sleep_time = 300
        elif total_detik > 300:  # Jika lebih dari 5 menit, update setiap 1 menit
            sleep_time = 60
        elif total_detik > 60:  # Jika lebih dari 1 menit, update setiap 30 detik
            sleep_time = 30
        elif total_detik > 10:  # Jika lebih dari 10 detik, update setiap 10 detik
            sleep_time = 10
        else:  # Countdown final 10 detik
            for i in range(total_detik, 0, -1):
                bar = tampilkan_bar(i, waktu_mulai_menit * 60)
                print(Fore.RED + f"\r⏳ {bar} {i} detik lagi... ", end="", flush=True)
                time.sleep(1)
            break

        time.sleep(sleep_time)
        total_detik -= sleep_time  # Kurangi waktu sesuai sleep

    print(Fore.GREEN + "\n🚀 Mulai sekarang!\n")

def validasi_token(nama_token, token):
    headers = {"Authorization": token}
    try:
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if response.status_code == 200:
            log_message("info", f"✅ Token {nama_token} valid.")
            return True
        else:
            log_message("error", f"❌ Token {nama_token} tidak valid! (Status Code: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        log_message("error", f"⚠️ Kesalahan saat memvalidasi token {nama_token}: {e}")
        return False

def mengetik(channel_id, token):
    headers = {'Authorization': token}
    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/typing", headers=headers)
        if response.status_code in [200, 204]:
            log_message("info", "💬 Bot sedang mengetik...")
    except requests.exceptions.RequestException as e:
        log_message("error", f"❗ Error saat mengirim typing indicator: {e}")

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
            log_message("info", f"📩 [{nama_token}] Pesan dikirim: '{pesan}' (Message ID: {message_id})")
            return message_id
        elif response.status_code == 429:
            retry_after = response.json().get("retry_after", 1)
            log_message("warning", f"⚠️ [{nama_token}] Rate limit! Tunggu {retry_after:.2f} detik.")
            time.sleep(retry_after)
            return kirim_pesan(channel_id, nama_token, token, pesan, message_reference)
        else:
            log_message("error", f"❌ [{nama_token}] Gagal mengirim pesan: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message("error", f"❗ Error saat mengirim pesan: {e}")

def tampilkan_daftar_token(tokens):
    header = ["Nama Token", "Min Interval (s)", "Max Interval (s)"]
    tabel = [(nama, interval_min, interval_max) for nama, _, interval_min, interval_max in tokens]

    print(Fore.CYAN + "\n" + "="*40)
    print(Fore.YELLOW + "           🎛️ DAFTAR TOKEN")
    print(Fore.CYAN + "="*40)
    print(tabulate(tabel, headers=header, tablefmt="grid"))
    print(Fore.CYAN + "="*40 + "\n")

def main():
    tampilkan_banner()

    try:
        with open("dialog.txt", "r", encoding="utf-8") as f:
            dialog_list = json.load(f)
        if not dialog_list:
            raise ValueError("❌ File dialog.txt kosong.")

        with open("token.txt", "r") as f:
tokens = []
for line in f.readlines():
parts = line.strip().split(":")
if len(parts) != 4:
raise ValueError("⚠️ Format token.txt salah! Gunakan: nama_token:token:min_interval:max_interval")
nama_token, token, min_interval, max_interval = parts
tokens.append((nama_token, token, int(min_interval), int(max_interval)))

if len(tokens) < 2:  
        raise ValueError("⚠️ File token harus berisi minimal 2 akun.")  

    # **Validasi Token Sebelum Melanjutkan**  
    for nama_token, token, _, _ in tokens:  
        if not validasi_token(nama_token, token):  
            return  

        tampilkan_daftar_token(tokens)

        channel_id = input(Fore.CYAN + "🔢 Masukkan ID channel: " + Style.RESET_ALL).strip()
        if not channel_id.isdigit():
            raise ValueError("⚠️ Channel ID harus angka.")

        waktu_mulai_menit = int(input(Fore.CYAN + "⏳ Masukkan waktu mulai dalam menit (0 untuk langsung mulai): " + Style.RESET_ALL))
        if waktu_mulai_menit < 0:
            raise ValueError("⚠️ Waktu mulai tidak boleh negatif.")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        log_message("error", f"❗ Error: {e}")
        return

    if waktu_mulai_menit > 0:
        countdown(waktu_mulai_menit)

    log_message("info", "🤖 Memulai percakapan otomatis...")

    last_message_per_sender = {}

    for index, dialog in enumerate(dialog_list):
        try:
            text = dialog["text"]
            sender_index = dialog["sender"]
            reply_to = dialog.get("reply_to", None)

            if sender_index >= len(tokens):
                log_message("error", f"⚠️ Sender index {sender_index} di luar batas jumlah token.")
                return

            nama_token, token, min_interval, max_interval = tokens[sender_index]

            message_reference = last_message_per_sender.get(reply_to) if reply_to is not None else None

            message_id = kirim_pesan(channel_id, nama_token, token, text, message_reference)
            if message_id:
                last_message_per_sender[sender_index] = message_id

            waktu_tunggu = random.uniform(min_interval, max_interval)
            log_message("info", f"⏳ Waktu tunggu {waktu_tunggu:.2f} detik sebelum pesan berikutnya...")
            time.sleep(waktu_tunggu)

        except Exception as e:
            log_message("error", f"❗ Terjadi kesalahan: {e}")
            return

    log_message("info", "🎉 Percakapan selesai.")

if __name__ == "__main__":
    main()
