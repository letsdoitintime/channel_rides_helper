"""Tests for vote service."""
import pytest
from datetime import datetime, timezone, timedelta

from app.services.vote_service import VoteService
from app.domain.models import VoteStatus
from app.exceptions import RateLimitError, VoteError


@pytest.mark.asyncio
async def test_cast_vote_success(temp_db):
    """Test casting a vote successfully."""
    vote_service = VoteService(temp_db, vote_cooldown=0)
    
    await vote_service.cast_vote(
        channel_id=-1001234567890,
        message_id=123,
        user_id=111,
        status=VoteStatus.JOIN,
    )
    
    # Verify vote was recorded
    vote = await temp_db.get_vote(-1001234567890, 123, 111)
    assert vote is not None
    assert vote["status"] == "join"


@pytest.mark.asyncio
async def test_cast_vote_with_rate_limiting(temp_db):
    """Test rate limiting when casting votes."""
    vote_service = VoteService(temp_db, vote_cooldown=5)
    
    # First vote should succeed
    await vote_service.cast_vote(
        channel_id=-1001234567890,
        message_id=123,
        user_id=111,
        status=VoteStatus.JOIN,
    )
    
    # Second vote immediately should fail
    with pytest.raises(RateLimitError) as exc_info:
        await vote_service.cast_vote(
            channel_id=-1001234567890,
            message_id=123,
            user_id=111,
            status=VoteStatus.MAYBE,
        )
    
    assert exc_info.value.seconds_remaining > 0


@pytest.mark.asyncio
async def test_cast_vote_no_rate_limit_for_different_posts(temp_db):
    """Test that rate limiting is per-post."""
    vote_service = VoteService(temp_db, vote_cooldown=5)
    
    # Vote on first post
    await vote_service.cast_vote(
        channel_id=-1001234567890,
        message_id=123,
        user_id=111,
        status=VoteStatus.JOIN,
    )
    
    # Vote on different post should succeed
    await vote_service.cast_vote(
        channel_id=-1001234567890,
        message_id=124,
        user_id=111,
        status=VoteStatus.JOIN,
    )
    
    # Both votes should be recorded
    vote1 = await temp_db.get_vote(-1001234567890, 123, 111)
    vote2 = await temp_db.get_vote(-1001234567890, 124, 111)
    assert vote1 is not None
    assert vote2 is not None


@pytest.mark.asyncio
async def test_get_vote_counts(temp_db):
    """Test getting vote counts."""
    vote_service = VoteService(temp_db, vote_cooldown=0)
    
    # Cast multiple votes
    await vote_service.cast_vote(-1001234567890, 123, 111, VoteStatus.JOIN)
    await vote_service.cast_vote(-1001234567890, 123, 222, VoteStatus.JOIN)
    await vote_service.cast_vote(-1001234567890, 123, 333, VoteStatus.MAYBE)
    await vote_service.cast_vote(-1001234567890, 123, 444, VoteStatus.DECLINE)
    
    # Get counts
    counts = await vote_service.get_vote_counts(-1001234567890, 123)
    
    assert counts.join == 2
    assert counts.maybe == 1
    assert counts.decline == 1
    assert counts.total == 4


@pytest.mark.asyncio
async def test_get_voters_by_status(temp_db):
    """Test getting voters grouped by status."""
    vote_service = VoteService(temp_db, vote_cooldown=0)
    
    # Cast votes
    await vote_service.cast_vote(-1001234567890, 123, 111, VoteStatus.JOIN)
    await vote_service.cast_vote(-1001234567890, 123, 222, VoteStatus.JOIN)
    await vote_service.cast_vote(-1001234567890, 123, 333, VoteStatus.MAYBE)
    
    # Get voters
    voters = await vote_service.get_voters_by_status(-1001234567890, 123)
    
    assert VoteStatus.JOIN in voters
    assert VoteStatus.MAYBE in voters
    assert VoteStatus.DECLINE in voters
    
    assert 111 in voters[VoteStatus.JOIN]
    assert 222 in voters[VoteStatus.JOIN]
    assert 333 in voters[VoteStatus.MAYBE]


@pytest.mark.asyncio
async def test_user_has_voted(temp_db):
    """Test checking if user has voted."""
    vote_service = VoteService(temp_db, vote_cooldown=0)
    
    # User hasn't voted yet
    has_voted = await vote_service.user_has_voted(-1001234567890, 123, 111)
    assert has_voted is False
    
    # User votes
    await vote_service.cast_vote(-1001234567890, 123, 111, VoteStatus.JOIN)
    
    # User has now voted
    has_voted = await vote_service.user_has_voted(-1001234567890, 123, 111)
    assert has_voted is True


@pytest.mark.asyncio
async def test_changed_mind_tracking(temp_db):
    """Test that changed mind count is tracked in vote counts."""
    vote_service = VoteService(temp_db, vote_cooldown=0)
    
    # User votes join
    await vote_service.cast_vote(-1001234567890, 123, 111, VoteStatus.JOIN)
    
    # User changes to maybe
    await vote_service.cast_vote(-1001234567890, 123, 111, VoteStatus.MAYBE)
    
    # Get counts
    counts = await vote_service.get_vote_counts(-1001234567890, 123)
    
    assert counts.join == 0
    assert counts.maybe == 1
    assert counts.changed_mind == 1
