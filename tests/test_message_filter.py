"""Tests for message filter service."""
import pytest
from unittest.mock import Mock

from app.services.message_filter import MessageFilterService


def create_mock_message(text: str = "", is_bot: bool = False):
    """Create a mock Telegram message."""
    message = Mock()
    message.text = text
    message.caption = None
    message.from_user = Mock()
    message.from_user.is_bot = is_bot
    message.message_id = 123
    return message


def test_should_process_filter_all():
    """Test 'all' filter processes all messages."""
    service = MessageFilterService(ride_filter="all", ride_hashtags=[])
    
    message = create_mock_message("Just a regular message")
    assert service.should_process(message) is True


def test_should_process_skips_bot_messages():
    """Test that bot messages are skipped."""
    service = MessageFilterService(ride_filter="all", ride_hashtags=[])
    
    message = create_mock_message("Bot message", is_bot=True)
    assert service.should_process(message) is False


def test_should_process_hashtag_filter_matches():
    """Test hashtag filter matches messages with required hashtag."""
    service = MessageFilterService(
        ride_filter="hashtag",
        ride_hashtags=["#ride", "#велопокатушка"]
    )
    
    message = create_mock_message("Join us for a #ride tomorrow!")
    assert service.should_process(message) is True


def test_should_process_hashtag_filter_no_match():
    """Test hashtag filter skips messages without required hashtag."""
    service = MessageFilterService(
        ride_filter="hashtag",
        ride_hashtags=["#ride"]
    )
    
    message = create_mock_message("Just a regular message")
    assert service.should_process(message) is False


def test_should_process_hashtag_case_insensitive():
    """Test hashtag matching is case-insensitive."""
    service = MessageFilterService(
        ride_filter="hashtag",
        ride_hashtags=["#ride"]
    )
    
    message = create_mock_message("Join us for a #RIDE tomorrow!")
    assert service.should_process(message) is True
    
    message = create_mock_message("Join us for a #Ride tomorrow!")
    assert service.should_process(message) is True


def test_should_process_multiple_hashtags():
    """Test matching with multiple configured hashtags."""
    service = MessageFilterService(
        ride_filter="hashtag",
        ride_hashtags=["#ride", "#велопокатушка", "#cycling"]
    )
    
    # Message with first hashtag
    message = create_mock_message("Let's go for a #ride")
    assert service.should_process(message) is True
    
    # Message with second hashtag
    message = create_mock_message("Завтра #велопокатушка")
    assert service.should_process(message) is True
    
    # Message with third hashtag
    message = create_mock_message("Morning #cycling session")
    assert service.should_process(message) is True


def test_should_process_checks_caption():
    """Test that captions are also checked for hashtags."""
    service = MessageFilterService(
        ride_filter="hashtag",
        ride_hashtags=["#ride"]
    )
    
    message = create_mock_message()
    message.text = None
    message.caption = "Weekend #ride photo"
    
    assert service.should_process(message) is True


def test_get_hashtags_from_message():
    """Test extracting hashtags from message."""
    service = MessageFilterService(ride_filter="all", ride_hashtags=[])
    
    message = create_mock_message("Join #ride tomorrow #cycling #fun")
    hashtags = service.get_hashtags_from_message(message)
    
    assert "#ride" in hashtags
    assert "#cycling" in hashtags
    assert "#fun" in hashtags
    assert len(hashtags) == 3


def test_get_hashtags_from_empty_message():
    """Test extracting hashtags from empty message."""
    service = MessageFilterService(ride_filter="all", ride_hashtags=[])
    
    message = create_mock_message("")
    hashtags = service.get_hashtags_from_message(message)
    
    assert len(hashtags) == 0


def test_get_hashtags_from_caption():
    """Test extracting hashtags from caption."""
    service = MessageFilterService(ride_filter="all", ride_hashtags=[])
    
    message = create_mock_message()
    message.text = None
    message.caption = "Photo from #ride #cycling"
    
    hashtags = service.get_hashtags_from_message(message)
    
    assert "#ride" in hashtags
    assert "#cycling" in hashtags
    assert len(hashtags) == 2


def test_get_hashtags_with_punctuation():
    """Test that hashtags with punctuation are correctly extracted."""
    service = MessageFilterService(ride_filter="all", ride_hashtags=[])
    
    # Hashtags followed by punctuation should not include punctuation
    message = create_mock_message("Join #ride! and #cycling, it's #fun.")
    hashtags = service.get_hashtags_from_message(message)
    
    assert "#ride" in hashtags
    assert "#cycling" in hashtags
    assert "#fun" in hashtags
    assert "#ride!" not in hashtags
    assert "#cycling," not in hashtags
    assert len(hashtags) == 3
