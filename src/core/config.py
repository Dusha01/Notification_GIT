from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Notification bot"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8080

    TELEGRAM_BOT_TOKEN: str
    GITHUB_REPO: str
    CHAT_IDS: str = ""
    GITHUB_TOKEN: str | None = None

    CHECK_INTERVAL: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def BOT_TOKEN(self) -> str:
        return self.TELEGRAM_BOT_TOKEN

    @property
    def chat_ids_list(self) -> List[str]:
        if not self.CHAT_IDS:
            return []
        return [cid.strip() for cid in self.CHAT_IDS.split(",") if cid.strip()]


settings = Settings()