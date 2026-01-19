# 🚀 Setup Guide untuk Ubuntu Server

Panduan lengkap untuk menjalankan GitHub Followers Bot di Ubuntu Server.

## 📋 Prerequisites

- Ubuntu Server 20.04+ (atau Debian-based distro)
- Python 3.10+
- Git

---

## 🔧 Step 1: Update System & Install Dependencies

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install Python dan pip
sudo apt install python3 python3-pip python3-venv git -y

# Verify installation
python3 --version
pip3 --version
```

---

## 📦 Step 2: Clone Repository

```bash
# Clone dari GitHub (ganti dengan repo URL kamu)
git clone https://github.com/dewhush/Github-Followers-API.git

# Masuk ke direktori project
cd Github-Followers-API
```

---

## 🐍 Step 3: Setup Virtual Environment

```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Pastikan pip up-to-date
pip install --upgrade pip
```

---

## 📥 Step 4: Install Requirements

```bash
pip install -r requirements.txt
```

---

## ⚙️ Step 5: Konfigurasi Environment Variables

```bash
# Copy template environment
cp .env.example .env

# Edit file .env
nano .env
```

**Isi file `.env`:**
```env
# App Configuration
APP_NAME=GitHub-Followers-API
APP_ENV=production
API_KEY=your_secure_api_key_here

# GitHub Credentials (Wajib)
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Telegram Configuration (Wajib untuk Telegram Bot)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=your_chat_id
```

**Cara dapat GITHUB_TOKEN:**
1. Buka https://github.com/settings/tokens
2. Generate new token (classic)
3. Centang: `user:follow`, `read:user`
4. Copy token-nya

**Cara dapat TELEGRAM_BOT_TOKEN:**
1. Chat @BotFather di Telegram
2. Ketik `/newbot` dan ikuti instruksi
3. Copy token yang diberikan

**Cara dapat TELEGRAM_CHAT_ID:**
1. Chat @userinfobot di Telegram
2. Copy ID kamu

---

## 🚀 Step 6: Jalankan Bot

### Option A: Jalankan Langsung (Foreground)
```bash
python3 main.py
```

### Option B: Jalankan dengan Screen (Background)
```bash
# Install screen jika belum ada
sudo apt install screen -y

# Buat session baru
screen -S github-bot

# Jalankan bot
source venv/bin/activate
python3 main.py

# Detach dari screen: tekan Ctrl+A lalu D
# Re-attach: screen -r github-bot
```

### Option C: Jalankan dengan tmux (Background)
```bash
# Install tmux
sudo apt install tmux -y

# Buat session baru
tmux new -s github-bot

# Jalankan bot
source venv/bin/activate
python3 main.py

# Detach dari tmux: tekan Ctrl+B lalu D
# Re-attach: tmux attach -t github-bot
```

---

## 🔄 Step 7: Setup Systemd Service (Auto-start on Boot)

Buat file service:
```bash
sudo nano /etc/systemd/system/github-bot.service
```

**Isi file:**
```ini
[Unit]
Description=GitHub Followers Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Github-Followers-API
Environment="PATH=/home/YOUR_USERNAME/Github-Followers-API/venv/bin"
ExecStart=/home/YOUR_USERNAME/Github-Followers-API/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

> ⚠️ **Ganti `YOUR_USERNAME` dengan username Ubuntu kamu!**

**Enable dan start service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable github-bot

# Start service
sudo systemctl start github-bot

# Cek status
sudo systemctl status github-bot
```

**Perintah berguna:**
```bash
# Stop bot
sudo systemctl stop github-bot

# Restart bot
sudo systemctl restart github-bot

# Lihat logs
sudo journalctl -u github-bot -f
```

---

## 📡 Optional: Setup FastAPI Server

Jika ingin menjalankan API server juga:

```bash
# Jalankan API dengan uvicorn
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000
```

Atau buat service terpisah untuk API.

---

## 🛠️ Troubleshooting

### Error: ModuleNotFoundError
```bash
# Pastikan virtual environment aktif
source venv/bin/activate
pip install -r requirements.txt
```

### Error: Permission denied
```bash
chmod +x main.py
```

### Error: TELEGRAM_BOT_TOKEN not found
```bash
# Pastikan .env sudah dikonfigurasi
cat .env
```

### Melihat Log Bot
```bash
# Log file
tail -f github_autofollow.log

# Systemd logs
sudo journalctl -u github-bot -f --no-pager
```

---

## 📁 Struktur File

```
Github-Followers-API/
├── main.py           # Telegram Bot Handler
├── core.py           # Logika utama bot
├── api.py            # FastAPI endpoints
├── config.json       # Konfigurasi farming
├── .env              # Environment variables (rahasia!)
├── .env.example      # Template environment
├── requirements.txt  # Dependencies
└── venv/             # Virtual environment
```

---

## ✅ Quick Start Script

Buat file `start.sh` untuk memudahkan:

```bash
#!/bin/bash
cd /home/YOUR_USERNAME/Github-Followers-API
source venv/bin/activate
python3 main.py
```

```bash
chmod +x start.sh
./start.sh
```

---

## 🎉 Selesai!

Bot kamu sekarang berjalan di Ubuntu Server. Gunakan Telegram untuk mengontrol:
- `/status` - Lihat status bot
- `/farm` - Mulai farming
- `/clean` - Cleanup following
- `/stop` - Hentikan bot

---

*Created by: dewhush*
