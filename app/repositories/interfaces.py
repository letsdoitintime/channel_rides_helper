"""Abstract interfaces for repository operations."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

from app.domain.models import Post, Vote, VoteStatus, VoteCounts, RegistrationMode


class IPostRepository(ABC):
    """Interface for post repository operations."""
    
    @abstractmethod
    async def create(
        self,
        channel_id: int,
        channel_message_id: int,
        mode: RegistrationMode,
        registration_chat_id: Optional[int] = None,
        registration_message_id: Optional[int] = None,
        media_group_id: Optional[str] = None,
    ) -> bool:
        """Create a new post record."""
        pass
    
    @abstractmethod
    async def get(self, channel_id: int, channel_message_id: int) -> Optional[Post]:
        """Get post by channel_id and message_id."""
        pass
    
    @abstractmethod
    async def get_by_media_group(
        self, channel_id: int, media_group_id: str
    ) -> Optional[Post]:
        """Get post by media group ID."""
        pass
    
    @abstractmethod
    async def update_registration(
        self,
        channel_id: int,
        channel_message_id: int,
        registration_chat_id: int,
        registration_message_id: int,
    ) -> None:
        """Update registration message info for a post."""
        pass
    
    @abstractmethod
    async def update_voters_message(
        self,
        channel_id: int,
        channel_message_id: int,
        voters_message_id: int,
    ) -> None:
        """Update voters message ID for a post."""
        pass
    
    @abstractmethod
    async def update_discussion_message(
        self,
        channel_id: int,
        channel_message_id: int,
        discussion_message_id: int,
    ) -> None:
        """Update discussion message ID for a post."""
        pass


class IVoteRepository(ABC):
    """Interface for vote repository operations."""
    
    @abstractmethod
    async def upsert(
        self,
        channel_id: int,
        channel_message_id: int,
        user_id: int,
        status: VoteStatus,
    ) -> None:
        """Insert or update a vote."""
        pass
    
    @abstractmethod
    async def get_counts(
        self, channel_id: int, channel_message_id: int
    ) -> VoteCounts:
        """Get vote counts by status."""
        pass
    
    @abstractmethod
    async def get_voters_by_status(
        self, channel_id: int, channel_message_id: int
    ) -> Dict[VoteStatus, List[int]]:
        """Get list of voter user_ids grouped by status."""
        pass
    
    @abstractmethod
    async def get_last_vote_time(
        self, channel_id: int, channel_message_id: int, user_id: int
    ) -> Optional[datetime]:
        """Get the last vote time for a user on a specific post."""
        pass
