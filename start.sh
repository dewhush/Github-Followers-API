#!/bin/bash

# GitHub Followers Bot - Start Script for Ubuntu
# Created by: dewhush

echo "🚀 Starting GitHub Followers Bot..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please copy .env.example to .env and configure it."
    echo "   Run: cp .env.example .env && nano .env"
    exit 1
fi

echo "✅ Environment loaded"
echo "🌾 Starting Telegram Bot..."
echo ""

# Run the bot
python3 main.py
