COMMIT_NOTIFICATION = """
📦 <b>Новый коммит в {repo}</b>

👤 <b>Автор:</b> {author}
🔖 <b>Хеш:</b> <code>{sha_short}</code>

📝 <b>Сообщение:</b>
{message}

🔗 <a href='{url}'>Посмотреть коммит</a>
"""


MERGE_NOTIFICATION = """
🎉 <b>Pull Request мерджнут: {repo}</b>

📋 <b>Заголовок:</b> {title}
👤 <b>Автор:</b> {author}
🔢 <b>Номер:</b> #{number}

🔗 <a href='{url}'>Посмотреть PR</a>
"""
