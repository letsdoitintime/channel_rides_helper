"""Test configuration."""
import pytest
import asyncio
from pathlib import Path
import tempfile
import os

from app.config import Config
from app.db import Database


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    db = Database(db_path)
    await db.connect()
    
    yield db
    
    await db.close()
    
    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def test_config():
    """Create a test configuration."""
    # Set minimal environment variables for testing
    os.environ["BOT_TOKEN"] = "test_token_123456789"
    os.environ["RIDES_CHANNEL_ID"] = "-1001234567890"
    os.environ["DISCUSSION_GROUP_ID"] = "-1009876543210"
    os.environ["REGISTRATION_MODE"] = "edit_channel"
    os.environ["RIDE_FILTER"] = "hashtag"
    os.environ["RIDE_HASHTAGS"] = "#ride,#test"
    os.environ["ADMIN_USER_IDS"] = "123456789,987654321"
    
    return Config.from_env()
