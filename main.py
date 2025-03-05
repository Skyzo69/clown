import time
import logging
import requests
import json
import random
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate
import pyfiglet  # Tambahkan pyfiglet untuk banner

# Inisialisasi colorama agar warna otomatis reset setelah setiap cetakan
init(autoreset=True)

logging.basicConfig(filename="activity.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def log_message(level, message):
    current_time = get_current_time()
    full_message = f"[{current_time}] {message}"

    if level == "info":
        logging.info(full_message)
        print(Fore.GREEN + full_message + Style.RESET_ALL)
    elif level == "warning":
        logging.warning(full_message)
        print(Fore.YELLOW + full_message + Style.RESET_ALL)
    elif level == "error":
        logging.error(full_message)
        print(Fore.RED + full_message + Style.RESET_ALL)
        exit(1)

def tampilkan_banner():
    banner = pyfiglet.figlet_format("BOT DIALOG")
    print(Fore.CYAN + banner + Style.RESET_ALL)

def countdown(waktu_mulai_menit):
    total_detik = waktu_mulai_menit * 60

    while total_detik > 0:
        if total_detik > 60:
            menit = total_detik // 60
            log_message("info", f"Memulai dalam {menit} menit...")
            time.sleep(60)  # Update tiap menit
        elif total_detik > 10:
            log_message("info", f"Memulai dalam {total_detik} detik...")
            time.sleep(10)  # Update tiap 10 detik
        else:
            log_message("info", f"Memulai dalam {total_detik} detik...")
            time.sleep(1)  # Update tiap detik
        total_detik -= 1

    log_message("info", "Mulai sekarang!")

def mengetik(channel_id, token):
    headers = {'Authorization': token}
    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/typing", headers=headers)
        if response.status_code in [200, 204]:
            log_message("info", "Typing indicator dikirim.")
    except requests.exceptions.RequestException as e:
        log_message("error", f"Error saat mengirim typing indicator: {e}")

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
            log_message("info", f"[{nama_token}] Pesan dikirim: '{pesan}' (Message ID: {message_id})")
            return message_id
        elif response.status_code == 429:
            retry_after = response.json().get("retry_after", 1)
            log_message("warning", f"[{nama_token}] Rate limit! Tunggu {retry_after:.2f} detik.")
            time.sleep(retry_after)
            return kirim_pesan(channel_id, nama_token, token, pesan, message_reference)
        else:
            log_message("error", f"[{nama_token}] Gagal mengirim pesan: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message("error", f"Error saat mengirim pesan: {e}")

def tampilkan_daftar_token(tokens):
    header = ["Nama", "Min Interval", "Max Interval"]
    tabel = [(nama, interval_min, interval_max) for nama, _, interval_min, interval_max in tokens]

    print(Fore.CYAN + "\n╭──────────────────────────────────╮")
    print("│           Daftar Token           │")
    print("├─────────┬────────────┬───────────┤")
    print(tabulate(tabel, headers=header, tablefmt="plain"))
    print("╰─────────┴────────────┴───────────╯\n" + Style.RESET_ALL)

def main():
    tampilkan_banner()  # Tampilkan banner di awal

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

        tampilkan_daftar_token(tokens)

        channel_id = input(Fore.CYAN + "Masukkan ID channel: " + Style.RESET_ALL).strip()
        if not channel_id.isdigit():
            raise ValueError("Channel ID harus angka.")

        waktu_mulai_menit = int(input(Fore.CYAN + "Masukkan waktu mulai dalam menit (0 untuk langsung mulai): " + Style.RESET_ALL))
        if waktu_mulai_menit < 0:
            raise ValueError("Waktu mulai tidak boleh negatif.")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        log_message("error", f"Error: {e}")
        return

    if waktu_mulai_menit > 0:
        countdown(waktu_mulai_menit)

    log_message("info", "Memulai percakapan otomatis...")

    last_message_per_sender = {}

    for index, dialog in enumerate(dialog_list):
        try:
            text = dialog["text"]
            sender_index = dialog["sender"]
            reply_to = dialog.get("reply_to", None)
            double_send = dialog.get("double_send", False)

            if sender_index >= len(tokens):
                log_message("error", f"Sender index {sender_index} di luar batas jumlah token.")
                return

            nama_token, token, min_interval, max_interval = tokens[sender_index]

            message_reference = last_message_per_sender.get(reply_to) if reply_to is not None else None

            message_id = kirim_pesan(channel_id, nama_token, token, text, message_reference)
            if message_id:
                last_message_per_sender[sender_index] = message_id

            waktu_tunggu = random.uniform(min_interval, max_interval)
            log_message("info", f"Waktu tunggu {waktu_tunggu:.2f} detik sebelum pesan berikutnya...")
            time.sleep(waktu_tunggu)

            if double_send and index + 1 < len(dialog_list):
                next_dialog = dialog_list[index + 1]
                if next_dialog["sender"] == sender_index:
                    next_text = next_dialog["text"]
                    next_message_id = kirim_pesan(channel_id, nama_token, token, next_text, message_id)
                    if next_message_id:
                        last_message_per_sender[sender_index] = next_message_id
                    index += 1  

        except Exception as e:
            log_message("error", f"Terjadi kesalahan: {e}")
            return

    log_message("info", "Percakapan selesai.")

if __name__ == "__main__":
    main()
