import logging
import asyncio
from aiogram import Bot, Dispatcher

from config import Settings
from src.tracker.traker_services.traker import start_tracking, stop_tracking
from src.common import register_common_handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    logger.info("🚀 Bot starting up...")
    logger.info(f"📁 Tracking repository: {Settings.GITHUB_REPO}")
    logger.info(f"👥 Notification recipients: {len(Settings.CHAT_IDS)} users")
    
    # Запускаем отслеживание
    asyncio.create_task(start_tracking(bot))


async def on_shutdown(bot: Bot):
    logger.info("🛑 Bot shutting down...")
    await stop_tracking()


async def main():
    bot = Bot(token=Settings.BOT_TOKEN)
    dp = Dispatcher()
    
    register_common_handlers(dp)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())