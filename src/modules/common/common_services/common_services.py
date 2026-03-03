from aiogram import Bot
from aiogram.types import Message
from aiogram.enums import ParseMode

from config import Settings
from src.common.cosnt.const import START_MESSAGE, STATUS_MESSAGE, HELP_MESSAGE

async def cmd_start(message: Message):
    await message.answer(
        START_MESSAGE.format(repo=Settings.GITHUB_REPO),
        parse_mode=ParseMode.HTML
    )

async def cmd_status(message: Message):
    await message.answer(
        STATUS_MESSAGE.format(
            repo=Settings.GITHUB_REPO,
            interval=Settings.CHECK_INTERVAL,
            chat_count=len(Settings.CHAT_IDS)
        ),
        parse_mode=ParseMode.HTML
    )

async def cmd_help(message: Message):
    await message.answer(
        HELP_MESSAGE.format(repo=Settings.GITHUB_REPO),
        parse_mode=ParseMode.HTML
    )