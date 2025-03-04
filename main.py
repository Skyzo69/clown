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

DISCORD_API_BASE = "https://discord.com/api/v9"

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

def mengetik(channel_id, token):
    """Mengirim typing indicator ke channel."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(f"{DISCORD_API_BASE}/channels/{channel_id}/typing", headers=headers)
        if response.status_code in [200, 204]:
            log_message("info", "Typing indicator dikirim.")
        elif response.status_code == 401:
            log_message("error", "Token tidak valid! Periksa kembali file token.txt")
        elif response.status_code == 403:
            log_message("error", "Token diblokir! Tidak bisa mengirim pesan.")
        else:
            log_message("warning", f"Gagal mengirim typing indicator: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message("error", f"Error saat mengirim typing indicator: {e}")

def kirim_pesan(channel_id, nama_token, token, pesan, message_reference=None):
    """Mengirim pesan ke channel dengan handling error dan retry."""
    if len(pesan) > 2000:
        log_message("error", f"Pesan terlalu panjang (>{len(pesan)} karakter), tidak dikirim.")
        return None

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    payload = {'content': pesan}

    if message_reference:
        payload['message_reference'] = {'message_id': message_reference}

    for _ in range(3):  # Coba maksimal 3 kali jika error
        try:
            mengetik(channel_id, token)
            time.sleep(2)  # Simulasi delay mengetik
            response = requests.post(f"{DISCORD_API_BASE}/channels/{channel_id}/messages", json=payload, headers=headers)

            if response.status_code in [200, 201]:
                try:
                    message_id = response.json().get('id')
                    if message_id:
                        log_message("info", f"[{nama_token}] Pesan dikirim: '{pesan}' (Message ID: {message_id})")
                        return message_id
                    else:
                        log_message("warning", f"[{nama_token}] Tidak mendapatkan Message ID.")
                except json.JSONDecodeError:
                    log_message("error", f"[{nama_token}] Respons API tidak valid.")
            elif response.status_code == 401:
                log_message("error", f"[{nama_token}] Token tidak valid! Pesan tidak dikirim.")
                return None
            elif response.status_code == 403:
                log_message("error", f"[{nama_token}] Token diblokir! Pesan tidak dikirim.")
                return None
            elif response.status_code == 429:
                response_json = response.json()
                retry_after = response_json.get("retry_after", 1)
                is_global = response_json.get("global", False)

                if is_global:
                    log_message("warning", f"[{nama_token}] Rate limit GLOBAL! Tunggu {retry_after:.2f} detik.")
                else:
                    log_message("warning", f"[{nama_token}] Rate limit! Tunggu {retry_after:.2f} detik.")

                time.sleep(retry_after)
            else:
                log_message("error", f"[{nama_token}] Gagal mengirim pesan: {response.status_code}")

        except requests.exceptions.RequestException as e:
            log_message("error", f"Error saat mengirim pesan: {e}")
            time.sleep(2)  # Tunggu sebentar sebelum mencoba lagi

    log_message("error", f"[{nama_token}] Gagal mengirim pesan setelah 3 percobaan.")
    return None

def tampilkan_daftar_token(tokens):
    """Menampilkan daftar token dalam format tabel."""
    header = ["Nama", "Min Interval", "Max Interval"]
    tabel = [(nama, interval_min, interval_max) for nama, _, interval_min, interval_max in tokens]

    print("\n╭──────────────────────────────────╮")
    print("│           Daftar Token           │")
    print("├─────────┬────────────┬───────────┤")
    print(tabulate(tabel, headers=header, tablefmt="plain"))
    print("╰─────────┴────────────┴───────────╯\n")

def validasi_channel(channel_id, token):
    """Memeriksa apakah channel ID valid."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(f"{DISCORD_API_BASE}/channels/{channel_id}", headers=headers)

    if response.status_code == 200:
        return True
    elif response.status_code == 403:
        log_message("error", f"Token tidak memiliki izin untuk channel ID {channel_id}.")
    else:
        log_message("error", f"Channel ID {channel_id} tidak valid. Status code: {response.status_code}")
    return False

def main():
    try:
        with open("dialog.txt", "r", encoding="utf-8") as f:
            dialog_list = json.load(f)
        if not isinstance(dialog_list, list) or not all(isinstance(d, dict) for d in dialog_list):
            raise ValueError("Format file dialog.txt salah! Harus berupa list JSON dengan objek dict.")
        if not all("text" in d and "sender" in d for d in dialog_list):
            raise ValueError("Setiap elemen dalam dialog.txt harus memiliki 'text' dan 'sender'.")

        with open("token.txt", "r") as f:
            tokens = []
            for line in f.readlines():
                parts = line.strip().split(":")
                if len(parts) != 4:
                    raise ValueError("Format token.txt salah! Gunakan: nama_token:token:min_interval:max_interval")
                nama_token, token, min_interval, max_interval = parts
                if not min_interval.isdigit() or not max_interval.isdigit():
                    raise ValueError(f"Min/max interval harus angka: {min_interval}, {max_interval}")
                tokens.append((nama_token, token, int(min_interval), int(max_interval)))

        if len(tokens) < 2:
            raise ValueError("File token harus berisi minimal 2 akun.")

        tampilkan_daftar_token(tokens)

        channel_id = input("Masukkan ID channel: ").strip()
        if not channel_id.isdigit():
            raise ValueError("Channel ID harus angka.")

        if not validasi_channel(channel_id, tokens[0][1]):
            return

        waktu_mulai_menit = int(input("Masukkan waktu mulai dalam menit (0 untuk langsung mulai): "))
        if waktu_mulai_menit < 0:
            raise ValueError("Waktu mulai tidak boleh negatif.")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        log_message("error", f"Error: {e}")
        return

    if waktu_mulai_menit > 0:
        log_message("info", f"Menunggu {waktu_mulai_menit} menit sebelum mulai...")
        time.sleep(waktu_mulai_menit * 60)

    log_message("info", "Memulai percakapan otomatis...")

if __name__ == "__main__":
    main()
