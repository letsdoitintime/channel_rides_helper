"""Domain models for the bot."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class VoteStatus(Enum):
    """Vote status enumeration."""
    JOIN = "join"
    MAYBE = "maybe"
    DECLINE = "decline"


class RegistrationMode(Enum):
    """Registration mode enumeration."""
    EDIT_CHANNEL = "edit_channel"
    DISCUSSION_THREAD = "discussion_thread"
    CHANNEL_REPLY_POST = "channel_reply_post"


@dataclass
class Post:
    """Domain model for a post registration."""
    channel_id: int
    channel_message_id: int
    mode: RegistrationMode
    registration_chat_id: Optional[int] = None
    registration_message_id: Optional[int] = None
    voters_message_id: Optional[int] = None
    discussion_message_id: Optional[int] = None
    media_group_id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Post":
        """Create Post from database row dictionary."""
        mode_str = data.get("mode")
        mode = RegistrationMode(mode_str) if mode_str else RegistrationMode.EDIT_CHANNEL
        
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            channel_id=data["channel_id"],
            channel_message_id=data["channel_message_id"],
            mode=mode,
            registration_chat_id=data.get("registration_chat_id"),
            registration_message_id=data.get("registration_message_id"),
            voters_message_id=data.get("voters_message_id"),
            discussion_message_id=data.get("discussion_message_id"),
            media_group_id=data.get("media_group_id"),
            created_at=created_at,
        )


@dataclass
class Vote:
    """Domain model for a vote."""
    channel_id: int
    channel_message_id: int
    user_id: int
    status: VoteStatus
    first_status: VoteStatus
    ever_joined: bool
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict) -> "Vote":
        """Create Vote from database row dictionary."""
        status = VoteStatus(data["status"])
        first_status = VoteStatus(data["first_status"])
        
        updated_at = data["updated_at"]
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            channel_id=data["channel_id"],
            channel_message_id=data["channel_message_id"],
            user_id=data["user_id"],
            status=status,
            first_status=first_status,
            ever_joined=bool(data["ever_joined"]),
            updated_at=updated_at,
        )


@dataclass
class VoteCounts:
    """Vote count statistics."""
    join: int = 0
    maybe: int = 0
    decline: int = 0
    changed_mind: int = 0
    
    @property
    def total(self) -> int:
        """Total number of votes."""
        return self.join + self.maybe + self.decline
