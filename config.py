from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    CHAT_IDS = os.getenv("CHAT_IDS", "").split(",") if os.getenv("CHAT_IDS") else []
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

    CHECK_INTERVAL = 60