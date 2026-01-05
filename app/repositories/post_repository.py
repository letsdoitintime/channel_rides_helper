"""Post repository for managing post data."""
from typing import Optional
from datetime import datetime, timezone

from app.db import Database
from app.domain.models import Post, RegistrationMode
from app.exceptions import DatabaseError
from loguru import logger


class PostRepository:
    """Repository for post operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create(
        self,
        channel_id: int,
        channel_message_id: int,
        mode: RegistrationMode,
        registration_chat_id: Optional[int] = None,
        registration_message_id: Optional[int] = None,
        media_group_id: Optional[str] = None,
    ) -> bool:
        """
        Create a new post record.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID in channel
            mode: Registration mode
            registration_chat_id: Chat ID where registration is posted
            registration_message_id: Message ID of registration
            media_group_id: Optional media group ID for albums
        
        Returns:
            True if created successfully, False if already exists
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return await self.db.create_post(
                channel_id=channel_id,
                channel_message_id=channel_message_id,
                mode=mode.value,
                registration_chat_id=registration_chat_id,
                registration_message_id=registration_message_id,
                media_group_id=media_group_id,
            )
        except Exception as e:
            logger.error(f"Failed to create post: {e}")
            raise DatabaseError(f"Failed to create post: {e}")
    
    async def get(self, channel_id: int, channel_message_id: int) -> Optional[Post]:
        """
        Get post by channel_id and message_id.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID
        
        Returns:
            Post object or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            data = await self.db.get_post(channel_id, channel_message_id)
            return Post.from_dict(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get post: {e}")
            raise DatabaseError(f"Failed to get post: {e}")
    
    async def get_by_media_group(
        self, channel_id: int, media_group_id: str
    ) -> Optional[Post]:
        """
        Get post by media group ID.
        
        Args:
            channel_id: Channel ID
            media_group_id: Media group ID
        
        Returns:
            Post object or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            data = await self.db.get_post_by_media_group(channel_id, media_group_id)
            return Post.from_dict(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get post by media group: {e}")
            raise DatabaseError(f"Failed to get post by media group: {e}")
    
    async def update_registration(
        self,
        channel_id: int,
        channel_message_id: int,
        registration_chat_id: int,
        registration_message_id: int,
    ) -> None:
        """
        Update registration message info for a post.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID
            registration_chat_id: Registration chat ID
            registration_message_id: Registration message ID
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            await self.db.update_post_registration(
                channel_id, channel_message_id,
                registration_chat_id, registration_message_id
            )
        except Exception as e:
            logger.error(f"Failed to update post registration: {e}")
            raise DatabaseError(f"Failed to update post registration: {e}")
    
    async def update_voters_message(
        self,
        channel_id: int,
        channel_message_id: int,
        voters_message_id: int,
    ) -> None:
        """
        Update voters message ID for a post.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID
            voters_message_id: Voters message ID
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            await self.db.update_voters_message(
                channel_id, channel_message_id, voters_message_id
            )
        except Exception as e:
            logger.error(f"Failed to update voters message: {e}")
            raise DatabaseError(f"Failed to update voters message: {e}")
    
    async def update_discussion_message(
        self,
        channel_id: int,
        channel_message_id: int,
        discussion_message_id: int,
    ) -> None:
        """
        Update discussion message ID for a post.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID
            discussion_message_id: Discussion message ID
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            await self.db.update_discussion_message_id(
                channel_id, channel_message_id, discussion_message_id
            )
        except Exception as e:
            logger.error(f"Failed to update discussion message: {e}")
            raise DatabaseError(f"Failed to update discussion message: {e}")
