import re
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_github_repo(value: str) -> str:
    """Convert URL to owner/repo format for GitHub API."""
    value = (value or "").strip()
    if not value:
        return value
    # https://github.com/owner/repo or https://github.com/owner/repo/
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$", value)
    if match:
        return f"{match.group(1)}/{match.group(2).rstrip('/')}"
    return value


class Settings(BaseSettings):

    APP_NAME: str = "Notification bot"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8080

    TELEGRAM_BOT_TOKEN: str
    GITHUB_REPO: str
    CHAT_ID: str = ""
    GITHUB_TOKEN: str | None = None

    CHECK_INTERVAL: int = 60

    LANGUAGE: str = "ru"  # ru | en

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("GITHUB_REPO", mode="after")
    @classmethod
    def normalize_github_repo(cls, v: str) -> str:
        return _normalize_github_repo(v)

    @property
    def BOT_TOKEN(self) -> str:
        return self.TELEGRAM_BOT_TOKEN

    @property
    def chat_id_list(self) -> List[str]:
        if not self.CHAT_ID:
            return []
        return [cid.strip() for cid in self.CHAT_ID.split(",") if cid.strip()]


settings = Settings()