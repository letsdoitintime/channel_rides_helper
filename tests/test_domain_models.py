"""Tests for domain models."""
import pytest
from datetime import datetime, timezone

from app.domain.models import (
    VoteStatus, RegistrationMode, Post, Vote, VoteCounts
)


def test_vote_status_enum():
    """Test VoteStatus enumeration."""
    assert VoteStatus.JOIN.value == "join"
    assert VoteStatus.MAYBE.value == "maybe"
    assert VoteStatus.DECLINE.value == "decline"


def test_registration_mode_enum():
    """Test RegistrationMode enumeration."""
    assert RegistrationMode.EDIT_CHANNEL.value == "edit_channel"
    assert RegistrationMode.DISCUSSION_THREAD.value == "discussion_thread"
    assert RegistrationMode.CHANNEL_REPLY_POST.value == "channel_reply_post"


def test_post_from_dict():
    """Test creating Post from dictionary."""
    data = {
        "channel_id": -1001234567890,
        "channel_message_id": 123,
        "mode": "edit_channel",
        "registration_chat_id": -1001234567890,
        "registration_message_id": 124,
        "voters_message_id": None,
        "discussion_message_id": None,
        "media_group_id": "album_123",
        "created_at": "2024-01-01T12:00:00+00:00",
    }
    
    post = Post.from_dict(data)
    
    assert post.channel_id == -1001234567890
    assert post.channel_message_id == 123
    assert post.mode == RegistrationMode.EDIT_CHANNEL
    assert post.registration_chat_id == -1001234567890
    assert post.registration_message_id == 124
    assert post.media_group_id == "album_123"
    assert isinstance(post.created_at, datetime)


def test_vote_from_dict():
    """Test creating Vote from dictionary."""
    data = {
        "channel_id": -1001234567890,
        "channel_message_id": 123,
        "user_id": 12345,
        "status": "join",
        "first_status": "join",
        "ever_joined": 1,
        "updated_at": "2024-01-01T12:00:00+00:00",
    }
    
    vote = Vote.from_dict(data)
    
    assert vote.channel_id == -1001234567890
    assert vote.channel_message_id == 123
    assert vote.user_id == 12345
    assert vote.status == VoteStatus.JOIN
    assert vote.first_status == VoteStatus.JOIN
    assert vote.ever_joined is True
    assert isinstance(vote.updated_at, datetime)


def test_vote_counts():
    """Test VoteCounts model."""
    counts = VoteCounts(join=5, maybe=3, decline=2, changed_mind=1)
    
    assert counts.join == 5
    assert counts.maybe == 3
    assert counts.decline == 2
    assert counts.changed_mind == 1
    assert counts.total == 10


def test_vote_counts_default():
    """Test VoteCounts with default values."""
    counts = VoteCounts()
    
    assert counts.join == 0
    assert counts.maybe == 0
    assert counts.decline == 0
    assert counts.changed_mind == 0
    assert counts.total == 0
