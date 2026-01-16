# GitHub Auto-Follow API

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A powerful, secure, and automated tool to grow your GitHub network organically. Now refactored into a lightweight REST API.

## ✨ Features

- **Auto-Follow Back**: Automatically follows users who follow you.
- **Smart Farming**: Finds and follows active users from trending repos and your network.
- **Auto-Star**: Automatically stars repositories from your network.
- **Scheduled Cleanup**: Unfollows users who don't follow back after a set period.
- **Secure**: All credentials are stored safely in `.env`, not in code.
- **REST API**: Control the bot remotely via simple HTTP endpoints.

## 🚀 Quick Start

### 1. Setup

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Configure Credentials:**
1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Open `.env` and add your keys:
   - `GITHUB_TOKEN`: Generate from [GitHub Settings > Developer settings > PATs](https://github.com/settings/tokens).
   - `TELEGRAM_BOT_TOKEN`: Get from @BotFather (Optional).
   - `TELEGRAM_CHAT_ID`: Your Telegram User ID (Optional).

### 2. Run the API

Double-click `run_api.bat` or run:
```bash
uvicorn api:app --reload
```

The API will start at `http://127.0.0.1:8000`.

### 3. Usage

Visit the interactive documentation at **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.

**Endpoints:**
- `POST /start`: Start the farming background loop.
- `POST /stop`: Stop the farming background loop.
- `GET /status`: Check if the bot is running and view stats.
- `GET /config`: View current configuration limits.

## ⚙️ Configuration

Edit `config.json` to tweak farming behavior:
- `hourly_follow_limit`: Max follows per hour.
- `target_repos`: List of repositories to farm followers from.
- `smart_filtering`: Criteria for who to follow (ratio, bio, etc).

## 🛡️ Security

- **NEVER** commit your `.env` file to GitHub.
- This project uses `.gitignore` to prevent secret leakage.
- If you suspect a leak, revoke your GitHub token immediately.

## 👤 Credits

**Created by: dewhush**  
*Refactored for Security & Performance*

---
*Disclaimer: Use responsibly. GitHub has strict anti-spam policies. Aggressive settings may get your account flagged.*
