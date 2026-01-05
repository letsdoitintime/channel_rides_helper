# Service Layer Architecture

## Overview

The service layer encapsulates business logic and orchestrates operations between repositories, domain models, and handlers. This provides a clear separation of concerns and makes the codebase more maintainable and testable.

## Services

### VoteService

**Location:** `app/services/vote_service.py`

**Purpose:** Manages all vote-related operations including casting votes, retrieving vote counts, and enforcing rate limiting.

**Key Methods:**
- `cast_vote()`: Cast a vote with automatic rate limiting
- `get_vote_counts()`: Get vote statistics for a post
- `get_voters_by_status()`: Get voters grouped by their vote status
- `user_has_voted()`: Check if a user has voted on a post

**Benefits:**
- Centralizes vote logic in one place
- Encapsulates rate limiting logic
- Provides clean API for handlers
- Easier to test in isolation

**Example Usage:**
```python
vote_service = VoteService(db, vote_cooldown=1)

# Cast a vote
try:
    await vote_service.cast_vote(
        channel_id=-1001234567890,
        message_id=123,
        user_id=111,
        status=VoteStatus.JOIN
    )
except RateLimitError as e:
    print(f"Wait {e.seconds_remaining}s")
```

### MessageFilterService

**Location:** `app/services/message_filter.py`

**Purpose:** Determines which messages should be processed based on configuration (hashtag filtering, bot messages, etc.).

**Key Methods:**
- `should_process()`: Check if a message should be processed
- `get_hashtags_from_message()`: Extract hashtags from a message

**Benefits:**
- Decouples filtering logic from handlers
- Makes filter rules explicit and testable
- Easy to extend with new filter types
- Consistent filtering across handlers

**Example Usage:**
```python
filter_service = MessageFilterService(
    ride_filter="hashtag",
    ride_hashtags=["#ride", "#cycling"]
)

if filter_service.should_process(message):
    # Process the message
    pass
```

### RegistrationService

**Location:** `app/services/registration.py`

**Purpose:** Manages registration card creation and updates across different posting modes.

**Key Features:**
- Creates registration cards with buttons
- Handles multiple registration modes (edit_channel, discussion_thread, channel_reply_post)
- Implements fallback chain for robustness
- Updates registration cards with current vote counts

**Benefits:**
- Centralized registration logic
- Handles complex mode switching
- Consistent button configuration
- Transaction-like behavior with fallbacks

## Architecture Pattern

### Layered Architecture

```
┌─────────────────────────────────────┐
│         Handlers Layer              │
│  (Callbacks, Channel, Admin)        │  ← Receive user input
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│        Services Layer               │
│  (VoteService, MessageFilter,       │  ← Business logic
│   RegistrationService)              │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      Repository Layer               │
│  (PostRepository, VoteRepository)   │  ← Data access
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│        Database Layer               │
│         (Database)                  │  ← Persistence
└─────────────────────────────────────┘
```

### Dependency Flow

1. **Handlers** depend on **Services**
2. **Services** depend on **Repositories** and **Domain Models**
3. **Repositories** depend on **Database** and **Domain Models**
4. **Domain Models** have no dependencies (pure business entities)

### Interface Segregation

Services and repositories implement abstract interfaces (ABC) for:
- Better testability (easy to mock)
- Loose coupling
- Contract-driven development
- Swappable implementations

Example:
```python
class IVoteRepository(ABC):
    @abstractmethod
    async def upsert(self, ...):
        pass
    
class VoteRepository(IVoteRepository):
    async def upsert(self, ...):
        # Implementation
```

## Design Principles Applied

### 1. Single Responsibility Principle (SRP)
Each service has one clear responsibility:
- `VoteService`: Vote operations
- `MessageFilterService`: Message filtering
- `RegistrationService`: Registration management

### 2. Open/Closed Principle (OCP)
Services are open for extension but closed for modification:
- New filter types can be added without changing existing code
- New vote types can be added by extending enums
- New registration modes follow the same interface

### 3. Dependency Inversion Principle (DIP)
High-level modules (handlers) depend on abstractions (services), not concrete implementations:
- Handlers receive service instances
- Services implement interfaces
- Easy to swap implementations for testing

### 4. Interface Segregation Principle (ISP)
Interfaces are client-specific:
- `IVoteRepository` for vote operations
- `IPostRepository` for post operations
- Clients only depend on methods they use

### 5. Don't Repeat Yourself (DRY)
Logic is centralized:
- Rate limiting logic in `VoteService`
- Filtering logic in `MessageFilterService`
- No duplication across handlers

## Testing Strategy

### Unit Tests
Services can be tested in isolation with mocked dependencies:

```python
@pytest.mark.asyncio
async def test_cast_vote_with_rate_limiting(temp_db):
    vote_service = VoteService(temp_db, vote_cooldown=5)
    
    # First vote succeeds
    await vote_service.cast_vote(...)
    
    # Second vote fails (rate limited)
    with pytest.raises(RateLimitError):
        await vote_service.cast_vote(...)
```

### Integration Tests
Test service interaction with real repositories:

```python
async def test_vote_service_integration(temp_db):
    vote_service = VoteService(temp_db)
    
    await vote_service.cast_vote(...)
    counts = await vote_service.get_vote_counts(...)
    
    assert counts.join == 1
```

## Benefits Summary

### Maintainability
- Clear separation of concerns
- Easy to locate and modify business logic
- Reduced code duplication
- Consistent patterns across codebase

### Testability
- Services can be tested in isolation
- Easy to mock dependencies
- Clear test boundaries
- High test coverage achievable

### Extensibility
- New services can be added without changing existing code
- New features follow established patterns
- Interface-based design allows swapping implementations

### Readability
- Handlers are simpler and focused on routing
- Business logic is explicit in service layer
- Code is self-documenting through clear interfaces

## Future Enhancements

1. **Service Registry/Container**: Implement dependency injection container for better dependency management

2. **Event-Driven Architecture**: Add event bus for loose coupling between services

3. **Caching Service**: Add caching layer for frequently accessed data

4. **Notification Service**: Centralize notification sending logic

5. **Analytics Service**: Track and report usage statistics

6. **Validation Service**: Centralize input validation logic

## Migration Guide

For existing code using direct database access:

**Before:**
```python
# Handler directly accessing database
await db.upsert_vote(channel_id, message_id, user_id, status)
counts = await db.get_vote_counts(channel_id, message_id)
```

**After:**
```python
# Handler using service layer
vote_service = VoteService(db, vote_cooldown)
await vote_service.cast_vote(channel_id, message_id, user_id, status)
counts = await vote_service.get_vote_counts(channel_id, message_id)
```

## Conclusion

The service layer provides a robust foundation for business logic, making the codebase more maintainable, testable, and extensible. By following SOLID principles and clean architecture patterns, the bot is well-positioned for future growth and enhancement.
