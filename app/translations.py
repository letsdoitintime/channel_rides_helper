"""Multi-language translations for buttons and messages."""
from typing import Dict, Literal
from dataclasses import dataclass
from loguru import logger

from app.translation_loader import get_loader

Language = Literal["en", "ua"]


@dataclass
class ButtonTranslations:
    """Translations for button texts."""
    join: str
    maybe: str
    decline: str
    voters: str
    refresh: str
    

@dataclass
class MessageTranslations:
    """Translations for messages."""
    registration_title: str
    vote_recorded: str
    refreshed: str
    voters_list_title: str
    no_votes_yet: str
    vote_required: str
    join_label: str
    maybe_label: str
    decline_label: str
    changed_mind: str


# Hardcoded English translations (fallback if YAML not available)
EN_BUTTONS = ButtonTranslations(
    join="✅ Join",
    maybe="❔ Maybe",
    decline="❌ No",
    voters="👥 Voters",
    refresh="🔄 Refresh",
)

EN_MESSAGES = MessageTranslations(
    registration_title="🚴 Registration",
    vote_recorded="Your vote has been recorded!",
    refreshed="✅ Refreshed!",
    voters_list_title="👥 **Voters List**",
    no_votes_yet="_No votes yet_",
    vote_required="You need to vote first to see the voters list",
    join_label="Join",
    maybe_label="Maybe",
    decline_label="Decline",
    changed_mind="🔁 Changed mind",
)

# Hardcoded Ukrainian translations (fallback if YAML not available)
UA_BUTTONS = ButtonTranslations(
    join="✅ Їду",
    maybe="❔ Можливо",
    decline="❌ Ні",
    voters="👥 Учасники",
    refresh="🔄 Оновити",
)

UA_MESSAGES = MessageTranslations(
    registration_title="🚴 Реєстрація",
    vote_recorded="Ваш голос збережено!",
    refreshed="✅ Оновлено!",
    voters_list_title="👥 **Список учасників**",
    no_votes_yet="_Голосів поки немає_",
    vote_required="Спочатку проголосуйте, щоб побачити список учасників",
    join_label="Їду",
    maybe_label="Можливо",
    decline_label="Ні",
    changed_mind="🔁 Змінили думку",
)

# Hardcoded translation registry (fallback)
HARDCODED_TRANSLATIONS: Dict[Language, tuple[ButtonTranslations, MessageTranslations]] = {
    "en": (EN_BUTTONS, EN_MESSAGES),
    "ua": (UA_BUTTONS, UA_MESSAGES),
}


def _load_from_yaml(language: str) -> tuple[ButtonTranslations, MessageTranslations] | None:
    """Load translations from YAML file.
    
    Args:
        language: Language code
        
    Returns:
        Tuple of (ButtonTranslations, MessageTranslations) or None if loading fails
    """
    try:
        loader = get_loader()
        button_data = loader.get_button_translations(language)
        message_data = loader.get_message_translations(language)
        
        if not button_data or not message_data:
            return None
        
        buttons = ButtonTranslations(**button_data)
        messages = MessageTranslations(**message_data)
        return (buttons, messages)
    except Exception as e:
        logger.warning(f"Could not load translations from YAML for '{language}': {e}")
        return None


def get_translations(language: Language = "en") -> tuple[ButtonTranslations, MessageTranslations]:
    """Get translations for the specified language.
    
    Tries to load from YAML first, falls back to hardcoded translations.
    
    Args:
        language: Language code ('en' or 'ua')
        
    Returns:
        Tuple of (ButtonTranslations, MessageTranslations)
        
    Note:
        Falls back to English if language is not found.
    """
    # Try loading from YAML
    yaml_translations = _load_from_yaml(language)
    if yaml_translations is not None:
        return yaml_translations
    
    # Fall back to hardcoded translations
    if language not in HARDCODED_TRANSLATIONS:
        logger.warning(f"Language '{language}' not found, falling back to English")
        return HARDCODED_TRANSLATIONS["en"]
    
    return HARDCODED_TRANSLATIONS[language]
