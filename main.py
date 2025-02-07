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
    
    # Jika ada message_reference, tambahkan ke payload
    if message_reference:
        payload['message_reference'] = {'message_id': message_reference}
    
    try:
        send_response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                                      json=payload, headers=headers)

        # Cek status kode dari respons
        if send_response.status_code == 200:
            message_id = send_response.json().get('id')
            log_message("info", f"Token {nama_token} ({token[:10]}...): Pesan dikirim: {pesan}")
            return message_id  # Mengembalikan message_id yang baru saja dikirim
        elif send_response.status_code == 429:
            retry_after = send_response.json().get("retry_after", 1)
            log_message("warning", f"Token {nama_token} ({token[:10]}...): Rate limit terkena. Tunggu selama {retry_after:.2f} detik.")
            time.sleep(retry_after)  # Tunggu sesuai waktu yang disarankan
            return kirim_pesan(channel_id, nama_token, token, pesan, message_reference)  # Coba kirim ulang
        else:
            log_message("error", f"Token {nama_token} ({token[:10]}...): Gagal mengirim pesan: {send_response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        log_message("error", f"Error saat mengirim pesan: {e}")
        return None

def main():
    try:
        # Baca file dialog
        with open("dialog.txt", "r", encoding="utf-8") as f:
            dialog_list = [line.strip() for line in f.readlines()]
        if not dialog_list:
            raise ValueError("File dialog.txt kosong.")

        # Baca file token dan nama
        with open("token.txt", "r") as f:
            tokens = [line.strip().split(":") for line in f.readlines()]  # Format: nama_token:token
        if len(tokens) < 2:
            raise ValueError("File token harus berisi minimal 2 akun.")

        # Input ID channel
        channel_id = input("Masukkan ID channel: ").strip()
        if not channel_id.isdigit():
            raise ValueError("Channel ID harus berupa angka.")

        # Input waktu interval
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

    token_a, token_b = tokens[:2]  # Ambil 2 token pertama
    nama_a, token_a = token_a
    nama_b, token_b = token_b

    turn = 0  # Menentukan giliran siapa yang bicara
    message_id_a = None  # Menyimpan message ID yang terakhir dikirim oleh A
    message_id_b = None  # Menyimpan message ID yang terakhir dikirim oleh B
    max_responses = 10  # Batasan jumlah balasan dalam satu sesi

    while turn < max_responses:
        try:
            # Pilih pesan berdasarkan giliran
            if turn >= len(dialog_list):
                log_message("info", "Percakapan selesai.")
                break  # Hentikan jika semua dialog sudah dipakai

            pesan = dialog_list[turn]

            if turn % 2 == 0:  # A mengirim pesan
                message_id_a = kirim_pesan(channel_id, nama_a, token_a, pesan, message_reference=message_id_b)
                if not message_id_a:
                    log_message("error", "Gagal mengirim pesan dari A.")
                    break
                waktu_tunggu = random.uniform(waktu_kirim_min, waktu_kirim_max)
            else:  # B mengirim pesan
                time.sleep(random.uniform(waktu_balas_min, waktu_balas_max))  # Tunggu sebelum membalas
                message_id_b = kirim_pesan(channel_id, nama_b, token_b, pesan, message_reference=message_id_a)
                if not message_id_b:
                    log_message("error", "Gagal mengirim pesan dari B.")
                    break
                waktu_tunggu = random.uniform(waktu_kirim_min, waktu_kirim_max)

            turn += 1
            time.sleep(waktu_tunggu)  # Tunggu sebelum pesan berikutnya dikirim

        except Exception as e:
            log_message("error", f"Terjadi kesalahan: {e}")
            break

    log_message("info", "Selesai.")

# Jalankan program utama
if __name__ == "__main__":
    main()
