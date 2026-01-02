"""Configuration management for the bot."""
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Bot configuration."""
    
    # Telegram configuration
    bot_token: str
    rides_channel_id: int
    discussion_group_id: int
    registration_mode: str
    ride_filter: str
    ride_hashtags: List[str]
    admin_user_ids: List[int]
    
    # Database configuration
    database_path: str
    
    # Logging configuration
    log_level: str
    log_file: str
    
    # Optional configuration
    timezone: str
    vote_cooldown: int
    show_changed_mind_stats: bool
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise ValueError("BOT_TOKEN is required")
        
        rides_channel_id = int(os.getenv("RIDES_CHANNEL_ID", "0"))
        if rides_channel_id == 0:
            raise ValueError("RIDES_CHANNEL_ID is required")
        
        discussion_group_id = int(os.getenv("DISCUSSION_GROUP_ID", "0"))
        
        registration_mode = os.getenv("REGISTRATION_MODE", "edit_channel")
        if registration_mode not in ["edit_channel", "discussion_thread", "channel_reply_post"]:
            raise ValueError(f"Invalid REGISTRATION_MODE: {registration_mode}")
        
        ride_filter = os.getenv("RIDE_FILTER", "hashtag")
        if ride_filter not in ["hashtag", "all"]:
            raise ValueError(f"Invalid RIDE_FILTER: {ride_filter}")
        
        # Parse hashtags (comma-separated)
        ride_hashtags_str = os.getenv("RIDE_HASHTAGS", "#ride")
        ride_hashtags = [tag.strip() for tag in ride_hashtags_str.split(",") if tag.strip()]
        
        # Parse admin user IDs (comma-separated)
        admin_user_ids_str = os.getenv("ADMIN_USER_IDS", "")
        admin_user_ids = [int(uid.strip()) for uid in admin_user_ids_str.split(",") if uid.strip()]
        
        database_path = os.getenv("DATABASE_PATH", "./data/bot.db")
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = os.getenv("LOG_FILE", "./logs/bot.log")
        timezone = os.getenv("TIMEZONE", "UTC")
        vote_cooldown = int(os.getenv("VOTE_COOLDOWN", "1"))
        show_changed_mind_stats = os.getenv("SHOW_CHANGED_MIND_STATS", "true").lower() == "true"
        
        return cls(
            bot_token=bot_token,
            rides_channel_id=rides_channel_id,
            discussion_group_id=discussion_group_id,
            registration_mode=registration_mode,
            ride_filter=ride_filter,
            ride_hashtags=ride_hashtags,
            admin_user_ids=admin_user_ids,
            database_path=database_path,
            log_level=log_level,
            log_file=log_file,
            timezone=timezone,
            vote_cooldown=vote_cooldown,
            show_changed_mind_stats=show_changed_mind_stats,
        )
