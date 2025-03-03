import time
import logging
import requests
import random  
from colorama import Fore, Style
from datetime import datetime  

# Konfigurasi logging ke file
logging.basicConfig(filename="activity.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def get_current_time():
    """Mengembalikan waktu saat ini dalam format HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")

def log_message(level, message):
    """Log pesan ke file dan konsol dengan waktu."""
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

def tunggu_waktu_mulai(jam_mulai, menit_mulai):
    """Menunggu hingga waktu yang ditentukan."""
    while True:
        sekarang = datetime.now()
        jam_sekarang, menit_sekarang = sekarang.hour, sekarang.minute
        
        if jam_sekarang > jam_mulai or (jam_sekarang == jam_mulai and menit_sekarang >= menit_mulai):
            log_message("info", "Waktu mulai tercapai. Memulai eksekusi...")
            break

        sisa_menit = (jam_mulai - jam_sekarang) * 60 + (menit_mulai - menit_sekarang)
        log_message("info", f"Menunggu waktu mulai dalam {sisa_menit} menit...")
        time.sleep(10)

def mengetik(channel_id, token):
    """Mengirimkan typing indicator ke channel."""
    headers = {'Authorization': token}
    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/typing", headers=headers)
        
        if response.status_code in [200, 204]:
            log_message("info", f"Typing indicator terkirim (Status: {response.status_code}).")
        else:
            log_message("warning", f"Gagal mengirim typing indicator: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message("error", f"Error saat mengirim typing indicator: {e}")

def ketik_dikonsol(nama_token):
    """Menampilkan waktu mengetik di konsol."""
    start_time = get_current_time()
    log_message("info", f"[{nama_token}] Mulai mengetik pada {start_time}...")
    
    time.sleep(random.uniform(3, 6))

    end_time = get_current_time()
    log_message("info", f"[{nama_token}] Selesai mengetik pada {end_time}.")

def kirim_pesan(channel_id, nama_token, token, pesan, message_reference=None):
    """Mengirim pesan ke channel tertentu."""
    headers = {'Authorization': token}
    payload = {'content': pesan}

    if message_reference:
        payload['message_reference'] = {'message_id': message_reference}

    try:
        mengetik(channel_id, token)
        ketik_dikonsol(nama_token)

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
        jam_mulai = int(input("Masukkan jam mulai (0-23): "))
        menit_mulai = int(input("Masukkan menit mulai (0-59): "))

        if not (0 <= jam_mulai < 24 and 0 <= menit_mulai < 60):
            raise ValueError("Jam dan menit harus dalam rentang yang benar.")

        tunggu_waktu_mulai(jam_mulai, menit_mulai)

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

        waktu_tunggu_a_min = float(input("Set Waktu Tunggu Token A Minimum (detik): "))
        waktu_tunggu_a_max = float(input("Set Waktu Tunggu Token A Maksimum (detik): "))
        waktu_tunggu_b_min = float(input("Set Waktu Tunggu Token B Minimum (detik): "))
        waktu_tunggu_b_max = float(input("Set Waktu Tunggu Token B Maksimum (detik): "))

        if any(x < 1 for x in [waktu_tunggu_a_min, waktu_tunggu_a_max, waktu_tunggu_b_min, waktu_tunggu_b_max]):
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
            waktu_tunggu_a = random.uniform(waktu_tunggu_a_min, waktu_tunggu_a_max)
            time.sleep(waktu_tunggu_a)
            pesan_a = dialog_list[index]
            last_message_id = kirim_pesan(channel_id, nama_a, token_a, pesan_a, message_reference=last_message_id)
            index += 1

            if index >= len(dialog_list):
                break

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
