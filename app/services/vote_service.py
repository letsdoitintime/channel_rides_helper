"""Vote service for handling vote operations."""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from loguru import logger

from app.db import Database
from app.domain.models import VoteStatus, VoteCounts
from app.repositories.vote_repository import VoteRepository
from app.exceptions import RateLimitError, VoteError


class VoteService:
    """Service for managing vote operations."""
    
    def __init__(self, db: Database, vote_cooldown: int = 1):
        """
        Initialize vote service.
        
        Args:
            db: Database instance
            vote_cooldown: Minimum seconds between votes (default: 1)
        """
        self.db = db
        self.vote_repository = VoteRepository(db)
        self.vote_cooldown = vote_cooldown
    
    async def cast_vote(
        self,
        channel_id: int,
        message_id: int,
        user_id: int,
        status: VoteStatus,
    ) -> None:
        """
        Cast a vote with rate limiting check.
        
        Args:
            channel_id: Channel ID
            message_id: Message ID
            user_id: User ID
            status: Vote status
        
        Raises:
            RateLimitError: If vote is too soon after last vote
            VoteError: If vote operation fails
        """
        try:
            # Check rate limiting
            if self.vote_cooldown > 0:
                await self._check_rate_limit(channel_id, message_id, user_id)
            
            # Cast the vote
            await self.vote_repository.upsert(
                channel_id, message_id, user_id, status
            )
            
            logger.info(
                f"Vote cast: user={user_id}, post={channel_id}/{message_id}, "
                f"status={status.value}"
            )
            
        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"Failed to cast vote: {e}", exc_info=True)
            raise VoteError(f"Failed to cast vote: {e}")
    
    async def get_vote_counts(
        self, channel_id: int, message_id: int
    ) -> VoteCounts:
        """
        Get vote counts for a post.
        
        Args:
            channel_id: Channel ID
            message_id: Message ID
        
        Returns:
            VoteCounts object with statistics
        """
        return await self.vote_repository.get_counts(channel_id, message_id)
    
    async def get_voters_by_status(
        self, channel_id: int, message_id: int
    ) -> Dict[VoteStatus, List[int]]:
        """
        Get voters grouped by status.
        
        Args:
            channel_id: Channel ID
            message_id: Message ID
        
        Returns:
            Dictionary mapping VoteStatus to list of user IDs
        """
        return await self.vote_repository.get_voters_by_status(channel_id, message_id)
    
    async def user_has_voted(
        self, channel_id: int, message_id: int, user_id: int
    ) -> bool:
        """
        Check if user has voted on a post.
        
        Args:
            channel_id: Channel ID
            message_id: Message ID
            user_id: User ID
        
        Returns:
            True if user has voted, False otherwise
        """
        # Check if user has a vote by checking last vote time
        last_vote_time = await self.vote_repository.get_last_vote_time(
            channel_id, message_id, user_id
        )
        return last_vote_time is not None
    
    async def _check_rate_limit(
        self, channel_id: int, message_id: int, user_id: int
    ) -> None:
        """
        Check if user is rate limited.
        
        Args:
            channel_id: Channel ID
            message_id: Message ID
            user_id: User ID
        
        Raises:
            RateLimitError: If vote is too soon after last vote
        """
        last_vote = await self.vote_repository.get_last_vote_time(
            channel_id, message_id, user_id
        )
        
        if last_vote:
            time_since_last = datetime.now(timezone.utc) - last_vote
            if time_since_last < timedelta(seconds=self.vote_cooldown):
                remaining = self.vote_cooldown - time_since_last.total_seconds()
                raise RateLimitError(remaining)
