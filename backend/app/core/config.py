"""
Глобальная конфигурация приложения.
Все секреты читаются из переменных окружения (файл .env).
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- База данных ---
DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/triumphroll.db")

# --- JWT / Auth ---
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-!!!")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 дней

# --- LLM API Keys ---
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
VENICE_API_KEY: str = os.getenv("VENICE_API_KEY", "")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# --- Модели по умолчанию ---
DEEPSEEK_MODEL: str = "deepseek-chat"
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")

# --- CORS ---
CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# --- Пути ---
AVATARS_DIR: Path = BASE_DIR / "app" / "static" / "avatars"
AVATARS_DIR.mkdir(parents=True, exist_ok=True)
