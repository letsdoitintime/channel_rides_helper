"""Configuration management for the bot."""
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from app.exceptions import ConfigurationError
from app.translations import Language

load_dotenv()


@dataclass
class ButtonConfig:
    """Configuration for registration buttons."""
    
    # Button visibility
    show_join: bool = True
    show_maybe: bool = True
    show_decline: bool = True
    show_voters: bool = True
    show_refresh: bool = True
    
    # Custom button names (if None, uses translation)
    custom_join_text: Optional[str] = None
    custom_maybe_text: Optional[str] = None
    custom_decline_text: Optional[str] = None
    custom_voters_text: Optional[str] = None
    custom_refresh_text: Optional[str] = None
    
    # Additional buttons (format: {"text": "Button Text", "url": "https://..."})
    additional_buttons: List[Dict[str, str]] = field(default_factory=list)
    
    # Voter access control
    require_vote_to_see_voters: bool = False
    
    def __post_init__(self):
        """Validate button configuration."""
        # At least one vote button must be visible
        if not (self.show_join or self.show_maybe or self.show_decline):
            raise ConfigurationError("At least one vote button (join, maybe, decline) must be visible")


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
    
    # Button configuration
    button_config: ButtonConfig = field(default_factory=ButtonConfig)
    language: Language = "en"
    
    # Valid values for validation
    VALID_REGISTRATION_MODES = {"edit_channel", "discussion_thread", "channel_reply_post"}
    VALID_RIDE_FILTERS = {"hashtag", "all"}
    VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    VALID_LANGUAGES = {"en", "ua"}
    
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
        
        # Validate language
        if self.language not in self.VALID_LANGUAGES:
            raise ConfigurationError(
                f"Invalid LANGUAGE: {self.language}. "
                f"Valid options: {', '.join(self.VALID_LANGUAGES)}"
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
        
        # Parse language
        language = os.getenv("LANGUAGE", "en").lower()
        
        # Parse button configuration
        button_config = ButtonConfig(
            show_join=os.getenv("BUTTON_SHOW_JOIN", "true").lower() == "true",
            show_maybe=os.getenv("BUTTON_SHOW_MAYBE", "true").lower() == "true",
            show_decline=os.getenv("BUTTON_SHOW_DECLINE", "true").lower() == "true",
            show_voters=os.getenv("BUTTON_SHOW_VOTERS", "true").lower() == "true",
            show_refresh=os.getenv("BUTTON_SHOW_REFRESH", "true").lower() == "true",
            custom_join_text=os.getenv("BUTTON_CUSTOM_JOIN_TEXT") or None,
            custom_maybe_text=os.getenv("BUTTON_CUSTOM_MAYBE_TEXT") or None,
            custom_decline_text=os.getenv("BUTTON_CUSTOM_DECLINE_TEXT") or None,
            custom_voters_text=os.getenv("BUTTON_CUSTOM_VOTERS_TEXT") or None,
            custom_refresh_text=os.getenv("BUTTON_CUSTOM_REFRESH_TEXT") or None,
            additional_buttons=cls._parse_additional_buttons(os.getenv("BUTTON_ADDITIONAL", "")),
            require_vote_to_see_voters=os.getenv("BUTTON_REQUIRE_VOTE_FOR_VOTERS", "false").lower() == "true",
        )
        
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
            button_config=button_config,
            language=language,
        )
    
    @staticmethod
    def _parse_additional_buttons(buttons_str: str) -> List[Dict[str, str]]:
        """Parse additional buttons from environment variable.
        
        Format: "Button1|https://example.com,Button2|https://example2.com"
        """
        buttons = []
        if not buttons_str:
            return buttons
        
        for button_def in buttons_str.split(","):
            button_def = button_def.strip()
            if not button_def:
                continue
            
            parts = button_def.split("|")
            if len(parts) != 2:
                raise ConfigurationError(
                    f"Invalid additional button format: {button_def}. "
                    "Expected format: 'Button Text|https://url'"
                )
            
            text, url = parts
            buttons.append({"text": text.strip(), "url": url.strip()})
        
        return buttons
