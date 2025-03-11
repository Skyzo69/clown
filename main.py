import time
import logging
import requests
import json
import sys
import re
import threading
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from tabulate import tabulate
import pyfiglet

init(autoreset=True)

logging.basicConfig(filename="activity.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def log_message(level, message):
    """Prints a message with color and logs it to a file"""
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

def display_banner():
    """Displays a banner using pyfiglet"""
    banner = pyfiglet.figlet_format("BOT DIALOG")
    print(Fore.CYAN + banner)

def format_time(remaining_seconds):
    """Formats time into hours, minutes, and seconds"""
    formatted_time = str(timedelta(seconds=remaining_seconds))
    return formatted_time

def display_progress_bar(progress, total):
    """Creates a progress bar with a length of 30 characters"""
    bar_length = 30
    filled_length = int(bar_length * progress / total)
    bar = "█" * filled_length + "▒" * (bar_length - filled_length)
    return f"[{bar}]"

def countdown(start_time_minutes):
    total_seconds = start_time_minutes * 60

    if start_time_minutes >= 60:
        hours = start_time_minutes // 60
        minutes = start_time_minutes % 60
        log_message("info", f"\n🕒 Starting in {hours} hours {minutes} minutes...\n")

    while total_seconds > 0:
        time_str = format_time(total_seconds)
        bar = display_progress_bar(total_seconds, start_time_minutes * 60)

        print(Fore.CYAN + f"\r⏳ {bar} {time_str} remaining...", end="", flush=True)

        if total_seconds > 600:  # If more than 10 minutes, update every 5 minutes
            sleep_time = 300
        elif total_seconds > 300:  # If more than 5 minutes, update every 1 minute
            sleep_time = 60
        elif total_seconds > 60:  # If more than 1 minute, update every 30 seconds
            sleep_time = 30
        elif total_seconds > 10:  # If more than 10 seconds, update every 10 seconds
            sleep_time = 10
        else:  # Final 10-second countdown
            for i in range(total_seconds, 0, -1):
                bar = display_progress_bar(i, start_time_minutes * 60)
                print(Fore.RED + f"\r⏳ {bar} {i} seconds remaining... ", end="", flush=True)
                time.sleep(1)
            break

        time.sleep(sleep_time)
        total_seconds -= sleep_time  # Decrease time based on sleep duration

    print(Fore.GREEN + "\n🚀 Starting now!\n")

def validate_token(token_name, token):
    headers = {"Authorization": token}
    try:
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if response.status_code == 200:
            log_message("info", f"✅ Token {token_name} is valid.")
            return True
        else:
            log_message("error", f"❌ Token {token_name} is invalid! (Status Code: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        log_message("error", f"⚠️ Error validating token {token_name}: {e}")
        return False

def typing_indicator(channel_id, token, typing_time):
    headers = {'Authorization': token}
    start_time = time.time()
    
    log_message("info", f"💬 Bot is typing for {typing_time:.2f} seconds...")  # Log hanya sekali
    
    while time.time() - start_time < typing_time:
        try:
            response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/typing", headers=headers)
            if response.status_code not in [200, 204]:
                log_message("warning", f"⚠️ Typing request failed: {response.status_code}")
                break  # Stop kalau gagal
            
            # Hitung waktu tersisa dan sesuaikan interval
            remaining_time = typing_time - (time.time() - start_time)
            sleep_time = min(remaining_time, 5)  # Maksimum 5 detik
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                break  # Kalau waktu habis, stop loop

        except requests.exceptions.RequestException as e:
            log_message("error", f"❗ Error while sending typing indicator: {e}")
            break  # Stop loop kalau error

def send_message(channel_id, token_name, token, message, message_reference=None):
    headers = {'Authorization': token}
    payload = {'content': message}
    if message_reference:
        payload['message_reference'] = {'message_id': message_reference}

    # **Hitung waktu mengetik berdasarkan jumlah kata (lebih fleksibel)**
    word_count = len(message.split())
    typing_time = random.uniform(0.4 * word_count, 0.7 * word_count)

    # **Jalankan typing indicator di thread terpisah**
    thread = threading.Thread(target=typing_indicator, args=(channel_id, token, typing_time))
    thread.start()

    log_message("info", f"⌨️ Typing for {typing_time:.2f} seconds...")

    # **Tunggu sebelum kirim pesan**
    time.sleep(typing_time)

    try:
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", json=payload, headers=headers)

        if response.status_code == 200:
            message_id = response.json().get('id')
            log_message("info", f"📩 [{token_name}] Message sent: '{message}' (Message ID: {message_id})")
            return message_id
        elif response.status_code == 429:
            retry_after = response.json().get("retry_after", 1)
            log_message("warning", f"⚠️ [{token_name}] Rate limit! Waiting {retry_after:.2f} seconds.")
            time.sleep(retry_after)
            return send_message(channel_id, token_name, token, message, message_reference)
        else:
            log_message("error", f"❌ [{token_name}] Failed to send message: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_message("error", f"❗ Error while sending message: {e}")

def display_token_list(tokens):
    header = ["Token Name", "Min Interval (s)", "Max Interval (s)"]
    table = [(name, min_interval, max_interval) for name, _, min_interval, max_interval in tokens]

    print(Fore.CYAN + "\n" + "="*40)
    print(Fore.YELLOW + "           🎛️ TOKEN LIST")
    print(Fore.CYAN + "="*40)
    print(tabulate(table, headers=header, tablefmt="grid"))
    print(Fore.CYAN + "="*40 + "\n")

def main():
    display_banner()

    try:
    with open("dialog.txt", "r", encoding="utf-8") as f:
        dialog_list = json.load(f)
        if not dialog_list:
            raise ValueError("⚠️ dialog.txt file is empty.")

    with open("token.txt", "r") as f:
        tokens = []
        for line in f.readlines():
            parts = line.strip().split(":")
            if len(parts) != 4:
                raise ValueError("⚠️ Incorrect token.txt format! Use: token_name:token:min_interval:max_interval")
            token_name, token, min_interval, max_interval = parts
            tokens.append((token_name, token, int(min_interval), int(max_interval)))

    if len(tokens) < 2:
        raise ValueError("⚠️ Token file must contain at least 2 accounts.")

    reply_templates = load_templates()  # Ini juga harus sejajar dengan blok try

except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
    log_message("error", f"❗ Error: {e}")
    return

         # **Baca template dari file**
        def load_templates(file_path="template.txt"):
            templates = {}
            with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        key = None
        for line in lines:
            line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            key = line[1:-1].lower()
            templates[key] = []
        elif key and line:
            templates[key].append(line)

        return templates

         # **Cari balasan berdasarkan template**
        def get_reply(message):
             for key, responses in reply_templates.items():
        if any(word in message.lower() for word in key.split()):
             return random.choice(responses)
        return None

def handle_message(data, bot_id, channel_id, token, token_name):
    content = data.get("content", "")
    mentions = data.get("mentions", [])
    message_id = data.get("id")

    is_mentioned = any(user["id"] == bot_id for user in mentions)
    is_reply = "referenced_message" in data

    if is_mentioned or is_reply:
        log_message("info", f"🔔 Mention/Reply detected! Processing...")

        # **Ambil balasan dari template**
        reply_text = get_reply(content)

        if reply_text:
            reply_delay = random.uniform(15, 60)  # **Delay khusus untuk reply**
            log_message("info", f"⏳ Waiting {reply_delay:.2f} seconds before replying...")
            time.sleep(reply_delay)

            send_message(channel_id, token_name, token, reply_text, message_reference=message_id)
        else:
            log_message("warning", "❌ No matching template found. Ignoring.")

        # Validate Tokens
        for token_name, token, _, _ in tokens:
            if not validate_token(token_name, token):
                return  

        display_token_list(tokens)

        channel_id = input(Fore.CYAN + "🔢 Enter channel ID: " + Style.RESET_ALL).strip()
        if not channel_id.isdigit():
            raise ValueError("⚠️ Channel ID must be numeric.")

        start_time_minutes = int(input(Fore.CYAN + "⏳ Enter start time in minutes (0 to start immediately): " + Style.RESET_ALL))
        if start_time_minutes < 0:
            raise ValueError("⚠️ Start time cannot be negative.")

        max_delays = int(input(Fore.CYAN + "🔁 Enter how many times to delay: " + Style.RESET_ALL))
        delay_settings = []

        for i in range(max_delays):
            delay_after = int(input(Fore.CYAN + f"🔄 Enter how many messages before delay {i+1}: " + Style.RESET_ALL))
            delay_time = int(input(Fore.CYAN + f"⏳ Enter delay {i+1} time in seconds: " + Style.RESET_ALL))
            delay_settings.append((delay_after, delay_time))

        change_interval = input(Fore.CYAN + "⏳ Change interval after certain delays? (y/n): " + Style.RESET_ALL).strip().lower()
        interval_changes = {}

        if change_interval == "y":
            num_changes = int(input(Fore.CYAN + "🔄 How many interval changes? " + Style.RESET_ALL))
            for _ in range(num_changes):
                after_delay = int(input(Fore.CYAN + "🕒 After which delay number? " + Style.RESET_ALL))
                new_min_interval = int(input(Fore.CYAN + "🕒 Enter new min interval (seconds): " + Style.RESET_ALL))
                new_max_interval = int(input(Fore.CYAN + "🕒 Enter new max interval (seconds): " + Style.RESET_ALL))
                interval_changes[after_delay] = (new_min_interval, new_max_interval)

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        log_message("error", f"❗ Error: {e}")
        return

    if start_time_minutes > 0:
        countdown(start_time_minutes)

    log_message("info", "🤖 Starting automatic conversation...")

    last_message_per_sender = {}
    message_count = 0
    delay_count = 0

    for index, dialog in enumerate(dialog_list):
        try:
            text = dialog["text"]
            sender_index = dialog["sender"]
            reply_to = dialog.get("reply_to", None)

            if sender_index >= len(tokens):
                log_message("error", f"⚠️ Sender index {sender_index} is out of bounds.")
                return

            token_name, token, min_interval, max_interval = tokens[sender_index]
            message_reference = last_message_per_sender.get(reply_to) if reply_to is not None else None

            message_id = send_message(channel_id, token_name, token, text, message_reference)
            if message_id:
                last_message_per_sender[sender_index] = message_id

            custom_delay = dialog.get("delay", None)
            if custom_delay:
                log_message("info", f"⏳ Custom delay json detected: {custom_delay} seconds")
                time.sleep(custom_delay)
                log_message("info", "⏳ Resuming after custom delay...")
                continue  
                
            wait_time = random.uniform(min_interval, max_interval)
            log_message("info", f"⏳ Waiting {wait_time:.2f} seconds before the next message...")
            time.sleep(wait_time)

            message_count += 1

            if delay_count < max_delays and delay_count < len(delay_settings) and message_count >= delay_settings[delay_count][0]:
                log_message("info", f"⏸️ Pausing for {delay_settings[delay_count][1]} seconds... ({delay_count + 1}/{max_delays})")
                time.sleep(delay_settings[delay_count][1])
                delay_count += 1

            if delay_count in interval_changes:
                new_min_interval, new_max_interval = interval_changes[delay_count]
                tokens[sender_index] = (token_name, token, new_min_interval, new_max_interval)
                log_message("info", f"⏳ Interval changed to {new_min_interval}-{new_max_interval} seconds after delay {delay_count}/{max_delays}")

        except Exception as e:
            log_message("error", f"❗ An error occurred: {e}")
            return

    log_message("info", "🎉 Conversation completed.")

if __name__ == "__main__":
    main()
