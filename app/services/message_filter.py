"""Message filter service for determining which messages to process."""
from typing import List
from aiogram.types import Message
from loguru import logger


class MessageFilterService:
    """Service for filtering messages based on configuration."""
    
    def __init__(
        self,
        ride_filter: str,
        ride_hashtags: List[str],
    ):
        """
        Initialize message filter service.
        
        Args:
            ride_filter: Filter type ("all" or "hashtag")
            ride_hashtags: List of hashtags to filter by (if filter is "hashtag")
        """
        self.ride_filter = ride_filter
        self.ride_hashtags = [tag.lower() for tag in ride_hashtags]
    
    def should_process(self, message: Message) -> bool:
        """
        Determine if a message should be processed.
        
        Args:
            message: Telegram message to check
        
        Returns:
            True if message should be processed, False otherwise
        """
        # Ignore messages from bots
        if message.from_user and message.from_user.is_bot:
            logger.debug(f"Skipping bot message {message.message_id}")
            return False
        
        # Check ride filter
        if self.ride_filter == "all":
            logger.debug(f"Processing message {message.message_id} (filter: all)")
            return True
        
        # Check for hashtags
        if self.ride_filter == "hashtag":
            return self._has_required_hashtag(message)
        
        logger.warning(f"Unknown ride filter: {self.ride_filter}")
        return False
    
    def _has_required_hashtag(self, message: Message) -> bool:
        """
        Check if message contains any of the required hashtags.
        
        Args:
            message: Telegram message to check
        
        Returns:
            True if message contains required hashtag, False otherwise
        """
        text = message.text or message.caption or ""
        text_lower = text.lower()
        
        for hashtag in self.ride_hashtags:
            if hashtag in text_lower:
                logger.debug(
                    f"Message {message.message_id} matches hashtag: {hashtag}"
                )
                return True
        
        logger.debug(
            f"Message {message.message_id} does not contain required hashtags"
        )
        return False
    
    def get_hashtags_from_message(self, message: Message) -> List[str]:
        """
        Extract hashtags from message.
        
        Args:
            message: Telegram message to extract hashtags from
        
        Returns:
            List of hashtags found in message
        """
        text = message.text or message.caption or ""
        
        # Simple hashtag extraction (words starting with #)
        words = text.split()
        hashtags = [word for word in words if word.startswith("#")]
        
        return hashtags
