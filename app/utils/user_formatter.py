"""User information formatting utilities."""
from typing import Optional
from aiogram import Bot
from loguru import logger


async def format_user_name(bot: Bot, user_id: int, include_username: bool = False) -> str:
    """
    Format user name with optional username.
    
    Args:
        bot: Bot instance for fetching user info
        user_id: User ID
        include_username: Whether to include @username
    
    Returns:
        Formatted user name
    """
    try:
        user = await bot.get_chat(user_id)
        name = user.full_name or user.username or f"User {user_id}"
        
        if include_username and user.username:
            return f"{name} @{user.username}"
        return name
    except Exception as e:
        logger.debug(f"Could not fetch user {user_id}: {e}")
        return f"User {user_id}"


async def format_user_list(bot: Bot, user_ids: list[int], include_usernames: bool = False) -> list[str]:
    """
    Format a list of user IDs into formatted names.
    
    Args:
        bot: Bot instance for fetching user info
        user_ids: List of user IDs
        include_usernames: Whether to include @username
    
    Returns:
        List of formatted user names
    """
    formatted = []
    for user_id in user_ids:
        name = await format_user_name(bot, user_id, include_usernames)
        formatted.append(name)
    return formatted
