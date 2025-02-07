import random
import time
import logging
import requests
from colorama import Fore, Style

# Konfigurasi logging ke file
logging.basicConfig(filename="activity.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def log_message(level, message):
    """Log pesan ke file dan konsol."""
    if level == "info":
        logging.info(message)
        print(Fore.GREEN + message + Style.RESET_ALL)
    elif level == "warning":
        logging.warning(message)
        print(Fore.YELLOW + message + Style.RESET_ALL)
    elif level == "error":
        logging.error(message)
        print(Fore.RED + message + Style.RESET_ALL)

def kirim_pesan(channel_id, nama_token, token, pesan, message_reference=None):
    """Mengirim pesan ke channel tertentu menggunakan token, dengan reference jika ada."""
    headers = {'Authorization': token}
    payload = {'content': pesan}

    if message_reference:
        payload['message_reference'] = {'message_id': message_reference}

    try:
        send_response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                                      json=payload, headers=headers)

        if send_response.status_code == 200:
            message_id = send_response.json().get('id')
            log_message("info", f"Token {nama_token} ({token[:10]}...): Pesan dikirim: {pesan}")
            return message_id
        elif send_response.status_code == 429:
            retry_after = send_response.json().get("retry_after", 1)
            log_message("warning", f"Token {nama_token} ({token[:10]}...): Rate limit terkena. Tunggu {retry_after:.2f} detik.")
            time.sleep(retry_after)
            return kirim_pesan(channel_id, nama_token, token, pesan, message_reference)
        else:
            log_message("error", f"Token {nama_token} ({token[:10]}...): Gagal mengirim pesan: {send_response.status_code}")
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

        waktu_kirim_min = float(input("Set Waktu Kirim Pesan Minimal (detik): "))
        waktu_kirim_max = float(input("Set Waktu Kirim Pesan Maksimal (detik): "))
        waktu_balas_min = float(input("Set Waktu Balas Minimal (detik): "))
        waktu_balas_max = float(input("Set Waktu Balas Maksimal (detik): "))

        if waktu_kirim_min < 1 or waktu_kirim_max < waktu_kirim_min:
            raise ValueError("Waktu kirim tidak valid.")
        if waktu_balas_min < 1 or waktu_balas_max < waktu_balas_min:
            raise ValueError("Waktu balas tidak valid.")

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

    token_a, token_b = tokens[:2]
    nama_a, token_a = token_a
    nama_b, token_b = token_b

    message_id_a = None
    message_id_b = None

    for turn, pesan in enumerate(dialog_list):
        try:
            if turn % 2 == 0:
                # A mengirim pesan dulu
                message_id_a = kirim_pesan(channel_id, nama_a, token_a, pesan, message_reference=message_id_b)
                if message_id_a:
                    waktu_tunggu = random.uniform(waktu_kirim_min, waktu_kirim_max)
                    log_message("info", f"Menunggu {waktu_tunggu:.2f} detik sebelum balasan...")
                    time.sleep(waktu_tunggu)  # Tunggu sebelum giliran berikutnya
            else:
                # Tunggu waktu balasan sebelum B membalas
                waktu_balas = random.uniform(waktu_balas_min, waktu_balas_max)
                log_message("info", f"Menunggu {waktu_balas:.2f} detik sebelum balasan dari {nama_b}...")
                time.sleep(waktu_balas)

                # B membalas pesan A
                message_id_b = kirim_pesan(channel_id, nama_b, token_b, pesan, message_reference=message_id_a)

        except Exception as e:
            log_message("error", f"Terjadi kesalahan: {e}")
            break

    log_message("info", "Selesai.")

if __name__ == "__main__":
    main()
