from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from src.core.config import settings
from src.i18n import LANG_NAMES, t, set_language, get_language


async def cmd_start(message: Message) -> None:
    chat_id = message.chat.id
    await message.answer(
        t("START_MESSAGE", chat_id=chat_id, repo=settings.GITHUB_REPO),
        parse_mode="HTML",
    )


async def cmd_status(message: Message) -> None:
    chat_id = message.chat.id
    await message.answer(
        t(
            "STATUS_MESSAGE",
            chat_id=chat_id,
            repo=settings.GITHUB_REPO,
            interval=settings.CHECK_INTERVAL,
            chat_count=len(settings.chat_id_list),
        ),
        parse_mode="HTML",
    )


async def cmd_help(message: Message) -> None:
    chat_id = message.chat.id
    await message.answer(
        t("HELP_MESSAGE", chat_id=chat_id, repo=settings.GITHUB_REPO),
        parse_mode="HTML",
    )


async def cmd_language(message: Message) -> None:
    chat_id = message.chat.id
    text = message.text or ""
    parts = text.split(maxsplit=1)

    if len(parts) == 2:
        lang = parts[1].strip().lower()
        if set_language(chat_id, lang):
            lang_name = LANG_NAMES.get(lang, lang)
            await message.answer(
                t("LANGUAGE_CHANGED", chat_id=chat_id, lang=lang_name),
                parse_mode="HTML",
            )
        else:
            await message.answer(t("LANGUAGE_INVALID", chat_id=chat_id))
    else:
        current = get_language(chat_id)
        lang_name = LANG_NAMES.get(current, current)
        msg = t("LANGUAGE_CURRENT", chat_id=chat_id, lang=lang_name)
        msg += "\n\n" + t("LANGUAGE_CHOOSE", chat_id=chat_id)
        msg += "\n/language ru — Русский\n/language en — English"
        await message.answer(msg, parse_mode="HTML")


def register_common_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_status, Command("status"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_language, Command("language"))
