from typing import Any

from src.core.config import settings

_user_languages: dict[str, str] = {}

TRANSLATIONS = {
    "ru": {
        "START_MESSAGE": """
🤖 <b>GitHub Notification Bot</b>

Я отслеживаю репозиторий: <code>{repo}</code>

📋 <b>Что отслеживаю:</b>
• Новые коммиты
• Мерджы Pull Request'ов

🔔 <b>Вы будете получать уведомления автоматически!</b>

ℹ️ Для помощи: /help
""",
        "STATUS_MESSAGE": """
📊 <b>Статус отслеживания</b>

📁 Репозиторий: <code>{repo}</code>
⏰ Проверка каждые: {interval} секунд
👥 Получатели: {chat_count} пользователей

🔄 <i>Проверяю обновления...</i>
""",
        "HELP_MESSAGE": """
ℹ️ <b>Помощь по боту</b>

Я автоматически отслеживаю репозиторий: <code>{repo}</code>

📋 <b>Команды:</b>
/start - Информация о боте
/status - Текущий статус
/help - Эта справка
/language - Смена языка (ru/en)

🔔 <b>Отслеживаемые события:</b>
• Push (новые коммиты)
• Merge (мердж Pull Request'ов)

⏰ <b>Обновления проверяются каждую минуту</b>
""",
        "COMMIT_NOTIFICATION": """
📦 <b>Новый коммит в {repo}</b>

👤 <b>Автор:</b> {author}
🔖 <b>Хеш:</b> <code>{sha_short}</code>

📝 <b>Сообщение:</b>
{message}

🔗 <a href='{url}'>Посмотреть коммит</a>
""",
        "COMMIT_NEW_IN_BRANCH": "Новый коммит в ветке '{branch}'",
        "COMMIT_NEW": "Новый коммит",
        "MERGE_NOTIFICATION": """
🎉 <b>Pull Request мерджнут: {repo}</b>

📋 <b>Заголовок:</b> {title}
👤 <b>Автор:</b> {author}
🔢 <b>Номер:</b> #{number}

🔗 <a href='{url}'>Посмотреть PR</a>
""",
        "COMMITS_IN_PR": "\n\n📝 <b>Коммиты в PR:</b>\n",
        "AND_MORE_COMMITS": "... и ещё {count} коммитов",
        "NEW_BRANCH_NOTIFICATION": """
🌿 <b>Создана новая ветка: {branch_name}</b>

📦 <b>Последний коммит:</b>
👤 <b>Автор:</b> {author}
🔖 <b>Хеш:</b> <code>{sha_short}</code>

📝 <b>Сообщение:</b>
{message}

🔗 <a href='{url}'>Посмотреть коммит</a>
""",
        "LANGUAGE_CURRENT": "🌐 Текущий язык: <b>{lang}</b>",
        "LANGUAGE_CHOOSE": "Выберите язык:",
        "LANGUAGE_CHANGED": "✅ Язык изменён на <b>{lang}</b>",
        "LANGUAGE_INVALID": "Неизвестный язык. Используйте: ru или en",
    },
    "en": {
        "START_MESSAGE": """
🤖 <b>GitHub Notification Bot</b>

I'm tracking repository: <code>{repo}</code>

📋 <b>What I track:</b>
• New commits
• Pull Request merges

🔔 <b>You will receive notifications automatically!</b>

ℹ️ For help: /help
""",
        "STATUS_MESSAGE": """
📊 <b>Tracking status</b>

📁 Repository: <code>{repo}</code>
⏰ Check every: {interval} seconds
👥 Recipients: {chat_count} users

🔄 <i>Checking for updates...</i>
""",
        "HELP_MESSAGE": """
ℹ️ <b>Bot help</b>

I automatically track repository: <code>{repo}</code>

📋 <b>Commands:</b>
/start - Bot information
/status - Current status
/help - This help
/language - Change language (ru/en)

🔔 <b>Tracked events:</b>
• Push (new commits)
• Merge (Pull Request merges)

⏰ <b>Updates are checked every minute</b>
""",
        "COMMIT_NOTIFICATION": """
📦 <b>New commit in {repo}</b>

👤 <b>Author:</b> {author}
🔖 <b>Hash:</b> <code>{sha_short}</code>

📝 <b>Message:</b>
{message}

🔗 <a href='{url}'>View commit</a>
""",
        "COMMIT_NEW_IN_BRANCH": "New commit in branch '{branch}'",
        "COMMIT_NEW": "New commit",
        "MERGE_NOTIFICATION": """
🎉 <b>Pull Request merged: {repo}</b>

📋 <b>Title:</b> {title}
👤 <b>Author:</b> {author}
🔢 <b>Number:</b> #{number}

🔗 <a href='{url}'>View PR</a>
""",
        "COMMITS_IN_PR": "\n\n📝 <b>Commits in PR:</b>\n",
        "AND_MORE_COMMITS": "... and {count} more commits",
        "NEW_BRANCH_NOTIFICATION": """
🌿 <b>New branch created: {branch_name}</b>

📦 <b>Latest commit:</b>
👤 <b>Author:</b> {author}
🔖 <b>Hash:</b> <code>{sha_short}</code>

📝 <b>Message:</b>
{message}

🔗 <a href='{url}'>View commit</a>
""",
        "LANGUAGE_CURRENT": "🌐 Current language: <b>{lang}</b>",
        "LANGUAGE_CHOOSE": "Choose language:",
        "LANGUAGE_CHANGED": "✅ Language changed to <b>{lang}</b>",
        "LANGUAGE_INVALID": "Unknown language. Use: ru or en",
    },
}

LANG_NAMES = {"ru": "Русский", "en": "English"}


def _get_default_locale() -> str:
    lang = (settings.LANGUAGE or "ru").strip().lower()
    return lang if lang in TRANSLATIONS else "ru"


def get_locale(chat_id: str | int | None = None) -> str:
    if chat_id is not None:
        uid = str(chat_id)
        if uid in _user_languages:
            return _user_languages[uid]
    return _get_default_locale()


def t(key: str, chat_id: str | int | None = None, **kwargs: Any) -> str:
    locale = get_locale(chat_id)
    text = TRANSLATIONS.get(locale, TRANSLATIONS["ru"]).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


def set_language(chat_id: str | int, lang: str) -> bool:
    lang = lang.strip().lower()
    if lang in TRANSLATIONS:
        _user_languages[str(chat_id)] = lang
        return True
    return False


def get_language(chat_id: str | int | None = None) -> str:
    return get_locale(chat_id)