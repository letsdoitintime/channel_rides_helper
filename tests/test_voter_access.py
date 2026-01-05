"""Tests for voter access control."""
import pytest
from app.db import Database


@pytest.mark.asyncio
async def test_get_vote_exists(tmp_path):
    """Test getting a vote that exists."""
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    await db.connect()
    
    # Create a post
    await db.create_post(
        channel_id=-1001234567890,
        channel_message_id=123,
        mode="edit_channel",
        registration_chat_id=-1001234567890,
        registration_message_id=123,
    )
    
    # Add a vote
    await db.upsert_vote(-1001234567890, 123, 100, "join")
    
    # Get the vote
    vote = await db.get_vote(-1001234567890, 123, 100)
    
    assert vote is not None
    assert vote["status"] == "join"
    assert vote["first_status"] == "join"
    assert vote["ever_joined"] == 1
    
    await db.close()


@pytest.mark.asyncio
async def test_get_vote_not_exists(tmp_path):
    """Test getting a vote that doesn't exist."""
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    await db.connect()
    
    # Create a post
    await db.create_post(
        channel_id=-1001234567890,
        channel_message_id=123,
        mode="edit_channel",
        registration_chat_id=-1001234567890,
        registration_message_id=123,
    )
    
    # Try to get a vote that doesn't exist
    vote = await db.get_vote(-1001234567890, 123, 999)
    
    assert vote is None
    
    await db.close()


@pytest.mark.asyncio
async def test_get_vote_changed_status(tmp_path):
    """Test getting a vote where user changed their mind."""
    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    await db.connect()
    
    # Create a post
    await db.create_post(
        channel_id=-1001234567890,
        channel_message_id=123,
        mode="edit_channel",
        registration_chat_id=-1001234567890,
        registration_message_id=123,
    )
    
    # Add a vote
    await db.upsert_vote(-1001234567890, 123, 100, "join")
    
    # Change vote
    await db.upsert_vote(-1001234567890, 123, 100, "decline")
    
    # Get the vote
    vote = await db.get_vote(-1001234567890, 123, 100)
    
    assert vote is not None
    assert vote["status"] == "decline"
    assert vote["first_status"] == "join"
    assert vote["ever_joined"] == 1
    
    await db.close()
