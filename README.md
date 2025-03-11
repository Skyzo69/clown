# 🎉 BOT DIALOG 🎉
*A simple Discord bot to automate conversations with predefined dialogs, dynamic replies, and manual message cancellation support. 🚀*

---

## 📋 Prerequisites
- 🐍 **Python 3.8+**
- 📦 Install dependencies:
  ```bash
  pip install -r requirements.txt
  
## 📂 Setup Files
### 1. 🔑 token.txt
   
   📏 Format: token_name:token:min_interval:max_interval (one per line)
    📝 Example:
   
           Token1:your_discord_token1:5:10
           Token2:your_discord_token2:5:10
   
   ℹ️ Notes:
   ✅ Minimum 2 tokens required
   ⏱️ Intervals are in seconds
   
### 2. 📝 template.txt
   
   📏 Format: [keyword1|keyword2] followed by response lines
   📝 Example:

    [halo|hi]
    Halo bro, kabarku baik!
    [apa kabar]
    Kabar baik, kamu gimana?
5. 💬 dialog.txt
📏 Format: JSON array of dialog objects
📋 Fields:
✍️ text: Message content
👤 sender: Index of token (0-based)
↩️ reply_to (optional): Index of previous sender to reply to
⏳ delay (optional): Custom delay in seconds
📝 Example:
json
[
  {"text": "Halo semua!", "sender": 0},
  {"text": "Apa kabar?", "sender": 1, "reply_to": 0, "delay": 10}
]
🚀 Step-by-Step Usage
📑 Prepare Files
📝 Create token.txt, dialog.txt, and template.txt as described above
▶️ Run the Script
💻 Execute the following command:
bash
python main.py
❓ Follow Prompts
📡 Enter the channel ID (e.g., 123456789)
⏰ Set the start time in minutes (e.g., 0 for immediate start)
🔢 Specify the number of delays (e.g., 1)
⏳ Input delay details (e.g., 2 messages, 30 seconds)
⚙️ Choose whether to change intervals after delays (e.g., y/n)
👀 Monitor Terminal
📢 The script runs automated dialogs from dialog.txt
🔍 It polls messages and responds based on template.txt
🚫 Manual messages cancel pending auto-replies instantly
✨ Features
✔️ Automated dialogs with delays and replies
✔️ Dynamic responses to mentions/replies using templates
✔️ Manual messages stop auto-replies without delay
✔️ Logging to activity.log
⚠️ Notes
⚠️ Ensure tokens are valid Discord bot/user tokens
⚠️ Manual messages must be sent outside dialog.txt to cancel auto-replies
⚠️ Replies to others follow template rules and don’t cancel subsequent auto-messages
🔧 Perbaikan yang Dilakukan
📏 Indentasi Konsisten: Semua pake spasi (2 atau 4 spasi per level), ga ada tab
📋 Baris Rapi: Tiap poin punya spasi sama, ga ada baris kosong berlebih
🎨 Format Pas: Kode blok dan daftar dibuat rapi sesuai Markdown
🎉 Tambah Emoji: Ditambahin emoji biar lebih seru dan gampang dilihat

---

### Cara Salin
1. Buka GitHub, masuk ke repo `Skyzo69/Di`.
2. Klik file `README.md`, lalu klik **Edit** (icon pensil).
3. Hapus isi lama, lalu salin semua teks di atas (dari `# 🎉 BOT DIALOG 🎉` sampe akhir).
4. Tempel di editor GitHub, isi deskripsi commit (misal: "Update README with emojis and formatting"), lalu klik **Commit changes**.
5. Cek hasilnya, seharusnya udah rapi dengan emoji!

### Catatan
- Scriptnya tetep pake `main.py` ya bro, pastiin namanya sesuai.
- Emoji dipilih biar relevan sama konteks (misal 🚀 buat usage, ✔️ buat fitur).
- Kalo ada yang mau ditambah atau diubah lagi, kasih tahu aku!

Semoga suka bro, mbooott! 😄
