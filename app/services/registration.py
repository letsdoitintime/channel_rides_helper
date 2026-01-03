"""Registration service for creating and updating registration cards."""
from typing import Optional, Dict, Tuple
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.exceptions import TelegramAPIError
from loguru import logger

from app.db import Database
from app.config import Config


class RegistrationService:
    """Service for managing registration cards."""
    
    def __init__(self, bot: Bot, db: Database, config: Config):
        self.bot = bot
        self.db = db
        self.config = config
    
    def _create_registration_keyboard(
        self, channel_id: int, message_id: int
    ) -> InlineKeyboardMarkup:
        """Create inline keyboard for registration."""
        # Use shortened callback data to avoid 64-byte limit
        # Format: v:status:channel_id:message_id
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Join",
                    callback_data=f"v:join:{channel_id}:{message_id}"
                ),
                InlineKeyboardButton(
                    text="❔ Maybe",
                    callback_data=f"v:maybe:{channel_id}:{message_id}"
                ),
                InlineKeyboardButton(
                    text="❌ No",
                    callback_data=f"v:decline:{channel_id}:{message_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👥 Voters",
                    callback_data=f"voters:{channel_id}:{message_id}"
                ),
                InlineKeyboardButton(
                    text="🔄 Refresh",
                    callback_data=f"refresh:{channel_id}:{message_id}"
                ),
            ],
        ])
        return keyboard
    
    async def _create_registration_text(
        self, channel_id: int, message_id: int
    ) -> str:
        """Create registration card text with current stats."""
        counts = await self.db.get_vote_counts(channel_id, message_id)
        changed_mind = await self.db.get_changed_mind_count(channel_id, message_id)
        
        text = "🚴 Registration\n\n"
        text += f"✅ Join: {counts['join']}\n"
        text += f"❔ Maybe: {counts['maybe']}\n"
        text += f"❌ No: {counts['decline']}\n"
        
        if self.config.show_changed_mind_stats and changed_mind > 0:
            text += f"🔁 Changed mind: {changed_mind}\n"
        
        return text
    
    async def create_registration(
        self, channel_id: int, message_id: int, media_group_id: Optional[str] = None
    ) -> bool:
        """
        Create a registration card with fallback logic.
        
        Modes:
        1. edit_channel - Edit the original channel post (only if bot is author)
        2. discussion_thread - Post in linked discussion group thread
        3. channel_reply_post - Create a new channel post replying to original
        
        Fallback chain: edit_channel → discussion_thread → channel_reply_post
        
        Args:
            channel_id: Channel ID where the post was made
            message_id: Message ID in the channel
            media_group_id: Optional media group ID for albums
        """
        # Check if already exists
        existing = await self.db.get_post(channel_id, message_id)
        if existing:
            logger.info(f"Registration already exists for {channel_id}/{message_id}")
            return False
        
        # For albums, check if we already created registration for this media group
        if media_group_id:
            existing_album = await self.db.get_post_by_media_group(channel_id, media_group_id)
            if existing_album:
                logger.info(f"Registration already exists for album {media_group_id}")
                return False
        
        text = await self._create_registration_text(channel_id, message_id)
        keyboard = self._create_registration_keyboard(channel_id, message_id)
        
        # Try modes in order based on configuration
        modes_to_try = self._get_fallback_chain()
        
        for mode in modes_to_try:
            try:
                if mode == "edit_channel":
                    success, reg_chat_id, reg_message_id = await self._try_edit_channel(
                        channel_id, message_id, text, keyboard
                    )
                elif mode == "discussion_thread":
                    success, reg_chat_id, reg_message_id = await self._try_discussion_thread(
                        channel_id, message_id, text, keyboard
                    )
                elif mode == "channel_reply_post":
                    success, reg_chat_id, reg_message_id = await self._try_channel_reply(
                        channel_id, message_id, text, keyboard
                    )
                else:
                    continue
                
                if success:
                    # Store in database with registration location
                    await self.db.create_post(
                        channel_id=channel_id,
                        channel_message_id=message_id,
                        mode=mode,
                        registration_chat_id=reg_chat_id,
                        registration_message_id=reg_message_id,
                        media_group_id=media_group_id,
                    )
                    logger.info(f"Registration created using mode: {mode}")
                    return True
                    
            except Exception as e:
                logger.warning(f"Failed mode {mode}: {e}")
                continue
        
        logger.error(f"All registration modes failed for {channel_id}/{message_id}")
        return False
    
    def _get_fallback_chain(self) -> list:
        """Get the fallback chain starting from configured mode."""
        all_modes = ["edit_channel", "discussion_thread", "channel_reply_post"]
        
        # Start with configured mode
        start_index = all_modes.index(self.config.registration_mode)
        
        # Return modes starting from configured one
        return all_modes[start_index:] + all_modes[:start_index]
    
    async def _try_edit_channel(
        self, channel_id: int, message_id: int, text: str, keyboard: InlineKeyboardMarkup
    ) -> Tuple[bool, Optional[int], Optional[int]]:
        """Try to edit the original channel message. Returns (success, reg_chat_id, reg_message_id)."""
        try:
            await self.bot.edit_message_text(
                chat_id=channel_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
            )
            
            # Registration is in the same location as original message
            return True, channel_id, message_id
        except TelegramAPIError as e:
            logger.debug(f"Cannot edit channel message: {e}")
            return False, None, None
    
    async def _try_discussion_thread(
        self, channel_id: int, message_id: int, text: str, keyboard: InlineKeyboardMarkup
    ) -> Tuple[bool, Optional[int], Optional[int]]:
        """
        Try to post in linked discussion group as a comment/reply to the channel post.
        Returns (success, reg_chat_id, reg_message_id).
        
        For channels with linked discussion groups, Telegram automatically forwards
        channel posts to the discussion group. We need to reply to that forwarded message.
        """
        if not self.config.discussion_group_id:
            return False, None, None
        
        # Try to get the discussion message ID from database
        post = await self.db.get_post(channel_id, message_id)
        discussion_message_id = post.get("discussion_message_id") if post else None
        
        if not discussion_message_id:
            logger.warning(
                f"Discussion message ID not found for channel post {channel_id}/{message_id}. "
                "The channel post may not have been forwarded to the discussion group yet."
            )
            return False, None, None
        
        try:
            # Reply to the forwarded channel post in the discussion group
            sent = await self.bot.send_message(
                chat_id=self.config.discussion_group_id,
                text=text,
                reply_markup=keyboard,
                reply_to_message_id=discussion_message_id,
            )
            logger.info(f"Sent registration as reply to discussion message {discussion_message_id}")
            return True, self.config.discussion_group_id, sent.message_id
        except TelegramAPIError as e:
            logger.error(f"Cannot reply to discussion message {discussion_message_id}: {e}")
            return False, None, None
    
    async def _try_channel_reply(
        self, channel_id: int, message_id: int, text: str, keyboard: InlineKeyboardMarkup
    ) -> Tuple[bool, Optional[int], Optional[int]]:
        """Try to create a reply post in the channel. Returns (success, reg_chat_id, reg_message_id)."""
        try:
            # Try to reply to original message
            sent = await self.bot.send_message(
                chat_id=channel_id,
                text=text,
                reply_markup=keyboard,
                reply_to_message_id=message_id,
            )
            
            # Return registration location
            return True, channel_id, sent.message_id
        except TelegramAPIError as e:
            logger.debug(f"Cannot reply in channel, trying without reply: {e}")
            
            # If reply failed, try without reply but add link button
            try:
                # Add a button to link back to original post
                link_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    *keyboard.inline_keyboard,
                    [
                        InlineKeyboardButton(
                            text="📍 Original Post",
                            url=self._get_message_link(channel_id, message_id)
                        )
                    ]
                ])
                
                sent = await self.bot.send_message(
                    chat_id=channel_id,
                    text=text,
                    reply_markup=link_keyboard,
                )
                
                # Return registration location
                return True, channel_id, sent.message_id
            except TelegramAPIError as e2:
                logger.debug(f"Cannot post to channel at all: {e2}")
                return False, None, None
    
    async def complete_discussion_registration(
        self, channel_id: int, message_id: int
    ) -> bool:
        """Complete a pending discussion_thread registration after discussion message is captured."""
        try:
            text = await self._create_registration_text(channel_id, message_id)
            keyboard = self._create_registration_keyboard(channel_id, message_id)
            
            success, reg_chat_id, reg_message_id = await self._try_discussion_thread(
                channel_id, message_id, text, keyboard
            )
            
            if success:
                # Update the post with registration location
                await self.db.update_post_registration(
                    channel_id, message_id, reg_chat_id, reg_message_id
                )
                logger.info(f"Discussion registration completed for {channel_id}/{message_id}")
                return True
            else:
                logger.error(f"Failed to complete discussion registration for {channel_id}/{message_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error completing discussion registration: {e}", exc_info=True)
            return False
    
    def _get_message_link(self, channel_id: int, message_id: int) -> str:
        """Generate t.me link for a message."""
        # Convert channel_id to format suitable for links
        # For private channels: t.me/c/{channel_id without -100 prefix}/{message_id}
        if str(channel_id).startswith("-100"):
            clean_id = str(channel_id)[4:]  # Remove -100 prefix
            return f"https://t.me/c/{clean_id}/{message_id}"
        else:
            # For public channels, would need username (not implemented)
            return f"https://t.me/c/{channel_id}/{message_id}"
    
    async def _repair_post_registration(
        self, channel_id: int, message_id: int, mode: str
    ) -> bool:
        """Repair a post with missing registration IDs based on its mode."""
        try:
            if mode == "edit_channel":
                # For edit_channel mode, registration is at the same location
                await self.db.update_post_registration(
                    channel_id, message_id, channel_id, message_id
                )
                logger.info(f"Repaired edit_channel post {channel_id}/{message_id}")
                return True
            elif mode == "discussion_thread":
                # For discussion_thread, we can't reliably find the message
                # User would need to recreate it
                logger.error(f"Cannot repair discussion_thread post - message lost")
                return False
            elif mode == "channel_reply_post":
                # For channel_reply_post, we can't reliably find the message
                # User would need to recreate it
                logger.error(f"Cannot repair channel_reply_post - message lost")
                return False
            else:
                logger.error(f"Unknown mode: {mode}")
                return False
        except Exception as e:
            logger.error(f"Error repairing post: {e}")
            return False
    
    async def update_registration(
        self, channel_id: int, message_id: int
    ) -> bool:
        """Update an existing registration card."""
        post = await self.db.get_post(channel_id, message_id)
        if not post:
            logger.warning(f"Post not found: {channel_id}/{message_id}")
            return False
        
        # Check if registration message IDs are set
        if not post["registration_chat_id"] or not post["registration_message_id"]:
            logger.warning(
                f"Registration message not set for post {channel_id}/{message_id}. "
                f"Mode: {post.get('mode')}. Attempting to repair..."
            )
            # Try to repair by setting correct registration IDs based on mode
            repaired = await self._repair_post_registration(channel_id, message_id, post["mode"])
            if not repaired:
                logger.error(f"Failed to repair registration for post {channel_id}/{message_id}")
                return False
            # Reload post after repair
            post = await self.db.get_post(channel_id, message_id)
            if not post or not post["registration_chat_id"] or not post["registration_message_id"]:
                return False
        
        text = await self._create_registration_text(channel_id, message_id)
        keyboard = self._create_registration_keyboard(channel_id, message_id)
        
        try:
            await self.bot.edit_message_text(
                chat_id=post["registration_chat_id"],
                message_id=post["registration_message_id"],
                text=text,
                reply_markup=keyboard,
            )
            return True
        except TelegramAPIError as e:
            logger.error(f"Failed to update registration: {e}")
            return False
