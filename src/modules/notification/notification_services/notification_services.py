import logging
from aiogram import Bot
from aiogram.enums import ParseMode

from config import Settings

logger = logging.getLogger(__name__)

async def send_notification(bot: Bot, text: str):
    if not Settings.CHAT_IDS:
        logger.warning("No chat IDs configured for notifications")
        return
    
    for chat_id in Settings.CHAT_IDS:
        try:
            await bot.send_message(
                chat_id,
                text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            logger.info(f"Notification sent to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send notification to {chat_id}: {e}")