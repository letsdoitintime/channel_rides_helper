"""Callback handlers for vote buttons and other interactions."""
from datetime import datetime, timedelta, timezone
from aiogram import Router, F
from aiogram.types import CallbackQuery
from loguru import logger

from app.db import Database
from app.config import Config
from app.services.registration import RegistrationService
from app.domain.models import VoteStatus
from app.exceptions import RateLimitError
from app.utils.user_formatter import format_user_name


router = Router()


def setup_callbacks(
    db: Database,
    config: Config,
    registration_service: RegistrationService,
):
    """Setup callback handlers."""
    
    @router.callback_query(F.data.startswith("v:"))
    async def handle_vote(callback: CallbackQuery):
        """Handle vote button clicks."""
        try:
            # Parse callback data: v:status:channel_id:message_id
            parts = callback.data.split(":")
            if len(parts) != 4:
                await callback.answer("Invalid callback data", show_alert=True)
                return
            
            _, status, channel_id_str, message_id_str = parts
            channel_id = int(channel_id_str)
            message_id = int(message_id_str)
            
            # Validate status
            if status not in ["join", "maybe", "decline"]:
                await callback.answer("Invalid status", show_alert=True)
                return
            
            # Rate limiting check
            if config.vote_cooldown > 0:
                last_vote = await db.get_last_vote_time(
                    channel_id, message_id, callback.from_user.id
                )
                if last_vote:
                    time_since_last = datetime.now(timezone.utc) - last_vote
                    if time_since_last < timedelta(seconds=config.vote_cooldown):
                        remaining = config.vote_cooldown - time_since_last.total_seconds()
                        await callback.answer(
                            f"Please wait {remaining:.0f}s before voting again",
                            show_alert=False
                        )
                        return
            
            # Update vote in database
            await db.upsert_vote(channel_id, message_id, callback.from_user.id, status)
            
            # Update registration card
            await registration_service.update_registration(channel_id, message_id)
            
            # Send feedback
            status_emoji = {"join": "✅", "maybe": "❔", "decline": "❌"}
            await callback.answer(f"{status_emoji[status]} Your vote has been recorded!")
            
        except ValueError as e:
            logger.error(f"Invalid callback data format: {callback.data}")
            await callback.answer("Invalid data format", show_alert=True)
        except Exception as e:
            logger.error(f"Error handling vote: {e}", exc_info=True)
            await callback.answer("An error occurred. Please try again.", show_alert=True)
    
    @router.callback_query(F.data.startswith("refresh:"))
    async def handle_refresh(callback: CallbackQuery):
        """Handle refresh button click."""
        try:
            # Parse callback data: refresh:channel_id:message_id
            parts = callback.data.split(":")
            if len(parts) != 3:
                await callback.answer("Invalid callback data", show_alert=True)
                return
            
            _, channel_id_str, message_id_str = parts
            channel_id = int(channel_id_str)
            message_id = int(message_id_str)
            
            # Update registration card
            await registration_service.update_registration(channel_id, message_id)
            
            await callback.answer("✅ Refreshed!")
            
        except Exception as e:
            logger.error(f"Error handling refresh: {e}", exc_info=True)
            await callback.answer("An error occurred. Please try again.", show_alert=True)
    
    @router.callback_query(F.data.startswith("voters:"))
    async def handle_voters(callback: CallbackQuery):
        """Handle voters list button click."""
        try:
            # Parse callback data: voters:channel_id:message_id
            parts = callback.data.split(":")
            if len(parts) != 3:
                await callback.answer("Invalid callback data", show_alert=True)
                return
            
            _, channel_id_str, message_id_str = parts
            channel_id = int(channel_id_str)
            message_id = int(message_id_str)
            
            # Get voters grouped by status
            voters = await db.get_voters_by_status(channel_id, message_id)
            
            # Build message text
            text = "👥 **Voters List**\n\n"
            
            if voters["join"]:
                text += f"✅ **Join ({len(voters['join'])})**\n"
                for user_id in voters["join"]:
                    name = await format_user_name(callback.bot, user_id)
                    text += f"  • {name}\n"
                text += "\n"
            
            if voters["maybe"]:
                text += f"❔ **Maybe ({len(voters['maybe'])})**\n"
                for user_id in voters["maybe"]:
                    name = await format_user_name(callback.bot, user_id)
                    text += f"  • {name}\n"
                text += "\n"
            
            if voters["decline"]:
                text += f"❌ **Decline ({len(voters['decline'])})**\n"
                for user_id in voters["decline"]:
                    name = await format_user_name(callback.bot, user_id)
                    text += f"  • {name}\n"
                text += "\n"
            
            if not any(voters.values()):
                text += "_No votes yet_"
            
            # Check if discussion group is configured
            if not config.discussion_group_id:
                await callback.answer("Discussion group not configured", show_alert=True)
                return
            
            # Get the post to check for previous voters message and get thread info
            post = await db.get_post(channel_id, message_id)
            
            # Delete previous voters message if exists
            if post and post.get("voters_message_id"):
                try:
                    await callback.bot.delete_message(
                        chat_id=config.discussion_group_id,
                        message_id=post["voters_message_id"]
                    )
                except Exception as e:
                    logger.debug(f"Could not delete previous voters message: {e}")
            
            # Get the discussion message ID to reply to
            discussion_message_id = post.get("discussion_message_id") if post else None
            
            if not discussion_message_id:
                await callback.answer("Discussion thread not found", show_alert=True)
                return
            
            # Send new voters message to discussion group as reply to the thread
            try:
                sent = await callback.bot.send_message(
                    chat_id=config.discussion_group_id,
                    text=text,
                    parse_mode="Markdown",
                    reply_to_message_id=discussion_message_id,
                )
            except Exception as e:
                logger.error(f"Could not send voters message: {e}")
                await callback.answer("Failed to send voters list", show_alert=True)
                return
            
            # Store the new voters message ID
            await db.update_voters_message(channel_id, message_id, sent.message_id)
            
            await callback.answer("Voters list sent to discussion group!")
            
        except Exception as e:
            logger.error(f"Error handling voters: {e}", exc_info=True)
            await callback.answer("An error occurred. Please try again.", show_alert=True)
    
    return router
