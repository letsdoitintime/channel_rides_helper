"""Admin command handlers."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from app.db import Database
from app.config import Config
from app.utils.message_parser import parse_message_link
from app.utils.user_formatter import format_user_name


router = Router()


def is_admin(user_id: int, config: Config) -> bool:
    """Check if user is an admin."""
    return user_id in config.admin_user_ids


def setup_admin_commands(db: Database, config: Config):
    """Setup admin command handlers."""
    
    @router.message(Command("ping"))
    async def cmd_ping(message: Message):
        """Ping command to check if bot is alive."""
        if not is_admin(message.from_user.id, config):
            await message.reply("⛔ This command is for admins only.")
            return
        
        await message.reply("🏓 Pong! Bot is running.")
    
    @router.message(Command("voters"))
    async def cmd_voters(message: Message):
        """Show voters for a specific post."""
        if not is_admin(message.from_user.id, config):
            await message.reply("⛔ This command is for admins only.")
            return
        
        # Parse command arguments
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply(
                "Usage:\n"
                "/voters <message_id> - for current channel\n"
                "/voters <t.me link> - for any channel"
            )
            return
        
        arg = args[1].strip()
        
        # Try to parse as link first
        parsed = parse_message_link(arg)
        if parsed:
            channel_id, message_id = parsed
        else:
            # Try to parse as message_id for current channel
            try:
                message_id = int(arg)
                channel_id = config.rides_channel_id
            except ValueError:
                await message.reply(
                    "❌ Invalid format. Please provide:\n"
                    "- A message ID (number)\n"
                    "- A t.me/c/... link"
                )
                return
        
        # Get voters
        try:
            voters = await db.get_voters_by_status(channel_id, message_id)
            counts = await db.get_vote_counts(channel_id, message_id)
            changed_mind = await db.get_changed_mind_count(channel_id, message_id)
            
            # Build response
            text = f"👥 **Voters for message {message_id}**\n\n"
            text += f"📊 **Summary:**\n"
            text += f"✅ Join: {counts['join']}\n"
            text += f"❔ Maybe: {counts['maybe']}\n"
            text += f"❌ Decline: {counts['decline']}\n"
            
            if changed_mind > 0:
                text += f"🔁 Changed mind: {changed_mind}\n"
            
            text += "\n"
            
            # List voters by status
            if voters["join"]:
                text += f"✅ **Join ({len(voters['join'])})**\n"
                for user_id in voters["join"]:
                    name = await format_user_name(message.bot, user_id, include_username=True)
                    text += f"  • {name}\n"
                text += "\n"
            
            if voters["maybe"]:
                text += f"❔ **Maybe ({len(voters['maybe'])})**\n"
                for user_id in voters["maybe"]:
                    name = await format_user_name(message.bot, user_id, include_username=True)
                    text += f"  • {name}\n"
                text += "\n"
            
            if voters["decline"]:
                text += f"❌ **Decline ({len(voters['decline'])})**\n"
                for user_id in voters["decline"]:
                    name = await format_user_name(message.bot, user_id, include_username=True)
                    text += f"  • {name}\n"
                text += "\n"
            
            if not any(voters.values()):
                text += "_No votes yet for this post_"
            
            await message.reply(text, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Error fetching voters: {e}", exc_info=True)
            await message.reply(f"❌ Error fetching voters: {e}")
    
    return router
