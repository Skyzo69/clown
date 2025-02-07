import time
import logging
import requests
import random  # Import random untuk membuat waktu tunggu acak
from colorama import Fore, Style
from datetime import datetime  # Untuk mendapatkan waktu saat ini

# Konfigurasi logging ke file
logging.basicConfig(filename="activity.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def get_current_time():
    """Mengembalikan waktu saat ini dalam format HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")

def log_message(level, message):
    """Log pesan ke file dan konsol dengan waktu."""
    current_time = get_current_time()  # Mendapatkan waktu saat ini
    full_message = f"[{current_time}] {message}"  # Menambahkan waktu ke pesan
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
    """Mengirimkan typing indicator ke channel."""
    headers = {'Authorization': token}
    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/typing",
                                 headers=headers)
        if response.status_code == 200:
            log_message("info", "Typing indicator terkirim.")
        else:
            log_message("error", f"Gagal mengirim typing indicator: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message("error", f"Error saat mengirim typing indicator: {e}")

def ketik_dikonsol(nama_token):
    """Menampilkan waktu mengetik di konsol."""
    start_time = get_current_time()
    log_message("info", f"[{nama_token}] Mulai mengetik pada {start_time}...")
    
    # Simulasi typing dengan delay acak antara 3 hingga 6 detik
    time.sleep(random.uniform(3, 6))

    end_time = get_current_time()
    log_message("info", f"[{nama_token}] Selesai mengetik pada {end_time}.")

def kirim_pesan(channel_id, nama_token, token, pesan, message_reference=None):
    """Mengirim pesan ke channel tertentu menggunakan token, dengan reference jika ada."""
    headers = {'Authorization': token}
    payload = {'content': pesan}

    if message_reference:
        payload['message_reference'] = {'message_id': message_reference}

    try:
        # Kirim typing indicator terlebih dahulu
        mengetik(channel_id, token)
        
        # Menampilkan typing di konsol
        ketik_dikonsol(nama_token)

        # Kirim pesan setelah mengetik
        send_response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                                      json=payload, headers=headers)

        if send_response.status_code == 200:
            message_id = send_response.json().get('id')
            log_message("info", f"[{nama_token}] Pesan dikirim: '{pesan}' (Message ID: {message_id})")
            return message_id
        elif send_response.status_code == 429:
            retry_after = send_response.json().get("retry_after", 1)
            log_message("warning", f"[{nama_token}] Rate limit terkena. Tunggu {retry_after:.2f} detik.")
            time.sleep(retry_after)
            return kirim_pesan(channel_id, nama_token, token, pesan, message_reference)
        else:
            log_message("error", f"[{nama_token}] Gagal mengirim pesan: {send_response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        log_message("error", f"Error saat mengirim pesan: {e}")
        return None

def main():
    try:
        with open("dialog.txt", "r", encoding="utf-8") as f:
            dialog_list = [line.strip() for line in f.readlines()]
        if not dialog_list:
            raise ValueError("File dialog.txt kosong.")

        with open("token.txt", "r") as f:
            tokens = [line.strip().split(":") for line in f.readlines()]
        if len(tokens) < 2:
            raise ValueError("File token harus berisi minimal 2 akun.")

        channel_id = input("Masukkan ID channel: ").strip()
        if not channel_id.isdigit():
            raise ValueError("Channel ID harus berupa angka.")

        # Mengatur waktu tunggu minimal dan maksimal untuk Token A dan B
        waktu_tunggu_a_min = float(input("Set Waktu Tunggu Token A Minimum (detik): "))
        waktu_tunggu_a_max = float(input("Set Waktu Tunggu Token A Maksimum (detik): "))
        waktu_tunggu_b_min = float(input("Set Waktu Tunggu Token B Minimum (detik): "))
        waktu_tunggu_b_max = float(input("Set Waktu Tunggu Token B Maksimum (detik): "))

        if waktu_tunggu_a_min < 1 or waktu_tunggu_b_min < 1 or waktu_tunggu_a_max < 1 or waktu_tunggu_b_max < 1:
            raise ValueError("Waktu tunggu harus lebih dari 1 detik.")
        if waktu_tunggu_a_min > waktu_tunggu_a_max or waktu_tunggu_b_min > waktu_tunggu_b_max:
            raise ValueError("Waktu tunggu minimum tidak boleh lebih besar dari maksimum.")

    except FileNotFoundError as e:
        log_message("error", f"File tidak ditemukan: {e}")
        return
    except ValueError as e:
        log_message("error", f"Input error: {e}")
        return
    except Exception as e:
        log_message("error", f"Unexpected error: {e}")
        return

    log_message("info", "Memulai percakapan otomatis...")

    nama_a, token_a = tokens[0]
    nama_b, token_b = tokens[1]

    last_message_id = None
    index = 0

    while index < len(dialog_list):
        try:
            # Token A mengirim pesan pertama kali atau membalas Token B dengan waktu acak
            waktu_tunggu_a = random.uniform(waktu_tunggu_a_min, waktu_tunggu_a_max)
            time.sleep(waktu_tunggu_a)
            pesan_a = dialog_list[index]
            last_message_id = kirim_pesan(channel_id, nama_a, token_a, pesan_a, message_reference=last_message_id)
            index += 1

            if index >= len(dialog_list):
                break

            # Token B membalas Token A dengan waktu acak
            waktu_tunggu_b = random.uniform(waktu_tunggu_b_min, waktu_tunggu_b_max)
            time.sleep(waktu_tunggu_b)
            pesan_b = dialog_list[index]
            last_message_id = kirim_pesan(channel_id, nama_b, token_b, pesan_b, message_reference=last_message_id)
            index += 1

        except Exception as e:
            log_message("error", f"Terjadi kesalahan: {e}")
            break

    log_message("info", "Percakapan selesai.")

if __name__ == "__main__":
    main()
