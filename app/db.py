"""Database layer for the bot."""
import aiosqlite
from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple
from loguru import logger


class Database:
    """SQLite database manager."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        """Connect to the database and initialize schema."""
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await self._init_schema()
        logger.info(f"Database connected: {self.db_path}")
    
    async def close(self):
        """Close database connection."""
        if self.conn:
            await self.conn.close()
            logger.info("Database connection closed")
    
    async def _init_schema(self):
        """Initialize database schema."""
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                channel_id INTEGER NOT NULL,
                channel_message_id INTEGER NOT NULL,
                mode TEXT NOT NULL,
                registration_chat_id INTEGER,
                registration_message_id INTEGER,
                voters_message_id INTEGER,
                discussion_message_id INTEGER,
                media_group_id TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(channel_id, channel_message_id)
            )
        """)
        
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                channel_id INTEGER NOT NULL,
                channel_message_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                first_status TEXT NOT NULL,
                ever_joined INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL,
                UNIQUE(channel_id, channel_message_id, user_id)
            )
        """)
        
        # Create indexes for performance
        await self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_votes_user ON votes(user_id)
        """)
        
        await self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_votes_status ON votes(status)
        """)
        
        await self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at)
        """)
        
        await self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_media_group ON posts(media_group_id)
        """)
        
        await self.conn.commit()
        logger.info("Database schema initialized")
    
    # Posts operations
    
    async def create_post(
        self,
        channel_id: int,
        channel_message_id: int,
        mode: str,
        registration_chat_id: Optional[int] = None,
        registration_message_id: Optional[int] = None,
        media_group_id: Optional[str] = None,
    ) -> bool:
        """Create a new post record."""
        try:
            await self.conn.execute(
                """
                INSERT INTO posts (
                    channel_id, channel_message_id, mode,
                    registration_chat_id, registration_message_id,
                    media_group_id, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    channel_id,
                    channel_message_id,
                    mode,
                    registration_chat_id,
                    registration_message_id,
                    media_group_id,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            await self.conn.commit()
            return True
        except aiosqlite.IntegrityError:
            logger.warning(f"Post already exists: {channel_id}/{channel_message_id}")
            return False
    
    async def get_post(
        self, channel_id: int, channel_message_id: int
    ) -> Optional[Dict]:
        """Get post by channel_id and channel_message_id."""
        async with self.conn.execute(
            """
            SELECT * FROM posts
            WHERE channel_id = ? AND channel_message_id = ?
            """,
            (channel_id, channel_message_id),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_post_by_media_group(
        self, channel_id: int, media_group_id: str
    ) -> Optional[Dict]:
        """Get post by media_group_id (for album handling)."""
        async with self.conn.execute(
            """
            SELECT * FROM posts
            WHERE channel_id = ? AND media_group_id = ?
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (channel_id, media_group_id),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_post_registration(
        self,
        channel_id: int,
        channel_message_id: int,
        registration_chat_id: int,
        registration_message_id: int,
    ):
        """Update registration message info for a post."""
        await self.conn.execute(
            """
            UPDATE posts
            SET registration_chat_id = ?, registration_message_id = ?
            WHERE channel_id = ? AND channel_message_id = ?
            """,
            (registration_chat_id, registration_message_id, channel_id, channel_message_id),
        )
        await self.conn.commit()
    
    async def update_voters_message(
        self,
        channel_id: int,
        channel_message_id: int,
        voters_message_id: int,
    ):
        """Update voters message ID for a post."""
        await self.conn.execute(
            """
            UPDATE posts
            SET voters_message_id = ?
            WHERE channel_id = ? AND channel_message_id = ?
            """,
            (voters_message_id, channel_id, channel_message_id),
        )
        await self.conn.commit()
    
    async def update_discussion_message_id(
        self,
        channel_id: int,
        channel_message_id: int,
        discussion_message_id: int,
    ):
        """Update discussion message ID for a post."""
        await self.conn.execute(
            """
            UPDATE posts
            SET discussion_message_id = ?
            WHERE channel_id = ? AND channel_message_id = ?
            """,
            (discussion_message_id, channel_id, channel_message_id),
        )
        await self.conn.commit()
    
    # Votes operations
    
    async def upsert_vote(
        self,
        channel_id: int,
        channel_message_id: int,
        user_id: int,
        status: str,
    ):
        """Insert or update a vote."""
        # First, check if vote exists
        async with self.conn.execute(
            """
            SELECT first_status, ever_joined FROM votes
            WHERE channel_id = ? AND channel_message_id = ? AND user_id = ?
            """,
            (channel_id, channel_message_id, user_id),
        ) as cursor:
            existing = await cursor.fetchone()
        
        if existing:
            # Update existing vote
            ever_joined = existing["ever_joined"] or (status == "join")
            await self.conn.execute(
                """
                UPDATE votes
                SET status = ?, ever_joined = ?, updated_at = ?
                WHERE channel_id = ? AND channel_message_id = ? AND user_id = ?
                """,
                (
                    status,
                    1 if ever_joined else 0,
                    datetime.now(timezone.utc).isoformat(),
                    channel_id,
                    channel_message_id,
                    user_id,
                ),
            )
        else:
            # Insert new vote
            ever_joined = 1 if status == "join" else 0
            await self.conn.execute(
                """
                INSERT INTO votes (
                    channel_id, channel_message_id, user_id,
                    status, first_status, ever_joined, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    channel_id,
                    channel_message_id,
                    user_id,
                    status,
                    status,  # first_status = current status for new votes
                    ever_joined,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        
        await self.conn.commit()
    
    async def get_vote_counts(
        self, channel_id: int, channel_message_id: int
    ) -> Dict[str, int]:
        """Get vote counts by status."""
        async with self.conn.execute(
            """
            SELECT status, COUNT(*) as count
            FROM votes
            WHERE channel_id = ? AND channel_message_id = ?
            GROUP BY status
            """,
            (channel_id, channel_message_id),
        ) as cursor:
            rows = await cursor.fetchall()
        
        counts = {"join": 0, "maybe": 0, "decline": 0}
        for row in rows:
            counts[row["status"]] = row["count"]
        
        return counts
    
    async def get_changed_mind_count(
        self, channel_id: int, channel_message_id: int
    ) -> int:
        """Get count of users who ever joined but current status != join."""
        async with self.conn.execute(
            """
            SELECT COUNT(*) as count
            FROM votes
            WHERE channel_id = ? AND channel_message_id = ?
            AND ever_joined = 1 AND status != 'join'
            """,
            (channel_id, channel_message_id),
        ) as cursor:
            row = await cursor.fetchone()
            return row["count"] if row else 0
    
    async def get_voters_by_status(
        self, channel_id: int, channel_message_id: int
    ) -> Dict[str, List[int]]:
        """Get list of voter user_ids grouped by status."""
        async with self.conn.execute(
            """
            SELECT status, user_id
            FROM votes
            WHERE channel_id = ? AND channel_message_id = ?
            ORDER BY status, updated_at
            """,
            (channel_id, channel_message_id),
        ) as cursor:
            rows = await cursor.fetchall()
        
        voters = {"join": [], "maybe": [], "decline": []}
        for row in rows:
            voters[row["status"]].append(row["user_id"])
        
        return voters
    
    async def get_last_vote_time(
        self, channel_id: int, channel_message_id: int, user_id: int
    ) -> Optional[datetime]:
        """Get the last vote time for a user on a specific post."""
        async with self.conn.execute(
            """
            SELECT updated_at FROM votes
            WHERE channel_id = ? AND channel_message_id = ? AND user_id = ?
            """,
            (channel_id, channel_message_id, user_id),
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return datetime.fromisoformat(row["updated_at"])
            return None
