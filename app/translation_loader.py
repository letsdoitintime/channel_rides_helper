"""Translation loader for YAML-based translations."""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from loguru import logger


class TranslationLoader:
    """Loads translations from YAML file."""
    
    def __init__(self, translations_file: Optional[str] = None):
        """Initialize translation loader.
        
        Args:
            translations_file: Path to translations YAML file.
                             If None, uses default config/translations.yaml
        """
        if translations_file is None:
            # Default to config/translations.yaml relative to project root
            project_root = Path(__file__).parent.parent
            translations_file = project_root / "config" / "translations.yaml"
        
        self.translations_file = Path(translations_file)
        self._translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load translations from YAML file."""
        try:
            if not self.translations_file.exists():
                logger.warning(
                    f"Translations file not found: {self.translations_file}. "
                    "Using hardcoded defaults."
                )
                return
            
            with open(self.translations_file, 'r', encoding='utf-8') as f:
                self._translations = yaml.safe_load(f) or {}
            
            logger.info(
                f"Loaded translations for languages: {list(self._translations.keys())}"
            )
        except Exception as e:
            logger.error(f"Error loading translations from {self.translations_file}: {e}")
            self._translations = {}
    
    def get_button_translations(self, language: str) -> Dict[str, str]:
        """Get button translations for a language.
        
        Args:
            language: Language code (e.g., 'en', 'ua')
            
        Returns:
            Dictionary with button translations
        """
        if language not in self._translations:
            logger.warning(f"Language '{language}' not found, using 'en'")
            language = "en"
        
        if language not in self._translations:
            # Return empty dict if even 'en' is not available
            return {}
        
        return self._translations.get(language, {}).get("buttons", {})
    
    def get_message_translations(self, language: str) -> Dict[str, str]:
        """Get message translations for a language.
        
        Args:
            language: Language code (e.g., 'en', 'ua')
            
        Returns:
            Dictionary with message translations
        """
        if language not in self._translations:
            logger.warning(f"Language '{language}' not found, using 'en'")
            language = "en"
        
        if language not in self._translations:
            # Return empty dict if even 'en' is not available
            return {}
        
        return self._translations.get(language, {}).get("messages", {})
    
    def get_available_languages(self) -> list[str]:
        """Get list of available language codes.
        
        Returns:
            List of language codes
        """
        return list(self._translations.keys())
    
    def reload(self) -> None:
        """Reload translations from file."""
        self._load_translations()


# Singleton instance
_loader: Optional[TranslationLoader] = None


def get_loader(translations_file: Optional[str] = None) -> TranslationLoader:
    """Get or create translation loader instance.
    
    Args:
        translations_file: Path to translations YAML file (optional)
        
    Returns:
        TranslationLoader instance
    """
    global _loader
    if _loader is None:
        _loader = TranslationLoader(translations_file)
    return _loader
