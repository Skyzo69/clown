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

        waktu_balas_min = float(input("Set Waktu Balas Minimal (detik): "))
        waktu_balas_max = float(input("Set Waktu Balas Maksimal (detik): "))
        waktu_tunggu_min = float(input("Set Waktu Tunggu Minimal Sebelum A Kirim Lagi (detik): "))
        waktu_tunggu_max = float(input("Set Waktu Tunggu Maksimal Sebelum A Kirim Lagi (detik): "))

        if waktu_balas_min < 1 or waktu_balas_max < waktu_balas_min:
            raise ValueError("Waktu balas tidak valid.")
        if waktu_tunggu_min < 1 or waktu_tunggu_max < waktu_tunggu_min:
            raise ValueError("Waktu tunggu tidak valid.")

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

    for i in range(0, len(dialog_list), 2):  # Loop dalam pasangan (A -> B -> A -> B)
        try:
            if i >= len(dialog_list):
                break

            # 1. Bot A mengirim pesan pertama
            message_id = kirim_pesan(channel_id, nama_a, token_a, dialog_list[i])
            if message_id:
                waktu_balas = random.uniform(waktu_balas_min, waktu_balas_max)
                log_message("info", f"Menunggu {waktu_balas:.2f} detik sebelum balasan dari Bot B...")
                time.sleep(waktu_balas)

            if i + 1 >= len(dialog_list):
                break

            # 2. Bot B membalas menggunakan Token A (sebagai reply)
            message_id = kirim_pesan(channel_id, nama_a, token_a, dialog_list[i + 1], message_reference=message_id)
            if message_id:
                waktu_tunggu = random.uniform(waktu_tunggu_min, waktu_tunggu_max)
                log_message("info", f"Menunggu {waktu_tunggu:.2f} detik sebelum Bot A mengirim pesan lagi...")
                time.sleep(waktu_tunggu)

            if i + 2 >= len(dialog_list):
                break

            # 3. Bot A mengirim pesan berikutnya
            message_id = kirim_pesan(channel_id, nama_a, token_a, dialog_list[i + 2], message_reference=message_id)
            if message_id:
                waktu_balas = random.uniform(waktu_balas_min, waktu_balas_max)
                log_message("info", f"Menunggu {waktu_balas:.2f} detik sebelum balasan dari Bot B...")
                time.sleep(waktu_balas)

            if i + 3 >= len(dialog_list):
                break

            # 4. Bot B membalas menggunakan Token B
            message_id = kirim_pesan(channel_id, nama_b, token_b, dialog_list[i + 3], message_reference=message_id)

        except Exception as e:
            log_message("error", f"Terjadi kesalahan: {e}")
            break

    log_message("info", "Selesai.")

if __name__ == "__main__":
    main()
