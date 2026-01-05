"""Button configuration loader for YAML-based configuration."""
import os
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from loguru import logger


class ButtonConfigLoader:
    """Loads button configuration from YAML file."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize button config loader.
        
        Args:
            config_file: Path to button config YAML file.
                        If None, uses default config/buttons.yaml
        """
        if config_file is None:
            # Default to config/buttons.yaml relative to project root
            project_root = Path(__file__).parent.parent
            config_file = project_root / "config" / "buttons.yaml"
        
        self.config_file = Path(config_file)
        self._config: Optional[Dict] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load button configuration from YAML file."""
        try:
            if not self.config_file.exists():
                logger.info(
                    f"Button config file not found: {self.config_file}. "
                    "Will use environment variables."
                )
                self._config = None
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
            
            logger.info(f"Loaded button configuration from: {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading button config from {self.config_file}: {e}")
            self._config = None
    
    def is_available(self) -> bool:
        """Check if YAML config is available.
        
        Returns:
            True if YAML config was loaded successfully
        """
        return self._config is not None
    
    def get_visibility(self) -> Optional[Dict[str, bool]]:
        """Get button visibility settings.
        
        Returns:
            Dictionary with visibility settings or None if not available
        """
        if self._config is None:
            return None
        return self._config.get("visibility")
    
    def get_custom_text(self) -> Optional[Dict[str, Optional[str]]]:
        """Get custom button text settings.
        
        Returns:
            Dictionary with custom text settings or None if not available
        """
        if self._config is None:
            return None
        return self._config.get("custom_text")
    
    def get_additional_buttons(self) -> Optional[List[Dict[str, str]]]:
        """Get additional buttons list.
        
        Returns:
            List of additional buttons or None if not available
        """
        if self._config is None:
            return None
        buttons = self._config.get("additional_buttons")
        if buttons is None:
            return []
        return buttons
    
    def get_access_control(self) -> Optional[Dict[str, bool]]:
        """Get access control settings.
        
        Returns:
            Dictionary with access control settings or None if not available
        """
        if self._config is None:
            return None
        return self._config.get("access_control")
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()


# Singleton instance
_loader: Optional[ButtonConfigLoader] = None


def get_button_config_loader(config_file: Optional[str] = None) -> ButtonConfigLoader:
    """Get or create button config loader instance.
    
    Args:
        config_file: Path to button config YAML file (optional)
        
    Returns:
        ButtonConfigLoader instance
    """
    global _loader
    if _loader is None:
        _loader = ButtonConfigLoader(config_file)
    return _loader
