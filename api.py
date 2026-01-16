"""
GitHub Followers API
A secure REST API for GitHub Auto-Follow Bot

Created by: dewhush
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv

from core import GitHubFollowerBot

# Load environment variables
load_dotenv()

# Configuration
APP_NAME = os.getenv("APP_NAME", "GitHub-Followers-API")
APP_ENV = os.getenv("APP_ENV", "development")
API_KEY = os.getenv("API_KEY", "")

# Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key from header"""
    if not API_KEY:
        return True  # Skip auth if no API_KEY configured
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key"
        )
    return True

# Setup App
app = FastAPI(
    title=APP_NAME,
    description="🚀 Secure REST API for GitHub Follower Farming & Management",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global State
bot: Optional[GitHubFollowerBot] = None
is_running = False

# Response Models
class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str

class StatusResponse(BaseModel):
    status: str
    is_running: bool
    authenticated_as: Optional[str] = None
    stats: dict = {}

class ConfigResponse(BaseModel):
    farming_enabled: bool
    cleanup_enabled: bool
    daily_limits: dict

class MessageResponse(BaseModel):
    message: str
    success: bool = True

# ASCII Banner
BANNER = """
   _____ _ _   _           _       ______    _ _                            
  / ____(_) | | |         | |     |  ____|  | | |                           
 | |  __ _| |_| |__  _   _| |__   | |__ ___ | | | _____      _____ _ __ ___ 
 | | |_ | | __| '_ \\| | | | '_ \\  |  __/ _ \\| | |/ _ \\ \\ /\\ / / _ \\ '__/ __|
 | |__| | | |_| | | | |_| | |_) | | | | (_) | | | (_) \\ V  V /  __/ |  \\__ \\
  \\_____|_|\\__|_| |_|\\__,_|_.__/  |_|  \\___/|_|_|\\___/ \\_/\\_/ \\___|_|  |___/
                                                                            
                    ✨ Created by: dewhush ✨
"""

@app.on_event("startup")
async def startup_event():
    """Initialize bot on startup"""
    print(BANNER)
    print(f"  📦 App: {APP_NAME}")
    print(f"  🌍 Environment: {APP_ENV}")
    print(f"  🔐 API Key Protection: {'Enabled' if API_KEY else 'Disabled'}")
    print()
    
    global bot
    try:
        bot = GitHubFollowerBot()
        logging.info(f"✅ Bot initialized successfully")
    except Exception as e:
        logging.error(f"❌ Failed to initialize bot: {e}")

# ============== Public Endpoints ==============

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        app_name=APP_NAME,
        environment=APP_ENV
    )

@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status():
    """Get current bot status and statistics"""
    if not bot:
        return StatusResponse(
            status="Error: Bot not initialized",
            is_running=False
        )
    
    return StatusResponse(
        status="Running" if is_running else "Stopped",
        is_running=is_running,
        authenticated_as=bot.user.login if bot.user else None,
        stats={
            "followed_count": len(bot.followed_users),
            "farming_stats": bot.farming_stats
        }
    )

# ============== Protected Endpoints (v1) ==============

@app.get("/v1/config", response_model=ConfigResponse, tags=["Configuration"], dependencies=[Depends(verify_api_key)])
async def get_config():
    """View current bot configuration"""
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

# Background task for farming loop
async def farming_loop():
    """Background loop that runs the bot cycles"""
    global is_running
    while is_running:
        if bot:
            bot.run_cycle()
        await asyncio.sleep(300)  # Wait 5 minutes between cycles

@app.post("/v1/start", response_model=MessageResponse, tags=["Bot Control"], dependencies=[Depends(verify_api_key)])
async def start_farming(background_tasks: BackgroundTasks):
    """Start the farming background loop"""
    global is_running
    
    if is_running:
        return MessageResponse(message="Bot is already running", success=False)
    
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized (check logs/env)")
    
    is_running = True
    background_tasks.add_task(farming_loop)
    return MessageResponse(message="✅ Farming started in background")

@app.post("/v1/stop", response_model=MessageResponse, tags=["Bot Control"], dependencies=[Depends(verify_api_key)])
async def stop_farming():
    """Stop the farming background loop"""
    global is_running
    
    if not is_running:
        return MessageResponse(message="Bot is not running", success=False)
    
    is_running = False
    return MessageResponse(message="🛑 Farming stopping (will finish current cycle)")

@app.post("/v1/follow-back", response_model=MessageResponse, tags=["Actions"], dependencies=[Depends(verify_api_key)])
async def trigger_follow_back():
    """Manually trigger follow-back check"""
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        bot.check_and_follow_back()
        return MessageResponse(message="✅ Follow-back check completed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/cleanup", response_model=MessageResponse, tags=["Actions"], dependencies=[Depends(verify_api_key)])
async def trigger_cleanup():
    """Manually trigger cleanup of non-followers"""
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        bot.cleanup_non_followers()
        return MessageResponse(message="✅ Cleanup completed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/farm", response_model=MessageResponse, tags=["Actions"], dependencies=[Depends(verify_api_key)])
async def trigger_farm():
    """Manually trigger one farming cycle"""
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        bot.farm_followers()
        return MessageResponse(message="✅ Farming cycle completed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
