from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from src.core.config import settings
from src.modules.bot.domain.constants.messages import (
    START_MESSAGE,
    STATUS_MESSAGE,
    HELP_MESSAGE,
)


async def cmd_start(message: Message) -> None:
    await message.answer(
        START_MESSAGE.format(repo=settings.GITHUB_REPO),
        parse_mode="HTML",
    )


async def cmd_status(message: Message) -> None:
    await message.answer(
        STATUS_MESSAGE.format(
            repo=settings.GITHUB_REPO,
            interval=settings.CHECK_INTERVAL,
            chat_count=len(settings.chat_ids_list),
        ),
        parse_mode="HTML",
    )


async def cmd_help(message: Message) -> None:
    await message.answer(
        HELP_MESSAGE.format(repo=settings.GITHUB_REPO),
        parse_mode="HTML",
    )


def register_common_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_help, Command("help"))
