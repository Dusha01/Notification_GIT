# 🤖 GitHub Notification Bot

A Telegram bot for automatically tracking changes in GitHub repositories.

> 🇷🇺 [Русская версия](README.ru.md) Get notifications about new commits and Pull Request merges directly in Telegram.

## ✨ Features

- 🔔 **Commit notifications** — information about each new commit
- 🎉 **Merge notifications** — tracking Pull Request merges
- 🔀 **Fast-forward merge detection** — detects merges without merge commits
- 🌿 **New branches** — notifications about new branches with initial commits
- ⏰ **Automatic checks** — regular repository monitoring (default: every 60 seconds)
- 📊 **Tracking status** — `/status` command to check current state
- 🎨 **Formatted messages** — HTML markup in notifications
- 🌐 **Multilingual** — Russian and English (`/language`)

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Dusha01/Notification_GIT.git
cd Notification_GIT
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from [@BotFather](https://t.me/BotFather) |
| `GITHUB_REPO` | Yes | Repository in `owner/repo` format or full URL |
| `CHAT_ID` | Yes | Chat ID(s) for notifications, comma-separated |
| `GITHUB_TOKEN` | No | GitHub token (for higher API rate limits) |
| `LANGUAGE` | No | Language: `ru` or `en` (default: `ru`) |
| `CHECK_INTERVAL` | No | Check interval in seconds (default: `60`) |
| `DEBUG` | No | Debug mode: `True` / `False` |

### 4. Run

```bash
python run.py
```

## 🐳 Docker

### Build the image

From the project root:

```bash
docker build -f Docker/Dockerfile -t github-notification-bot .
```

### Run the container

```bash
docker run -d \
  --name github-notification-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e CHAT_ID=chat_id1,chat_id2 \
  -v $(pwd)/.env:/app/.env:ro \
  github-notification-bot
```

Or with variables directly:

```bash
docker run -d \
  --name github-notification-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e GITHUB_REPO=owner/repo \
  -e CHAT_ID=chat_id1,chat_id2 \
  -e GITHUB_TOKEN=optional_github_token \
  github-notification-bot
```

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and welcome message |
| `/status` | Current repository tracking status |
| `/help` | Command reference |
| `/language` | Switch language (ru/en) |

## 📋 Requirements

- Python 3.10+
- aiogram 3.x
- GitHub API access

## 📄 License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green)](https://docs.aiogram.dev/)
[![GitHub API](https://img.shields.io/badge/GitHub-API-lightgrey)](https://docs.github.com/en/rest)
