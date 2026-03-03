from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    APP_NAME: str = "Notification bot"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8080

    BOT_TOKEN: str
    GITHUB_REPO: str
    CHAT_ID: str
    GITHUB_TOKEN: str

    CHECK_INTERVAL = 60


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

config = Config()