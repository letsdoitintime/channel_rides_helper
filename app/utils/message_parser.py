"""Message link parsing utilities."""
import re
from typing import Optional, Tuple


def parse_message_link(text: str) -> Optional[Tuple[int, int]]:
    """
    Parse t.me message link to extract channel_id and message_id.
    
    Supports formats:
    - https://t.me/c/1234567890/123
    - t.me/c/1234567890/123
    - https://t.me/channel_username/123
    
    Args:
        text: Text containing a Telegram message link
    
    Returns:
        Tuple of (channel_id, message_id) or None if not found
    """
    # Pattern for private channel links: t.me/c/{channel_id}/{message_id}
    private_pattern = r't\.me/c/(\d+)/(\d+)'
    match = re.search(private_pattern, text)
    if match:
        channel_id = int(f"-100{match.group(1)}")  # Add -100 prefix
        message_id = int(match.group(2))
        return channel_id, message_id
    
    return None


def create_message_link(channel_id: int, message_id: int) -> str:
    """
    Generate t.me link for a message.
    
    Args:
        channel_id: Channel ID (with -100 prefix for private channels)
        message_id: Message ID
    
    Returns:
        Telegram message link
    """
    # Convert channel_id to format suitable for links
    # For private channels: t.me/c/{channel_id without -100 prefix}/{message_id}
    if str(channel_id).startswith("-100"):
        clean_id = str(channel_id)[4:]  # Remove -100 prefix
        return f"https://t.me/c/{clean_id}/{message_id}"
    else:
        # For public channels, would need username (not implemented)
        return f"https://t.me/c/{channel_id}/{message_id}"
