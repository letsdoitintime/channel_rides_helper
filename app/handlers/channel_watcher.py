"""Channel watcher handler - monitors channel for new ride posts."""
from aiogram import Router, F
from aiogram.types import Message
from loguru import logger

from app.db import Database
from app.config import Config
from app.services.registration import RegistrationService


router = Router()

# Store media group IDs temporarily to handle albums
_processing_media_groups = set()


async def should_process_message(message: Message, config: Config) -> bool:
    """Check if message should trigger registration creation."""
    # Ignore messages from bots (except if we want to track our own posts)
    if message.from_user and message.from_user.is_bot:
        return False
    
    # Check ride filter
    if config.ride_filter == "all":
        return True
    
    # Check for hashtags
    if config.ride_filter == "hashtag":
        text = message.text or message.caption or ""
        
        # Check if any configured hashtag is present
        for hashtag in config.ride_hashtags:
            if hashtag.lower() in text.lower():
                return True
        
        return False
    
    return False


def setup_channel_watcher(
    db: Database,
    config: Config,
    registration_service: RegistrationService,
):
    """Setup channel watcher handler."""
    
    @router.channel_post(F.chat.id == config.rides_channel_id)
    async def handle_channel_post(message: Message):
        """Handle new posts in the rides channel."""
        try:
            # Check if we should process this message
            if not await should_process_message(message, config):
                logger.debug(f"Skipping message {message.message_id} (filter rules)")
                return
            
            # Handle albums (media groups)
            media_group_id = message.media_group_id
            
            if media_group_id:
                # For albums, only create one registration for the entire group
                if media_group_id in _processing_media_groups:
                    logger.debug(f"Already processing media group {media_group_id}")
                    return
                
                # Mark this media group as being processed
                _processing_media_groups.add(media_group_id)
                
                # Check if we already have a registration for this media group
                existing = await db.get_post_by_media_group(
                    message.chat.id, media_group_id
                )
                if existing:
                    logger.info(f"Registration already exists for media group {media_group_id}")
                    _processing_media_groups.discard(media_group_id)
                    return
            
            # Create registration
            logger.info(f"Creating registration for message {message.message_id} in channel {message.chat.id}")
            
            success = await registration_service.create_registration(
                channel_id=message.chat.id,
                message_id=message.message_id,
                media_group_id=media_group_id,
            )
            
            if success:
                logger.info(f"Registration created successfully for {message.message_id}")
            else:
                logger.warning(f"Failed to create registration for {message.message_id}")
            
            # Clean up media group tracking
            if media_group_id:
                _processing_media_groups.discard(media_group_id)
                
        except Exception as e:
            logger.error(f"Error handling channel post: {e}", exc_info=True)
            # Clean up media group tracking on error
            if message.media_group_id:
                _processing_media_groups.discard(message.media_group_id)
    
    return router
