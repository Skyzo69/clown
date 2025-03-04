README - Discord Auto Chat Bot

📌 Deskripsi

Skrip ini digunakan untuk mengotomatisasi percakapan di channel Discord menggunakan beberapa akun/token. Skrip membaca skenario dialog dari file dialog.txt, menggunakan token dari token.txt, dan mengirim pesan ke channel yang ditentukan dengan interval waktu acak.

Skrip ini juga mencatat aktivitas ke dalam log (activity.log) dan menampilkan status pengiriman di terminal dengan warna berbeda.


---

📜 Fitur

✅ Menggunakan banyak token untuk bergantian mengirim pesan
✅ Mensimulasikan pengetikan sebelum mengirim pesan
✅ Menghindari rate limit dengan sistem penundaan otomatis
✅ Menampilkan log aktivitas di terminal dan file log
✅ Dapat membalas pesan sebelumnya dalam skenario percakapan
✅ Mendukung pengiriman ganda (double send) oleh satu token


---

📂 Struktur File

📁 Folder Proyek
├── bot.py             # Skrip utama
├── token.txt          # Daftar token (akun) yang digunakan
├── dialog.txt         # Skenario percakapan dalam format JSON
├── activity.log       # Log aktivitas bot (dibuat otomatis)
└── README.md          # Dokumentasi ini


---

⚙️ Cara Penggunaan

1️⃣ Instalasi Dependensi

Pastikan Python terinstal, lalu instal paket yang dibutuhkan:

pip install requests colorama tabulate

2️⃣ Siapkan Token di token.txt

Buka token.txt dan masukkan daftar token dengan format berikut:

nama_token:token:min_interval:max_interval

Contoh:

Akun1:OTg3NjI4MzExNzE2NjQ3NTU4.GvXtZs.abc123xyz:2:5
Akun2:MTIxMTEzOTM4MjU2ODg3NTU4.Gxyz987abc:3:6

nama_token → Nama untuk identifikasi token

token → Token bot akun Discord

min_interval → Waktu tunggu minimum sebelum mengirim pesan berikutnya

max_interval → Waktu tunggu maksimum sebelum mengirim pesan berikutnya


> ⚠️ Catatan:

Token harus valid, jika tidak, bot akan gagal mengirim pesan.

Minimal harus ada 2 token untuk percakapan otomatis.




3️⃣ Siapkan Skenario Percakapan di dialog.txt

File dialog.txt berisi daftar pesan dalam format JSON. Contoh:

[
    {"text": "Halo!", "sender": 0},
    {"text": "Hai juga!", "sender": 1, "reply_to": 0},
    {"text": "Apa kabar?", "sender": 0, "reply_to": 1},
    {"text": "Baik, kamu?", "sender": 1, "reply_to": 2}
]

text → Isi pesan

sender → Indeks token dalam token.txt yang akan mengirim pesan

reply_to → Indeks pesan yang akan dibalas (opsional)

double_send → Jika true, token yang sama bisa mengirim dua pesan berurutan


4️⃣ Jalankan Skrip

Gunakan perintah berikut untuk menjalankan bot:

python bot.py

Kemudian masukkan ID channel Discord dan waktu mulai (dalam menit).


---

📊 Contoh Output Terminal

╭──────────────────────────────────╮
│           Daftar Token           │
├─────────┬────────────┬───────────┤
Nama      Min Interval Max Interval
Akun1     2           5
Akun2     3           6
╰─────────┴────────────┴───────────╯

Masukkan ID channel: 123456789012345678
Masukkan waktu mulai dalam menit (0 untuk langsung mulai): 0
[12:30:15] Memulai percakapan otomatis...
[12:30:20] [Akun1] Pesan dikirim: 'Halo!' (Message ID: 112233445566778899)
[12:30:25] Waktu tunggu 4.32 detik sebelum pesan berikutnya...
[12:30:30] [Akun2] Pesan dikirim: 'Hai juga!' (Message ID: 223344556677889900)
[12:35:10] Percakapan selesai.

Warna Terminal:

✅ Hijau → Berhasil mengirim pesan

⚠️ Kuning → Rate limit (bot akan menunggu)

❌ Merah → Error (skrip langsung berhenti)



---

🛠️ Error Handling

File tidak ditemukan → Skrip akan berhenti jika dialog.txt atau token.txt tidak ada.

Format salah → Jika format token atau JSON salah, skrip akan menampilkan pesan error.

Rate limit (kode 429) → Bot otomatis menunggu sebelum mengirim pesan lagi.

Token invalid (kode 401) → Skrip akan berhenti jika ada token yang salah.



---

🔧 Pengembangan & Kustomisasi

Untuk menambah fitur baru, edit bot.py.

Jika ingin menambah fitur interaksi lain, gunakan API Discord.

Jika ingin mengganti warna terminal, ubah kode di log_message().



---

📞 Kontak

Jika ada masalah atau pertanyaan, hubungi developer bot atau cek dokumentasi Discord API.

> ⚠️ Disclaimer:
Skrip ini hanya untuk keperluan edukasi. Penggunaan yang melanggar aturan Discord dapat menyebabkan banned akun. Gunakan dengan bijak!



