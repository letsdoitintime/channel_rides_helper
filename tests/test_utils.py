"""Tests for utility modules."""
import pytest
from app.utils.message_parser import parse_message_link, create_message_link


def test_parse_private_channel_link():
    """Test parsing private channel link."""
    link = "https://t.me/c/1234567890/123"
    result = parse_message_link(link)
    
    assert result is not None
    channel_id, message_id = result
    assert channel_id == -1001234567890
    assert message_id == 123


def test_parse_private_channel_link_without_https():
    """Test parsing private channel link without https."""
    link = "t.me/c/1234567890/456"
    result = parse_message_link(link)
    
    assert result is not None
    channel_id, message_id = result
    assert channel_id == -1001234567890
    assert message_id == 456


def test_parse_invalid_link():
    """Test parsing invalid link."""
    link = "https://example.com/test"
    result = parse_message_link(link)
    
    assert result is None


def test_create_message_link():
    """Test creating message link."""
    channel_id = -1001234567890
    message_id = 123
    
    link = create_message_link(channel_id, message_id)
    
    assert link == "https://t.me/c/1234567890/123"
    
    # Verify the link can be parsed back
    parsed = parse_message_link(link)
    assert parsed is not None
    assert parsed == (channel_id, message_id)


def test_create_message_link_public_channel():
    """Test creating message link for public channel (no -100 prefix)."""
    channel_id = -123456789
    message_id = 456
    
    link = create_message_link(channel_id, message_id)
    
    # For non -100 prefixed channels, it still creates a link
    assert "t.me/c/" in link
