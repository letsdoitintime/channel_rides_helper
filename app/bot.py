"""Main bot entry point."""
import asyncio
import signal
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from app.config import Config
from app.db import Database
from app.services.registration import RegistrationService
from app.handlers.channel_watcher import setup_channel_watcher
from app.handlers.callbacks import setup_callbacks
from app.handlers.admin import setup_admin_commands


# Global references for cleanup
bot: Bot = None
db: Database = None
dp: Dispatcher = None


def setup_logging(config: Config):
    """Setup logging configuration."""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.log_level,
    )
    
    # Add file handler
    log_file_path = Path(config.log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        config.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=config.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info("Logging configured")


async def on_startup():
    """Run on bot startup."""
    logger.info("Bot is starting up...")
    logger.info(f"Monitoring channel: {config.rides_channel_id}")
    logger.info(f"Registration mode: {config.registration_mode}")
    logger.info(f"Ride filter: {config.ride_filter}")


async def on_shutdown():
    """Run on bot shutdown."""
    logger.info("Bot is shutting down...")
    
    if db:
        await db.close()
    
    if bot:
        await bot.session.close()
    
    logger.info("Bot shutdown complete")


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {sig}, initiating graceful shutdown...")
    asyncio.create_task(shutdown())


async def shutdown():
    """Graceful shutdown."""
    await on_shutdown()
    sys.exit(0)


async def main():
    """Main bot function."""
    global bot, db, dp, config
    
    try:
        # Load configuration
        config = Config.from_env()
        
        # Setup logging
        setup_logging(config)
        
        # Initialize database
        db_path = Path(config.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        db = Database(config.database_path)
        await db.connect()
        
        # Initialize bot
        bot = Bot(
            token=config.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        
        # Initialize dispatcher
        dp = Dispatcher()
        
        # Initialize services
        registration_service = RegistrationService(bot, db, config)
        
        # Setup handlers
        channel_watcher_router = setup_channel_watcher(db, config, registration_service)
        callbacks_router = setup_callbacks(db, config, registration_service)
        admin_router = setup_admin_commands(db, config)
        
        # Include routers
        dp.include_router(channel_watcher_router)
        dp.include_router(callbacks_router)
        dp.include_router(admin_router)
        
        # Register startup/shutdown handlers
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
    finally:
        await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)
