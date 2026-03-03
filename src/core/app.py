import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from src.core.config import settings
from src.modules.bot.application.use_cases import (
    register_common_handlers,
    start_tracking,
    stop_tracking,
)
from src.version import __version__



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield



app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    lifespan=lifespan,
)



@app.get("/health")
async def health():
    return {"status": "ok", "version": __version__}


def run_uvicorn():
    import uvicorn

    uvicorn.run(
        "src.core.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )



async def _on_startup(bot: Bot) -> None:
    logger.info("🚀 Bot starting up...")
    logger.info(f"version: {__version__}")
    logger.info(f"📁 Tracking repository: {settings.GITHUB_REPO}")
    logger.info(f"👥 Notification recipients: {len(settings.chat_ids_list)} users")
    asyncio.create_task(start_tracking(bot))



async def _on_shutdown(bot: Bot) -> None:
    logger.info("🛑 Bot shutting down...")
    await stop_tracking()



async def run_bot() -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    register_common_handlers(dp)
    dp.startup.register(_on_startup)
    dp.shutdown.register(_on_shutdown)

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
