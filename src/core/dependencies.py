from typing import Optional

from aiogram import Bot

from src.core.config import settings
from src.modules.bot.domain.services.notification_sender import NotificationSender
from src.modules.bot.infrastructure.adapters.telegram_adapter import (
    TelegramNotificationAdapter,
)
from src.modules.github.application.use_cases.github_service import GitHubService
from src.modules.github.domain.repositories.github_repository import GitHubRepository
from src.modules.github.infrastructure.adapters.github_api_adapter import (
    GitHubApiAdapter,
)


def get_github_repository(
    repo: Optional[str] = None,
    token: Optional[str] = None,
) -> GitHubRepository:
    return GitHubApiAdapter(
        repo=repo or settings.GITHUB_REPO,
        token=token or settings.GITHUB_TOKEN,
    )


def get_github_service(repository: Optional[GitHubRepository] = None) -> GitHubService:
    return GitHubService(repository=repository or get_github_repository())


def get_notification_sender(bot: Bot) -> NotificationSender:
    return TelegramNotificationAdapter(bot)
