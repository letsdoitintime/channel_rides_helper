"""Custom exceptions for the bot."""


class BotException(Exception):
    """Base exception for bot errors."""
    pass


class ConfigurationError(BotException):
    """Raised when configuration is invalid."""
    pass


class DatabaseError(BotException):
    """Raised when database operation fails."""
    pass


class RegistrationError(BotException):
    """Raised when registration creation or update fails."""
    pass


class PostNotFoundError(BotException):
    """Raised when a post is not found in the database."""
    pass


class VoteError(BotException):
    """Raised when a vote operation fails."""
    pass


class RateLimitError(BotException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, seconds_remaining: float):
        self.seconds_remaining = seconds_remaining
        super().__init__(f"Rate limit exceeded. Wait {seconds_remaining:.0f}s")
