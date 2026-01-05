"""Tests for YAML-based translation and button configuration."""
import pytest
import tempfile
import os
from pathlib import Path

from app.translation_loader import TranslationLoader, get_loader
from app.button_config_loader import ButtonConfigLoader, get_button_config_loader
from app.translations import get_translations
from app.config import Config


class TestTranslationLoader:
    """Tests for YAML translation loader."""
    
    def test_load_valid_translations(self):
        """Test loading valid translations from YAML."""
        yaml_content = """
en:
  buttons:
    join: "✅ Join"
    maybe: "❔ Maybe"
    decline: "❌ No"
    voters: "👥 Voters"
    refresh: "🔄 Refresh"
  messages:
    registration_title: "🚴 Registration"
    vote_recorded: "Your vote has been recorded!"
    refreshed: "✅ Refreshed!"
    voters_list_title: "👥 **Voters List**"
    no_votes_yet: "_No votes yet_"
    vote_required: "You need to vote first to see the voters list"
    join_label: "Join"
    maybe_label: "Maybe"
    decline_label: "Decline"
    changed_mind: "🔁 Changed mind"

ua:
  buttons:
    join: "✅ Їду"
    maybe: "❔ Можливо"
    decline: "❌ Ні"
    voters: "👥 Учасники"
    refresh: "🔄 Оновити"
  messages:
    registration_title: "🚴 Реєстрація"
    vote_recorded: "Ваш голос збережено!"
    refreshed: "✅ Оновлено!"
    voters_list_title: "👥 **Список учасників**"
    no_votes_yet: "_Голосів поки немає_"
    vote_required: "Спочатку проголосуйте, щоб побачити список учасників"
    join_label: "Їду"
    maybe_label: "Можливо"
    decline_label: "Ні"
    changed_mind: "🔁 Змінили думку"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            loader = TranslationLoader(temp_file)
            
            # Test English
            buttons_en = loader.get_button_translations("en")
            assert buttons_en["join"] == "✅ Join"
            assert buttons_en["voters"] == "👥 Voters"
            
            messages_en = loader.get_message_translations("en")
            assert messages_en["registration_title"] == "🚴 Registration"
            assert messages_en["vote_recorded"] == "Your vote has been recorded!"
            
            # Test Ukrainian
            buttons_ua = loader.get_button_translations("ua")
            assert buttons_ua["join"] == "✅ Їду"
            assert buttons_ua["voters"] == "👥 Учасники"
            
            messages_ua = loader.get_message_translations("ua")
            assert messages_ua["registration_title"] == "🚴 Реєстрація"
            assert messages_ua["vote_recorded"] == "Ваш голос збережено!"
        finally:
            os.unlink(temp_file)
    
    def test_load_missing_file(self):
        """Test loading with missing file."""
        loader = TranslationLoader("/nonexistent/file.yaml")
        
        # Should return empty dict when file doesn't exist
        buttons = loader.get_button_translations("en")
        assert buttons == {}
    
    def test_fallback_to_english(self):
        """Test fallback to English for unknown language."""
        yaml_content = """
en:
  buttons:
    join: "✅ Join"
    maybe: "❔ Maybe"
    decline: "❌ No"
    voters: "👥 Voters"
    refresh: "🔄 Refresh"
  messages:
    registration_title: "🚴 Registration"
    vote_recorded: "Your vote has been recorded!"
    refreshed: "✅ Refreshed!"
    voters_list_title: "👥 **Voters List**"
    no_votes_yet: "_No votes yet_"
    vote_required: "You need to vote first to see the voters list"
    join_label: "Join"
    maybe_label: "Maybe"
    decline_label: "Decline"
    changed_mind: "🔁 Changed mind"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            loader = TranslationLoader(temp_file)
            
            # Should fall back to English
            buttons = loader.get_button_translations("fr")
            assert buttons["join"] == "✅ Join"
        finally:
            os.unlink(temp_file)
    
    def test_available_languages(self):
        """Test getting available languages."""
        yaml_content = """
en:
  buttons:
    join: "Join"
  messages:
    registration_title: "Registration"

ua:
  buttons:
    join: "Їду"
  messages:
    registration_title: "Реєстрація"

de:
  buttons:
    join: "Dabei"
  messages:
    registration_title: "Anmeldung"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            loader = TranslationLoader(temp_file)
            languages = loader.get_available_languages()
            
            assert "en" in languages
            assert "ua" in languages
            assert "de" in languages
            assert len(languages) == 3
        finally:
            os.unlink(temp_file)


class TestButtonConfigLoader:
    """Tests for YAML button configuration loader."""
    
    def test_load_valid_config(self):
        """Test loading valid button config from YAML."""
        yaml_content = """
visibility:
  show_join: true
  show_maybe: true
  show_decline: false
  show_voters: true
  show_refresh: false

custom_text:
  join: "I'm In!"
  maybe: "Maybe Later"
  decline: null
  voters: "Show List"
  refresh: null

additional_buttons:
  - text: "Rules"
    url: "https://example.com/rules"
  - text: "Map"
    url: "https://example.com/map"

access_control:
  require_vote_to_see_voters: true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            loader = ButtonConfigLoader(temp_file)
            
            assert loader.is_available()
            
            visibility = loader.get_visibility()
            assert visibility["show_join"] is True
            assert visibility["show_decline"] is False
            assert visibility["show_refresh"] is False
            
            custom_text = loader.get_custom_text()
            assert custom_text["join"] == "I'm In!"
            assert custom_text["maybe"] == "Maybe Later"
            assert custom_text["decline"] is None
            
            additional = loader.get_additional_buttons()
            assert len(additional) == 2
            assert additional[0]["text"] == "Rules"
            assert additional[0]["url"] == "https://example.com/rules"
            
            access_control = loader.get_access_control()
            assert access_control["require_vote_to_see_voters"] is True
        finally:
            os.unlink(temp_file)
    
    def test_load_missing_file(self):
        """Test loading with missing file."""
        loader = ButtonConfigLoader("/nonexistent/file.yaml")
        
        assert not loader.is_available()
        assert loader.get_visibility() is None
        assert loader.get_custom_text() is None
        assert loader.get_additional_buttons() == []  # Returns empty list, not None


class TestYAMLIntegration:
    """Integration tests for YAML configuration with Config class."""
    
    def test_config_loads_from_yaml_when_available(self, monkeypatch, tmp_path):
        """Test that Config loads button config from YAML when available."""
        # Create a temporary button config YAML
        button_yaml = tmp_path / "buttons.yaml"
        button_yaml.write_text("""
visibility:
  show_join: true
  show_maybe: false
  show_decline: true
  show_voters: true
  show_refresh: true

custom_text:
  join: "Count Me In"
  maybe: null
  decline: null
  voters: null
  refresh: null

additional_buttons: []

access_control:
  require_vote_to_see_voters: false
""")
        
        # Set environment variables
        monkeypatch.setenv("BOT_TOKEN", "test_token")
        monkeypatch.setenv("RIDES_CHANNEL_ID", "-1001234567890")
        monkeypatch.setenv("RIDE_FILTER", "all")  # Avoid hashtag validation
        
        # Mock the button config loader to use our temp file
        from app import button_config_loader
        from app.button_config_loader import ButtonConfigLoader
        
        # Create a new loader instance for this test
        test_loader = ButtonConfigLoader(str(button_yaml))
        
        # Temporarily replace the singleton
        original_loader = button_config_loader._loader
        button_config_loader._loader = test_loader
        
        try:
            config = Config.from_env()
            
            # Verify YAML config was used
            assert config.button_config.show_join is True
            assert config.button_config.show_maybe is False  # Different from env default
            assert config.button_config.custom_join_text == "Count Me In"
        finally:
            # Restore original loader
            button_config_loader._loader = original_loader
    
    def test_config_falls_back_to_env_when_yaml_missing(self, monkeypatch):
        """Test that Config falls back to env vars when YAML is not available."""
        monkeypatch.setenv("BOT_TOKEN", "test_token")
        monkeypatch.setenv("RIDES_CHANNEL_ID", "-1001234567890")
        monkeypatch.setenv("RIDE_FILTER", "all")  # Avoid hashtag validation
        monkeypatch.setenv("BUTTON_SHOW_MAYBE", "false")
        monkeypatch.setenv("BUTTON_CUSTOM_JOIN_TEXT", "I'm Coming")
        
        # Mock the button config loader to return unavailable
        from app import button_config_loader
        from app.button_config_loader import ButtonConfigLoader
        
        # Create a new loader instance for this test
        test_loader = ButtonConfigLoader("/nonexistent/file.yaml")
        
        # Temporarily replace the singleton
        original_loader = button_config_loader._loader
        button_config_loader._loader = test_loader
        
        try:
            config = Config.from_env()
            
            # Verify env vars were used
            assert config.button_config.show_maybe is False
            assert config.button_config.custom_join_text == "I'm Coming"
        finally:
            # Restore original loader
            button_config_loader._loader = original_loader


class TestTranslationsYAMLIntegration:
    """Integration tests for YAML translations with get_translations function."""
    
    def test_translations_load_from_yaml(self, tmp_path):
        """Test that translations load from YAML file."""
        # Create a temporary translations YAML
        trans_yaml = tmp_path / "translations.yaml"
        trans_yaml.write_text("""
en:
  buttons:
    join: "✅ Join"
    maybe: "❔ Maybe"
    decline: "❌ No"
    voters: "👥 Voters"
    refresh: "🔄 Refresh"
  messages:
    registration_title: "🚴 Registration"
    vote_recorded: "Your vote has been recorded!"
    refreshed: "✅ Refreshed!"
    voters_list_title: "👥 **Voters List**"
    no_votes_yet: "_No votes yet_"
    vote_required: "You need to vote first to see the voters list"
    join_label: "Join"
    maybe_label: "Maybe"
    decline_label: "Decline"
    changed_mind: "🔁 Changed mind"
""")
        
        # Mock the translation loader
        from app import translation_loader
        from app.translation_loader import TranslationLoader
        
        # Create a new loader instance for this test
        test_loader = TranslationLoader(str(trans_yaml))
        
        # Temporarily replace the singleton
        original_loader = translation_loader._loader
        translation_loader._loader = test_loader
        
        try:
            button_trans, msg_trans = get_translations("en")
            
            assert button_trans.join == "✅ Join"
            assert button_trans.voters == "👥 Voters"
            assert msg_trans.registration_title == "🚴 Registration"
        finally:
            # Restore original loader
            translation_loader._loader = original_loader
    
    def test_translations_fallback_to_hardcoded(self):
        """Test that translations fall back to hardcoded when YAML fails."""
        # Mock the translation loader to return None
        from app import translation_loader
        from app.translation_loader import TranslationLoader
        
        # Create a new loader instance for this test
        test_loader = TranslationLoader("/nonexistent/file.yaml")
        
        # Temporarily replace the singleton
        original_loader = translation_loader._loader
        translation_loader._loader = test_loader
        
        try:
            button_trans, msg_trans = get_translations("en")
            
            # Should still work with hardcoded fallback
            assert button_trans.join == "✅ Join"
            assert msg_trans.registration_title == "🚴 Registration"
        finally:
            # Restore original loader
            translation_loader._loader = original_loader
