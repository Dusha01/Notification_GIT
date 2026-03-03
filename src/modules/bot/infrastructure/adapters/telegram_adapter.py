"""Telegram notification adapter - infrastructure implementation."""

import logging
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.enums import ParseMode

from src.core.config import settings
from src.modules.bot.domain.services.notification_sender import NotificationSender

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class TelegramNotificationAdapter(NotificationSender):
    """Concrete implementation using Telegram Bot API."""

    def __init__(self, bot: Bot):
        self._bot = bot

    async def send(self, text: str) -> None:
        """Send notification to configured chat IDs."""
        chat_ids = settings.chat_id_list
        if not chat_ids:
            logger.warning("No chat IDs configured for notifications")
            return

        for chat_id in chat_ids:
            try:
                await self._bot.send_message(
                    chat_id,
                    text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                logger.info(f"Notification sent to {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send notification to {chat_id}: {e}")
