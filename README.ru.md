# 🤖 GitHub Notification Bot

Telegram-бот для автоматического отслеживания изменений в GitHub репозиториях.

> 🇬🇧 [English version](README.md) Получайте уведомления о новых коммитах и слияниях Pull Request'ов прямо в Telegram.

## ✨ Возможности

- 🔔 **Уведомления о коммитах** — информация о каждом новом коммите
- 🎉 **Уведомления о мерджах** — отслеживание слияния Pull Request'ов
- 🔀 **Fast-forward merge** — определение мерджей без merge-коммитов
- 🌿 **Новые ветки** — уведомления о новых ветках с первыми коммитами
- ⏰ **Автоматическая проверка** — регулярный мониторинг репозитория (по умолчанию каждые 60 сек)
- 📊 **Статус отслеживания** — команда `/status` для проверки текущего состояния
- 🎨 **Форматированные сообщения** — HTML-разметка в уведомлениях
- 🌐 **Мультиязычность** — русский и английский (`/language`)

## 🚀 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/Dusha01/Notification_GIT.git
cd Notification_GIT
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Переменные окружения:

| Переменная | Обязательная | Описание |
|------------|--------------|----------|
| `TELEGRAM_BOT_TOKEN` | Да | Токен бота от [@BotFather](https://t.me/BotFather) |
| `GITHUB_REPO` | Да | Репозиторий в формате `owner/repo` или полный URL |
| `CHAT_ID` | Да | ID чата(ов) через запятую для уведомлений |
| `GITHUB_TOKEN` | Нет | Токен GitHub (для увеличения лимита API) |
| `LANGUAGE` | Нет | Язык: `ru` или `en` (по умолчанию `ru`) |
| `CHECK_INTERVAL` | Нет | Интервал проверки в секундах (по умолчанию `60`) |
| `DEBUG` | Нет | Режим отладки: `True` / `False` |

### 4. Запуск

```bash
python run.py
```

## 🐳 Docker

### Сборка образа

Из корня проекта:

```bash
docker build -f Docker/Dockerfile -t github-notification-bot .
```

### Запуск контейнера

```bash
docker run -d \
  --name github-notification-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e CHAT_ID=chat_id1,chat_id2 \
  -v $(pwd)/.env:/app/.env:ro \
  github-notification-bot
```

Или с переменными напрямую:

```bash
docker run -d \
  --name github-notification-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e CHAT_ID=chat_id1,chat_id2 \
  -e GITHUB_TOKEN=optional_github_token \
  github-notification-bot
```

## 📱 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запуск бота и приветствие |
| `/status` | Текущий статус отслеживания репозитория |
| `/help` | Справка по командам |
| `/language` | Переключение языка (ru/en) |

## 📋 Требования

- Python 3.10+
- aiogram 3.x
- Доступ к GitHub API

## 📄 Лицензия

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green)](https://docs.aiogram.dev/)
[![GitHub API](https://img.shields.io/badge/GitHub-API-lightgrey)](https://docs.github.com/en/rest)
