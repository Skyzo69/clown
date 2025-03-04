import time
import logging
import requests
import json
from colorama import Fore, Style
from datetime import datetime
import random
from tabulate import tabulate

# Konfigurasi logging ke file
logging.basicConfig(filename="activity.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

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
        exit(1)  # Jika error, skrip langsung berhenti.

def mengetik(channel_id, token):
    """Mengirim typing indicator ke channel."""
    headers = {'Authorization': token}
    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/typing", headers=headers)
        if response.status_code in [200, 204]:
            log_message("info", "Typing indicator dikirim.")
    except requests.exceptions.RequestException as e:
        log_message("error", f"Error saat mengirim typing indicator: {e}")

def kirim_pesan(channel_id, nama_token, token, pesan, message_reference=None):
    """Mengirim pesan ke channel, dengan reference jika ada."""
    headers = {'Authorization': token}
    payload = {'content': pesan}

    if message_reference:
        payload['message_reference'] = {'message_id': message_reference}

    try:
        mengetik(channel_id, token)
        time.sleep(2)  # Simulasi delay mengetik
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
    """Menampilkan daftar token dalam format tabel."""
    header = ["Nama", "Min Interval", "Max Interval"]
    tabel = [(nama, interval_min, interval_max) for nama, _, interval_min, interval_max in tokens]

    print("\n╭──────────────────────────────────╮")
    print("│           Daftar Token           │")
    print("├─────────┬────────────┬───────────┤")
    print(tabulate(tabel, headers=header, tablefmt="plain"))
    print("╰─────────┴────────────┴───────────╯\n")

def main():
    try:
        # Load dialog
        with open("dialog.txt", "r", encoding="utf-8") as f:
            dialog_list = json.load(f)
        if not dialog_list:
            raise ValueError("File dialog.txt kosong.")

        # Load token dan interval
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

        # Tampilkan daftar token
        tampilkan_daftar_token(tokens)

        channel_id = input("Masukkan ID channel: ").strip()
        if not channel_id.isdigit():
            raise ValueError("Channel ID harus angka.")

        waktu_mulai_menit = int(input("Masukkan waktu mulai dalam menit (0 untuk langsung mulai): "))
        if waktu_mulai_menit < 0:
            raise ValueError("Waktu mulai tidak boleh negatif.")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        log_message("error", f"Error: {e}")
        return

    # Jika ada waktu tunggu sebelum mulai
    if waktu_mulai_menit > 0:
        log_message("info", f"Menunggu {waktu_mulai_menit} menit sebelum mulai...")
        time.sleep(waktu_mulai_menit * 60)

    log_message("info", "Memulai percakapan otomatis...")

    message_history = {}

    index = 0
    while index < len(dialog_list):
        try:
            dialog = dialog_list[index]
            text = dialog["text"]
            sender_index = dialog["sender"]
            reply_to = dialog.get("reply_to", None)  # Bisa None atau indeks tertentu
            double_send = dialog.get("double_send", False)  # Apakah sender boleh kirim 2 kali

            if sender_index >= len(tokens):
                log_message("error", f"Sender index {sender_index} di luar batas jumlah token.")
                return

            # Ambil data token dan interval
            nama_token, token, min_interval, max_interval = tokens[sender_index]

            # Cari message_id yang akan dibalas
            message_reference = message_history.get(reply_to)

            # Kirim pesan pertama
            message_id = kirim_pesan(channel_id, nama_token, token, text, message_reference)
            if message_id:
                message_history[index] = message_id

            # Custom interval sesuai token
            waktu_tunggu = random.uniform(min_interval, max_interval)
            log_message("info", f"Waktu tunggu {waktu_tunggu:.2f} detik sebelum pesan berikutnya...")
            time.sleep(waktu_tunggu)

            # Jika double_send, kirim lagi tanpa menunggu giliran
            if double_send and index + 1 < len(dialog_list):
                next_dialog = dialog_list[index + 1]
                if next_dialog["sender"] == sender_index:
                    next_text = next_dialog["text"]
                    next_message_id = kirim_pesan(channel_id, nama_token, token, next_text, message_id)
                    if next_message_id:
                        message_history[index + 1] = next_message_id
                    index += 1  # Lewati 1 langkah karena sudah dikirim

            index += 1

        except Exception as e:
            log_message("error", f"Terjadi kesalahan: {e}")
            return

    log_message("info", "Percakapan selesai.")

if __name__ == "__main__":
    main()
