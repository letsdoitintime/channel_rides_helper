"""Vote repository for managing vote data."""
from typing import Dict, List, Optional
from datetime import datetime

from app.db import Database
from app.domain.models import Vote, VoteStatus, VoteCounts
from app.exceptions import DatabaseError
from loguru import logger


class VoteRepository:
    """Repository for vote operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def upsert(
        self,
        channel_id: int,
        channel_message_id: int,
        user_id: int,
        status: VoteStatus,
    ) -> None:
        """
        Insert or update a vote.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID
            user_id: User ID
            status: Vote status
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            await self.db.upsert_vote(
                channel_id, channel_message_id, user_id, status.value
            )
        except Exception as e:
            logger.error(f"Failed to upsert vote: {e}")
            raise DatabaseError(f"Failed to upsert vote: {e}")
    
    async def get_counts(
        self, channel_id: int, channel_message_id: int
    ) -> VoteCounts:
        """
        Get vote counts by status.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID
        
        Returns:
            VoteCounts object with statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            counts = await self.db.get_vote_counts(channel_id, channel_message_id)
            changed_mind = await self.db.get_changed_mind_count(channel_id, channel_message_id)
            
            return VoteCounts(
                join=counts["join"],
                maybe=counts["maybe"],
                decline=counts["decline"],
                changed_mind=changed_mind,
            )
        except Exception as e:
            logger.error(f"Failed to get vote counts: {e}")
            raise DatabaseError(f"Failed to get vote counts: {e}")
    
    async def get_voters_by_status(
        self, channel_id: int, channel_message_id: int
    ) -> Dict[VoteStatus, List[int]]:
        """
        Get list of voter user_ids grouped by status.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID
        
        Returns:
            Dictionary mapping VoteStatus to list of user IDs
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            voters = await self.db.get_voters_by_status(channel_id, channel_message_id)
            
            return {
                VoteStatus.JOIN: voters["join"],
                VoteStatus.MAYBE: voters["maybe"],
                VoteStatus.DECLINE: voters["decline"],
            }
        except Exception as e:
            logger.error(f"Failed to get voters by status: {e}")
            raise DatabaseError(f"Failed to get voters by status: {e}")
    
    async def get_last_vote_time(
        self, channel_id: int, channel_message_id: int, user_id: int
    ) -> Optional[datetime]:
        """
        Get the last vote time for a user on a specific post.
        
        Args:
            channel_id: Channel ID
            channel_message_id: Message ID
            user_id: User ID
        
        Returns:
            Datetime of last vote or None if no vote exists
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return await self.db.get_last_vote_time(
                channel_id, channel_message_id, user_id
            )
        except Exception as e:
            logger.error(f"Failed to get last vote time: {e}")
            raise DatabaseError(f"Failed to get last vote time: {e}")
