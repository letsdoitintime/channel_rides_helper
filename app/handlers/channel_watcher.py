"""Channel watcher handler - monitors channel for new ride posts."""
from aiogram import Router, F
from aiogram.types import Message
from loguru import logger

from app.db import Database
from app.config import Config
from app.services.registration import RegistrationService
from app.services.message_filter import MessageFilterService


router = Router()

# Store media group IDs temporarily to handle albums
_processing_media_groups = set()


def setup_channel_watcher(
    db: Database,
    config: Config,
    registration_service: RegistrationService,
):
    """Setup channel watcher handler."""
    
    # Initialize message filter service
    message_filter = MessageFilterService(
        config.ride_filter,
        config.ride_hashtags
    )
    
    @router.channel_post(F.chat.id == config.rides_channel_id)
    async def handle_channel_post(message: Message):
        """Handle new posts in the rides channel."""
        try:
            # Check if we should process this message using message filter service
            if not message_filter.should_process(message):
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
            
            # For discussion_thread mode, create a pending post and wait for discussion watcher
            if config.registration_mode == "discussion_thread":
                # Create pending post - discussion watcher will complete it
                await db.create_post(
                    channel_id=message.chat.id,
                    channel_message_id=message.message_id,
                    mode="discussion_thread",
                    media_group_id=media_group_id,
                )
                logger.info(f"Created pending post for discussion_thread mode, waiting for forward...")
            else:
                # For other modes, create registration immediately
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
