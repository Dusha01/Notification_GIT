from aiogram import Bot
from aiogram.types import Message
from aiogram.enums import ParseMode

from config import Settings

async def cmd_start(message: Message):
    await message.answer(
        f"🤖 <b>GitHub Notification Bot</b>\n\n"
        f"Я отслеживаю репозиторий: <code>{Settings.GITHUB_REPO}</code>\n\n"
        f"📋 <b>Что отслеживаю:</b>\n"
        f"• Новые коммиты\n"
        f"• Мерджы Pull Request'ов\n\n"
        f"🔔 <b>Вы будете получать уведомления автоматически!</b>\n\n"
        f"ℹ️ Для помощи: /help",
        parse_mode=ParseMode.HTML
    )

async def cmd_status(message: Message, bot: Bot):
    await message.answer(
        f"📊 <b>Статус отслеживания</b>\n\n"
        f"📁 Репозиторий: <code>{Settings.GITHUB_REPO}</code>\n"
        f"⏰ Проверка каждые: {Settings.CHECK_INTERVAL} секунд\n"
        f"👥 Получатели: {len(Settings.CHAT_IDS)} пользователей\n\n"
        f"🔄 <i>Проверяю обновления...</i>",
        parse_mode=ParseMode.HTML
    )

async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Помощь по боту</b>\n\n"
        f"Я автоматически отслеживаю репозиторий: <code>{Settings.GITHUB_REPO}</code>\n\n"
        "📋 <b>Команды:</b>\n"
        "/start - Информация о боте\n"
        "/status - Текущий статус\n"
        "/help - Эта справка\n\n"
        "🔔 <b>Отслеживаемые события:</b>\n"
        "• Push (новые коммиты)\n"
        "• Merge (мердж Pull Request'ов)\n\n"
        "⏰ <b>Обновления проверяются каждую минуту</b>",
        parse_mode=ParseMode.HTML
    )