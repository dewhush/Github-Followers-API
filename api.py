from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import asyncio
import logging
from core import GitHubAutoFollowBot
import os
from typing import Optional

# Setup App
app = FastAPI(
    title="GitHub Auto-Follow API",
    description="Secure REST API for GitHub Follower Farming",
    version="1.0.0"
)

# Global State
bot: Optional[GitHubAutoFollowBot] = None
is_running = False
background_task_handle = None

# Models
class StatusResponse(BaseModel):
    status: str
    is_running: bool
    authenticated_as: Optional[str] = None
    stats: dict = {}

class ConfigResponse(BaseModel):
    farming_enabled: bool
    cleanup_enabled: bool
    daily_limits: dict

# ASCII Banner
BANNER = """
   _____ _ _   _           _         _       _ 
  |  __ (_) | | |         | |       | |     | |
  | |  \/_| |_| |__  _   _| |__     | | __ _| |__   ___ 
  | | __| | __| '_ \| | | | '_ \    | |/ _` | '_ \ / __|
  | |_\ \ | |_| | | | |_| | |_) |   | | (_| | |_) |\__ \\
   \____/_|\__|_| |_|\__,_|_.__/    |_|\__,_|_.__/ |___/
                                                        
      ✨ Created by: dewhush ✨
"""

@app.on_event("startup")
async def startup_event():
    print(BANNER)
    global bot
    try:
        # Initialize bot (loads env vars internally)
        bot = GitHubAutoFollowBot()
    except Exception as e:
        print(f"❌ Failed to initialize bot: {e}")

async def farming_loop():
    """Background loop that runs the bot cycles"""
    global is_running
    while is_running:
        if bot:
            bot.run_cycle()
        await asyncio.sleep(300) # Wait 5 minutes between cycles

@app.post("/start")
async def start_farming(background_tasks: BackgroundTasks):
    global is_running
    if is_running:
        return {"message": "Bot is already running"}
    
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized (check logs/env)")

    is_running = True
    background_tasks.add_task(farming_loop)
    return {"message": "✅ Farming started in background"}

@app.post("/stop")
async def stop_farming():
    global is_running
    if not is_running:
        return {"message": "Bot is not running"}
    
    is_running = False
    return {"message": "🛑 Farming stopping (will finish current cycle)"}

@app.get("/status", response_model=StatusResponse)
async def get_status():
    if not bot:
        return StatusResponse(status="Error: Bot not initialized", is_running=False)
        
    return StatusResponse(
        status="Running" if is_running else "Stopped",
        is_running=is_running,
        authenticated_as=bot.user.login if bot.user else None,
        stats={
            "followed_count": len(bot.followed_users),
            "farming_stats": bot.farming_stats
        }
    )

@app.get("/config", response_model=ConfigResponse)
async def get_config():
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized")
        
    return ConfigResponse(
        farming_enabled=bot.config.get('farming', {}).get('enabled', False),
        cleanup_enabled=bot.config.get('cleanup_non_followers', False),
        daily_limits={
            "daily_follow_limit": bot.config.get('farming', {}).get('daily_follow_limit', 100),
            "hourly_follow_limit": bot.config.get('farming', {}).get('hourly_follow_limit', 40)
        }
    )
