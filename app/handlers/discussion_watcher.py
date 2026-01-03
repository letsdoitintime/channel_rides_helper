"""Discussion group watcher - captures forwarded channel posts to map discussion message IDs."""
from aiogram import Router, F
from aiogram.types import Message
from loguru import logger

from app.db import Database
from app.config import Config
from app.services.registration import RegistrationService


router = Router()


def setup_discussion_watcher(
    db: Database,
    config: Config,
    registration_service: RegistrationService,
):
    """Setup discussion group watcher to capture forwarded channel posts."""
    
    @router.message(F.chat.id == config.discussion_group_id)
    async def handle_discussion_message(message: Message):
        """Handle messages in the discussion group to capture channel post forwards."""
        try:
            # Check if this is a forwarded message from our channel
            if (message.forward_from_chat 
                and message.forward_from_chat.id == config.rides_channel_id
                and message.forward_from_message_id):
                
                channel_message_id = message.forward_from_message_id
                discussion_message_id = message.message_id
                
                logger.info(
                    f"Captured discussion mapping: channel msg {channel_message_id} "
                    f"-> discussion msg {discussion_message_id}"
                )
                
                # Store this mapping
                await db.update_discussion_message_id(
                    config.rides_channel_id,
                    channel_message_id,
                    discussion_message_id
                )
                
                # Check if we have a pending post waiting for this discussion message
                post = await db.get_post(config.rides_channel_id, channel_message_id)
                if post and post.get("mode") == "discussion_thread" and not post.get("registration_message_id"):
                    # We have a pending post - now create the registration
                    logger.info(f"Discussion message captured, creating registration for post {channel_message_id}")
                    
                    # Create registration using the discussion_thread method
                    success = await registration_service.complete_discussion_registration(
                        config.rides_channel_id,
                        channel_message_id
                    )
                    
                    if success:
                        logger.info(f"Registration completed successfully in discussion thread")
                    else:
                        logger.warning(f"Failed to create registration in discussion thread")
                
        except Exception as e:
            logger.error(f"Error handling discussion message: {e}", exc_info=True)
    
    return router
