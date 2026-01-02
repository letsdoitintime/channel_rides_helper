"""Tests for database layer."""
import pytest
from datetime import datetime

from app.db import Database


@pytest.mark.asyncio
async def test_database_connection(temp_db):
    """Test database connection."""
    assert temp_db.conn is not None


@pytest.mark.asyncio
async def test_create_post(temp_db):
    """Test creating a post."""
    success = await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=123,
        mode="edit_channel",
    )
    assert success is True
    
    # Try to create duplicate - should fail
    success = await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=123,
        mode="edit_channel",
    )
    assert success is False


@pytest.mark.asyncio
async def test_get_post(temp_db):
    """Test retrieving a post."""
    await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=456,
        mode="discussion_thread",
        registration_chat_id=-1009876543210,
        registration_message_id=789,
    )
    
    post = await temp_db.get_post(-1001234567890, 456)
    assert post is not None
    assert post["channel_id"] == -1001234567890
    assert post["channel_message_id"] == 456
    assert post["mode"] == "discussion_thread"
    assert post["registration_chat_id"] == -1009876543210
    assert post["registration_message_id"] == 789


@pytest.mark.asyncio
async def test_upsert_vote(temp_db):
    """Test inserting and updating votes."""
    # Create a post first
    await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=100,
        mode="edit_channel",
    )
    
    # Insert vote
    await temp_db.upsert_vote(-1001234567890, 100, 111, "join")
    
    # Check vote counts
    counts = await temp_db.get_vote_counts(-1001234567890, 100)
    assert counts["join"] == 1
    assert counts["maybe"] == 0
    assert counts["decline"] == 0
    
    # Update vote to "maybe"
    await temp_db.upsert_vote(-1001234567890, 100, 111, "maybe")
    
    counts = await temp_db.get_vote_counts(-1001234567890, 100)
    assert counts["join"] == 0
    assert counts["maybe"] == 1
    assert counts["decline"] == 0


@pytest.mark.asyncio
async def test_ever_joined_logic(temp_db):
    """Test ever_joined tracking."""
    await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=200,
        mode="edit_channel",
    )
    
    # User votes "join"
    await temp_db.upsert_vote(-1001234567890, 200, 222, "join")
    
    # Changed mind count should be 0
    changed_mind = await temp_db.get_changed_mind_count(-1001234567890, 200)
    assert changed_mind == 0
    
    # User changes to "maybe"
    await temp_db.upsert_vote(-1001234567890, 200, 222, "maybe")
    
    # Now changed mind should be 1
    changed_mind = await temp_db.get_changed_mind_count(-1001234567890, 200)
    assert changed_mind == 1
    
    # User changes to "decline"
    await temp_db.upsert_vote(-1001234567890, 200, 222, "decline")
    
    # Still 1 (same user)
    changed_mind = await temp_db.get_changed_mind_count(-1001234567890, 200)
    assert changed_mind == 1


@pytest.mark.asyncio
async def test_voters_by_status(temp_db):
    """Test getting voters grouped by status."""
    await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=300,
        mode="edit_channel",
    )
    
    # Add multiple votes
    await temp_db.upsert_vote(-1001234567890, 300, 111, "join")
    await temp_db.upsert_vote(-1001234567890, 300, 222, "join")
    await temp_db.upsert_vote(-1001234567890, 300, 333, "maybe")
    await temp_db.upsert_vote(-1001234567890, 300, 444, "decline")
    
    voters = await temp_db.get_voters_by_status(-1001234567890, 300)
    
    assert len(voters["join"]) == 2
    assert 111 in voters["join"]
    assert 222 in voters["join"]
    assert len(voters["maybe"]) == 1
    assert 333 in voters["maybe"]
    assert len(voters["decline"]) == 1
    assert 444 in voters["decline"]


@pytest.mark.asyncio
async def test_media_group_handling(temp_db):
    """Test media group (album) handling."""
    # Create first post in album
    await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=400,
        mode="edit_channel",
        media_group_id="album_123",
    )
    
    # Try to get by media_group_id
    post = await temp_db.get_post_by_media_group(-1001234567890, "album_123")
    assert post is not None
    assert post["channel_message_id"] == 400
    assert post["media_group_id"] == "album_123"
    
    # Create another post in the same album
    await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=401,
        mode="edit_channel",
        media_group_id="album_123",
    )
    
    # Should still get the first post
    post = await temp_db.get_post_by_media_group(-1001234567890, "album_123")
    assert post["channel_message_id"] == 400


@pytest.mark.asyncio
async def test_vote_rate_limiting(temp_db):
    """Test getting last vote time for rate limiting."""
    await temp_db.create_post(
        channel_id=-1001234567890,
        channel_message_id=500,
        mode="edit_channel",
    )
    
    # First vote
    await temp_db.upsert_vote(-1001234567890, 500, 555, "join")
    
    # Get last vote time
    last_vote = await temp_db.get_last_vote_time(-1001234567890, 500, 555)
    assert last_vote is not None
    assert isinstance(last_vote, datetime)
    
    # Non-existent vote should return None
    last_vote = await temp_db.get_last_vote_time(-1001234567890, 500, 999)
    assert last_vote is None
