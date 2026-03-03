# 🤖 GitHub Notification Bot

Telegram бот для автоматического отслеживания изменений в GitHub репозиториях. Получайте уведомления о новых коммитах и мерджах Pull Request'ов прямо в Telegram.

## ✨ Возможности

- 🔔 **Уведомления о коммитах** - получайте информацию о каждом новом коммите
- 🎉 **Уведомления о мерджах** - отслеживание слияния Pull Request'ов
- ⏰ **Автоматическая проверка** - регулярный мониторинг репозитория
- 📊 **Статус отслеживания** - команда для проверки текущего состояния
- 🎨 **Красивые уведомления** - форматированные сообщения с HTML разметкой

## 🚀 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/Dusha01/Notification_GIT.git
cd github-notification-bot
```

## 2. Установка зависимостей

```bash
pip install requirements.txt
```

## 3. Настройка переменных окружения

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GITHUB_REPO=username/repository_name
CHAT_ID=chat_id1,chat_id2,chat_id3
GITHUB_TOKEN=your_github_token_optional
```

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green)](https://docs.aiogram.dev/)
[![GitHub API](https://img.shields.io/badge/GitHub-API-lightgrey)](https://docs.github.com/en/rest)
