"""Configuration management for the bot."""
import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

from app.exceptions import ConfigurationError

load_dotenv()


@dataclass
class Config:
    """Bot configuration."""
    
    # Telegram configuration
    bot_token: str
    rides_channel_id: int
    discussion_group_id: Optional[int]
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
    
    # Valid values for validation
    VALID_REGISTRATION_MODES = {"edit_channel", "discussion_thread", "channel_reply_post"}
    VALID_RIDE_FILTERS = {"hashtag", "all"}
    VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate configuration values."""
        # Validate registration mode
        if self.registration_mode not in self.VALID_REGISTRATION_MODES:
            raise ConfigurationError(
                f"Invalid REGISTRATION_MODE: {self.registration_mode}. "
                f"Valid options: {', '.join(self.VALID_REGISTRATION_MODES)}"
            )
        
        # Validate ride filter
        if self.ride_filter not in self.VALID_RIDE_FILTERS:
            raise ConfigurationError(
                f"Invalid RIDE_FILTER: {self.ride_filter}. "
                f"Valid options: {', '.join(self.VALID_RIDE_FILTERS)}"
            )
        
        # Validate log level
        if self.log_level not in self.VALID_LOG_LEVELS:
            raise ConfigurationError(
                f"Invalid LOG_LEVEL: {self.log_level}. "
                f"Valid options: {', '.join(self.VALID_LOG_LEVELS)}"
            )
        
        # Validate vote cooldown
        if self.vote_cooldown < 0:
            raise ConfigurationError(
                f"VOTE_COOLDOWN must be non-negative, got: {self.vote_cooldown}"
            )
        
        # Validate hashtags if filter is set to hashtag
        if self.ride_filter == "hashtag" and not self.ride_hashtags:
            raise ConfigurationError(
                "RIDE_HASHTAGS must be provided when RIDE_FILTER is 'hashtag'"
            )
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise ConfigurationError("BOT_TOKEN is required")
        
        rides_channel_id_str = os.getenv("RIDES_CHANNEL_ID", "0")
        try:
            rides_channel_id = int(rides_channel_id_str)
        except ValueError:
            raise ConfigurationError(f"RIDES_CHANNEL_ID must be an integer, got: {rides_channel_id_str}")
        
        if rides_channel_id == 0:
            raise ConfigurationError("RIDES_CHANNEL_ID is required")
        
        discussion_group_id_str = os.getenv("DISCUSSION_GROUP_ID", "0")
        try:
            discussion_group_id = int(discussion_group_id_str)
        except ValueError:
            raise ConfigurationError(f"DISCUSSION_GROUP_ID must be an integer, got: {discussion_group_id_str}")
        
        discussion_group_id = discussion_group_id if discussion_group_id != 0 else None
        
        registration_mode = os.getenv("REGISTRATION_MODE", "edit_channel")
        ride_filter = os.getenv("RIDE_FILTER", "hashtag")
        
        # Parse hashtags (comma-separated)
        ride_hashtags_str = os.getenv("RIDE_HASHTAGS", "#ride")
        ride_hashtags = [tag.strip() for tag in ride_hashtags_str.split(",") if tag.strip()]
        
        # Parse admin user IDs (comma-separated)
        admin_user_ids_str = os.getenv("ADMIN_USER_IDS", "")
        admin_user_ids = []
        if admin_user_ids_str:
            try:
                admin_user_ids = [int(uid.strip()) for uid in admin_user_ids_str.split(",") if uid.strip()]
            except ValueError as e:
                raise ConfigurationError(f"ADMIN_USER_IDS must be comma-separated integers: {e}")
        
        database_path = os.getenv("DATABASE_PATH", "./data/bot.db")
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_file = os.getenv("LOG_FILE", "./logs/bot.log")
        timezone = os.getenv("TIMEZONE", "UTC")
        
        vote_cooldown_str = os.getenv("VOTE_COOLDOWN", "1")
        try:
            vote_cooldown = int(vote_cooldown_str)
        except ValueError:
            raise ConfigurationError(f"VOTE_COOLDOWN must be an integer, got: {vote_cooldown_str}")
        
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
