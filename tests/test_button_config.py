"""Tests for button configuration and translations."""
import os
import pytest
from app.config import Config, ButtonConfig
from app.translations import get_translations, EN_BUTTONS, UA_BUTTONS
from app.exceptions import ConfigurationError


def test_button_config_defaults():
    """Test default button configuration."""
    config = ButtonConfig()
    
    assert config.show_join is True
    assert config.show_maybe is True
    assert config.show_decline is True
    assert config.show_voters is True
    assert config.show_refresh is True
    assert config.require_vote_to_see_voters is False
    assert config.custom_join_text is None
    assert config.additional_buttons == []


def test_button_config_at_least_one_vote_button():
    """Test that at least one vote button must be visible."""
    with pytest.raises(ConfigurationError) as exc_info:
        ButtonConfig(show_join=False, show_maybe=False, show_decline=False)
    
    assert "at least one vote button" in str(exc_info.value).lower()


def test_button_config_custom_texts():
    """Test custom button text configuration."""
    config = ButtonConfig(
        custom_join_text="Custom Join",
        custom_maybe_text="Custom Maybe",
        custom_decline_text="Custom Decline",
    )
    
    assert config.custom_join_text == "Custom Join"
    assert config.custom_maybe_text == "Custom Maybe"
    assert config.custom_decline_text == "Custom Decline"


def test_button_config_additional_buttons():
    """Test additional buttons configuration."""
    additional = [
        {"text": "Rules", "url": "https://example.com/rules"},
        {"text": "Map", "url": "https://example.com/map"},
    ]
    config = ButtonConfig(additional_buttons=additional)
    
    assert len(config.additional_buttons) == 2
    assert config.additional_buttons[0]["text"] == "Rules"
    assert config.additional_buttons[1]["url"] == "https://example.com/map"


def test_config_with_button_config(monkeypatch):
    """Test Config with button configuration."""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("RIDES_CHANNEL_ID", "-1001234567890")
    monkeypatch.setenv("BUTTON_SHOW_REFRESH", "false")
    monkeypatch.setenv("BUTTON_CUSTOM_JOIN_TEXT", "I'm Coming!")
    monkeypatch.setenv("BUTTON_REQUIRE_VOTE_FOR_VOTERS", "true")
    
    config = Config.from_env()
    
    assert config.button_config.show_refresh is False
    assert config.button_config.custom_join_text == "I'm Coming!"
    assert config.button_config.require_vote_to_see_voters is True


def test_config_parse_additional_buttons(monkeypatch):
    """Test parsing additional buttons from environment."""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("RIDES_CHANNEL_ID", "-1001234567890")
    monkeypatch.setenv("BUTTON_ADDITIONAL", "Rules|https://example.com/rules,Map|https://example.com/map")
    
    config = Config.from_env()
    
    assert len(config.button_config.additional_buttons) == 2
    assert config.button_config.additional_buttons[0]["text"] == "Rules"
    assert config.button_config.additional_buttons[0]["url"] == "https://example.com/rules"
    assert config.button_config.additional_buttons[1]["text"] == "Map"
    assert config.button_config.additional_buttons[1]["url"] == "https://example.com/map"


def test_config_invalid_additional_button_format(monkeypatch):
    """Test invalid additional button format raises error."""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("RIDES_CHANNEL_ID", "-1001234567890")
    monkeypatch.setenv("BUTTON_ADDITIONAL", "InvalidFormat")
    
    with pytest.raises(ConfigurationError) as exc_info:
        Config.from_env()
    
    assert "invalid additional button format" in str(exc_info.value).lower()


def test_config_language_en(monkeypatch):
    """Test English language configuration."""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("RIDES_CHANNEL_ID", "-1001234567890")
    monkeypatch.setenv("LANGUAGE", "en")
    
    config = Config.from_env()
    assert config.language == "en"


def test_config_language_ua(monkeypatch):
    """Test Ukrainian language configuration."""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("RIDES_CHANNEL_ID", "-1001234567890")
    monkeypatch.setenv("LANGUAGE", "ua")
    
    config = Config.from_env()
    assert config.language == "ua"


def test_config_invalid_language(monkeypatch):
    """Test invalid language raises error."""
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.setenv("RIDES_CHANNEL_ID", "-1001234567890")
    monkeypatch.setenv("LANGUAGE", "invalid")
    
    with pytest.raises(ConfigurationError) as exc_info:
        Config.from_env()
    
    assert "invalid language" in str(exc_info.value).lower()


def test_translations_english():
    """Test English translations."""
    button_trans, msg_trans = get_translations("en")
    
    assert button_trans.join == EN_BUTTONS.join
    assert button_trans.voters == EN_BUTTONS.voters
    assert msg_trans.registration_title == "🚴 Registration"
    assert msg_trans.vote_recorded == "Your vote has been recorded!"


def test_translations_ukrainian():
    """Test Ukrainian translations."""
    button_trans, msg_trans = get_translations("ua")
    
    assert button_trans.join == UA_BUTTONS.join
    assert button_trans.voters == UA_BUTTONS.voters
    assert msg_trans.registration_title == "🚴 Реєстрація"
    assert msg_trans.vote_recorded == "Ваш голос збережено!"


def test_translations_fallback_to_english():
    """Test that invalid language falls back to English."""
    button_trans, msg_trans = get_translations("invalid")
    
    assert button_trans.join == EN_BUTTONS.join
    assert msg_trans.registration_title == "🚴 Registration"
