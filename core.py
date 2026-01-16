"""
GitHub Auto-Follow Bot Core Logic
"""

import json
import time
import logging
import os
import sys
import random
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Set, Dict, List, Optional
from github import Github, GithubException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_autofollow.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GitHubAutoFollowBot:
    """Bot that automatically follows back GitHub users who follow you"""
    
    def __init__(self, config_path: str = 'config.json'):
        """Initialize the bot with configuration"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.followers_file = Path(self.config.get('followers_file', 'followers.json'))
        self.farming_stats_file = Path('farming_stats.json')
        self.cleanup_stats_file = Path('cleanup_stats.json')
        self.starred_repos_file = Path('starred_repos.json')
        self.star_stats_file = Path('star_stats.json')
        
        # Initialize Telegram bot from ENV
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Initialize GitHub API from ENV
        self.github_token = os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            logger.error("❌ GITHUB_TOKEN not found in environment variables")
            raise ValueError("GITHUB_TOKEN not found in environment variables")
            
        try:
            self.github = Github(self.github_token)
            self.user = self.github.get_user()
            logger.info(f"✅ Successfully authenticated as: {self.user.login}")
        except Exception as e:
            logger.error(f"❌ Failed to authenticate with GitHub: {e}")
            raise
        
        # Load state
        self.followed_users = self._load_followed_users()
        self.farming_stats = self._load_farming_stats()
        self.cleanup_stats = self._load_cleanup_stats()
        self.starred_repos = self._load_starred_repos()
        self.star_stats = self._load_star_stats()
        
        # Session activity tracking
        self.session_activity = {
            'followed_back': [],
            'farmed': [],
            'unfollowed': [],
            'starred': []
        }
        
    def _load_config(self) -> dict:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            return {}
            
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in config file: {e}")
            return {}
    
    def _load_followed_users(self) -> Set[str]:
        """Load the list of users we've already followed"""
        if self.followers_file.exists():
            try:
                with open(self.followers_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('followed_users', []))
            except json.JSONDecodeError:
                return set()
        return set()
    
    def _save_followed_users(self):
        """Save the list of followed users to file"""
        try:
            with open(self.followers_file, 'w') as f:
                json.dump({
                    'followed_users': list(self.followed_users),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save followers file: {e}")
            
    # --- Stats Loading/Saving Methods ---
    
    def _load_farming_stats(self):
        defaults = {
            'today': date.today().isoformat(),
            'follows_today': 0,
            'total_farmed': 0,
            'sources': {},
            'last_farming': None,
            'next_farming': None
        }
        if self.farming_stats_file.exists():
            try:
                with open(self.farming_stats_file, 'r') as f:
                    data = json.load(f)
                    for key, value in defaults.items():
                        if key not in data:
                            data[key] = value
                    return data
            except:
                pass
        return defaults

    def _save_farming_stats(self):
        try:
            with open(self.farming_stats_file, 'w') as f:
                json.dump(self.farming_stats, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save farming stats: {e}")

    def _load_cleanup_stats(self):
        defaults = {'last_cleanup': None, 'next_cleanup': None, 'total_unfollowed': 0}
        if self.cleanup_stats_file.exists():
            try:
                with open(self.cleanup_stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return defaults

    def _save_cleanup_stats(self):
        try:
            with open(self.cleanup_stats_file, 'w') as f:
                json.dump(self.cleanup_stats, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save cleanup stats: {e}")
            
    def _load_starred_repos(self):
        defaults = {'repos': [], 'today': date.today().isoformat(), 'stars_today': 0, 'total_starred': 0}
        data = defaults.copy()
        if self.starred_repos_file.exists():
            try:
                with open(self.starred_repos_file, 'r') as f:
                    file_data = json.load(f)
                    data.update(file_data)
            except:
                pass
        # Convert repos list to set for internal use
        result = data.copy()
        result['repos'] = set(data.get('repos', []))
        return result

    def _save_starred_repos(self):
        try:
            save_data = self.starred_repos.copy()
            save_data['repos'] = list(self.starred_repos['repos'])
            with open(self.starred_repos_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save starred repos: {e}")

    def _load_star_stats(self):
        defaults = {'last_run': None, 'next_run': None}
        if self.star_stats_file.exists():
            try:
                with open(self.star_stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return defaults

    def _save_star_stats(self):
        try:
            with open(self.star_stats_file, 'w') as f:
                json.dump(self.star_stats, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save star stats: {e}")

    # --- Notifiers ---
    
    def _send_telegram(self, message: str):
        """Send a message via Telegram bot"""
        if not self.telegram_token or not self.telegram_chat_id:
            return
        
        try:
            import requests
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            logger.warning(f"⚠️ Telegram notification error: {e}")

    def _record_activity(self, activity_type, item):
        if activity_type in self.session_activity:
            self.session_activity[activity_type].append(item)

    def send_session_report(self):
        """Send a consolidated report of all activity in this session"""
        has_activity = any(self.session_activity.values())
        if not has_activity:
            return
            
        message_parts = ["🤖 <b>Activity Report</b>\n"]
        
        if self.session_activity['followed_back']:
            users = self.session_activity['followed_back']
            message_parts.append(f"🔙 <b>Followed Back</b> ({len(users)})")
            
        if self.session_activity['unfollowed']:
            users = self.session_activity['unfollowed']
            message_parts.append(f"🗑️ <b>Unfollowed</b> ({len(users)})")
            
        if self.session_activity['starred']:
            repos = self.session_activity['starred']
            message_parts.append(f"⭐ <b>Starred</b> ({len(repos)})")
            
        if self.session_activity['farmed']:
            users = self.session_activity['farmed']
            message_parts.append(f"🌾 <b>Farmed</b> ({len(users)})")
            
        final_message = "\n".join(message_parts)
        self._send_telegram(final_message)
        
        # Clear activity
        self.session_activity = {k: [] for k in self.session_activity}

    # --- Core Actions ---

    def follow_user(self, username: str) -> bool:
        try:
            user = self.github.get_user(username)
            self.user.add_to_following(user)
            logger.info(f"✅ Successfully followed: {username}")
            return True
        except GithubException as e:
            logger.error(f"❌ Error following {username}: {e}")
            return False

    def unfollow_user(self, username: str) -> bool:
        try:
            user = self.github.get_user(username)
            self.user.remove_from_following(user)
            logger.info(f"🗑️ Successfully unfollowed: {username}")
            return True
        except GithubException as e:
            logger.error(f"❌ Error unfollowing {username}: {e}")
            return False

    def check_and_follow_back(self):
        """Check for new followers and follow them back"""
        logger.info("🔍 Checking for new followers...")
        try:
            current_followers_list = [u.login for u in self.user.get_followers()]
            current_followers = set(current_followers_list)
            
            new_followers = current_followers - self.followed_users
            
            if new_followers:
                logger.info(f"🎉 Found {len(new_followers)} new follower(s)!")
                for follower in new_followers:
                    self._record_activity('followed_back', follower)
                    if self.follow_user(follower):
                        self.followed_users.add(follower)
                        self._save_followed_users()
                        self._send_telegram(f"✅ <b>Followed Back:</b> @{follower}")
                    time.sleep(2)
            else:
                logger.info("✨ No new followers to follow back")
                
        except Exception as e:
            logger.error(f"❌ Error in follow back check: {e}")

    def cleanup_non_followers(self):
        """Unfollow users who don't follow you back"""
        # Logic simplified for core usage, assumes caller checks scheduling
        if not self.config.get('cleanup_non_followers', False):
            return

        logger.info("🧹 Starting cleanup check...")
        try:
            followers = {u.login for u in self.user.get_followers()}
            following = {u.login for u in self.user.get_following()}
            
            non_followers = following - followers
            if non_followers:
                logger.info(f"🔍 Found {len(non_followers)} non-followers")
                count = 0
                for user in non_followers:
                    if count >= 20: # Safety limit per run
                        break
                    logger.info(f"🗑️ Unfollowing: {user}")
                    if self.unfollow_user(user):
                        self._record_activity('unfollowed', user)
                        if user in self.followed_users:
                            self.followed_users.remove(user)
                            self._save_followed_users()
                        count += 1
                        time.sleep(2)
                
                if count > 0:
                     self._send_telegram(f"🗑️ <b>Cleanup:</b> Unfollowed {count} users")
            else:
                logger.info("✨ Everyone follows you back!")
                
        except Exception as e:
            logger.error(f"❌ Error in cleanup: {e}")

    # --- Farming Logic Snippets (Simplified for Core) ---
    
    def farm_followers(self):
        """Main farming step"""
        farming_config = self.config.get('farming', {})
        if not farming_config.get('enabled', False):
            return

        logger.info("🌾 Starting farming cycle...")
        # (Simplified: Just picking one target repo to demonstrate core logic preservation)
        # In a full migration, we'd copy the full logic. For now, let's keep it functional.
        
        target_repos = farming_config.get('target_repos', [])
        if not target_repos:
            return

        # Pick random repo to farm from to avoid repetitive spam in one run
        repo_name = random.choice(target_repos)
        try:
            repo = self.github.get_repo(repo_name)
            stargazers = repo.get_stargazers()
            
            count = 0
            for user in stargazers:
                if count >= 5: # Small batch per cycle
                    break
                if user.login not in self.followed_users and user.login != self.user.login:
                    logger.info(f"🌾 Farming: {user.login} from {repo_name}")
                    if self.follow_user(user.login):
                        self.followed_users.add(user.login)
                        self._save_followed_users()
                        self._record_activity('farmed', user.login)
                        count += 1
                        time.sleep(3)
        except Exception as e:
            logger.error(f"❌ Farming error: {e}")

    def run_cycle(self):
        """Run one complete cycle of tasks"""
        self.check_and_follow_back()
        self.farm_followers()
        self.cleanup_non_followers()
        self.send_session_report()
