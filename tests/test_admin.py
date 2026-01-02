"""Tests for admin commands."""
import pytest

from app.handlers.admin import parse_message_link


def test_parse_private_channel_link():
    """Test parsing private channel t.me/c/ links."""
    # Full HTTPS link
    result = parse_message_link("https://t.me/c/1234567890/123")
    assert result == (-1001234567890, 123)
    
    # Without https
    result = parse_message_link("t.me/c/1234567890/456")
    assert result == (-1001234567890, 456)
    
    # With other text
    result = parse_message_link("Check this out: https://t.me/c/9876543210/789 cool right?")
    assert result == (-1009876543210, 789)


def test_parse_invalid_link():
    """Test parsing invalid links."""
    result = parse_message_link("not a link")
    assert result is None
    
    result = parse_message_link("https://google.com")
    assert result is None
    
    result = parse_message_link("123456")
    assert result is None
