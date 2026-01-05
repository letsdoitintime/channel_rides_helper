"""Tests for configuration."""
import pytest
import os

from app.config import Config
from app.exceptions import ConfigurationError


def test_config_from_env():
    """Test configuration loading from environment."""
    os.environ["BOT_TOKEN"] = "test_token"
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    os.environ["DISCUSSION_GROUP_ID"] = "-1009876543210"
    os.environ["REGISTRATION_MODE"] = "discussion_thread"
    os.environ["RIDE_FILTER"] = "all"
    os.environ["RIDE_HASHTAGS"] = "#ride,#test,#велопокатушка"
    os.environ["ADMIN_USER_IDS"] = "123,456,789"
    
    config = Config.from_env()
    
    assert config.bot_token == "test_token"
    assert config.rides_channel_id == -1001234567890
    assert config.discussion_group_id == -1009876543210
    assert config.registration_mode == "discussion_thread"
    assert config.ride_filter == "all"
    assert config.ride_hashtags == ["#ride", "#test", "#велопокатушка"]
    assert config.admin_user_ids == [123, 456, 789]


def test_config_defaults():
    """Test configuration defaults."""
    os.environ["BOT_TOKEN"] = "test_token"
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    # Don't set optional values
    
    config = Config.from_env()
    
    assert config.database_path == "./data/bot.db"
    assert config.log_level == "INFO"
    assert config.timezone == "UTC"
    assert config.vote_cooldown == 1
    assert config.show_changed_mind_stats is True


def test_config_invalid_mode():
    """Test invalid registration mode."""
    os.environ["BOT_TOKEN"] = "test_token"
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    os.environ["REGISTRATION_MODE"] = "invalid_mode"
    
    with pytest.raises(ConfigurationError, match="Invalid REGISTRATION_MODE"):
        Config.from_env()


def test_config_invalid_filter():
    """Test invalid ride filter."""
    os.environ["BOT_TOKEN"] = "test_token"
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    os.environ["REGISTRATION_MODE"] = "edit_channel"  # Set valid mode first
    os.environ["RIDE_FILTER"] = "invalid_filter"
    
    with pytest.raises(ConfigurationError, match="Invalid RIDE_FILTER"):
        Config.from_env()


def test_config_missing_token():
    """Test missing bot token."""
    if "BOT_TOKEN" in os.environ:
        del os.environ["BOT_TOKEN"]
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    
    with pytest.raises(ConfigurationError, match="BOT_TOKEN is required"):
        Config.from_env()


def test_config_missing_channel_id():
    """Test missing channel ID."""
    os.environ["BOT_TOKEN"] = "test_token"
    if "RIDES_CHANNEL_ID" in os.environ:
        del os.environ["RIDES_CHANNEL_ID"]
    
    with pytest.raises(ConfigurationError, match="RIDES_CHANNEL_ID is required"):
        Config.from_env()


def test_config_invalid_log_level():
    """Test invalid log level."""
    os.environ["BOT_TOKEN"] = "test_token"
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    os.environ["REGISTRATION_MODE"] = "edit_channel"
    os.environ["RIDE_FILTER"] = "all"
    os.environ["LOG_LEVEL"] = "INVALID"
    
    with pytest.raises(ConfigurationError, match="Invalid LOG_LEVEL"):
        Config.from_env()


def test_config_negative_vote_cooldown():
    """Test negative vote cooldown."""
    os.environ["BOT_TOKEN"] = "test_token"
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    os.environ["REGISTRATION_MODE"] = "edit_channel"
    os.environ["RIDE_FILTER"] = "all"
    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["VOTE_COOLDOWN"] = "-1"
    
    with pytest.raises(ConfigurationError, match="VOTE_COOLDOWN must be non-negative"):
        Config.from_env()


def test_config_hashtag_filter_without_hashtags():
    """Test hashtag filter without hashtags."""
    os.environ["BOT_TOKEN"] = "test_token"
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    os.environ["REGISTRATION_MODE"] = "edit_channel"
    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["VOTE_COOLDOWN"] = "1"
    os.environ["RIDE_FILTER"] = "hashtag"
    os.environ["RIDE_HASHTAGS"] = ""
    
    with pytest.raises(ConfigurationError, match="RIDE_HASHTAGS must be provided"):
        Config.from_env()
