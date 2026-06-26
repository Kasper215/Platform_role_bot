"""
Глобальная конфигурация приложения.
Все секреты читаются из переменных окружения (файл .env) с помощью Pydantic Settings.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Базовая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Roleplay Bot API"

    # --- База данных ---
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/triumphroll.db"

    # --- JWT / Auth ---
    SECRET_KEY: str = "change-me-in-production-!!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 дней

    # --- LLM API Keys ---
    DEEPSEEK_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    VENICE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # --- Модели по умолчанию ---
    DEEPSEEK_MODEL: str = "deepseek-chat"
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-exp:free"

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Конфигурация чтения из .env файла
    model_config = SettingsConfigDict(
        # Указываем абсолютный путь к .env файлу на основе базовой директории
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8-sig",  # Избавились от Windows BOM
        extra="ignore"
    )


# Инициализируем настройки
settings = Settings()

# ─── Экспорт переменных для обратной совместимости со старыми файлами (main.py, security.py) ───
CORS_ORIGINS = settings.CORS_ORIGINS
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

DEEPSEEK_API_KEY = settings.DEEPSEEK_API_KEY
OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
VENICE_API_KEY = settings.VENICE_API_KEY
GEMINI_API_KEY = settings.GEMINI_API_KEY

DEEPSEEK_MODEL = settings.DEEPSEEK_MODEL
OPENROUTER_MODEL = settings.OPENROUTER_MODEL

# --- Пути ---
AVATARS_DIR: Path = BASE_DIR / "app" / "static" / "avatars"
AVATARS_DIR.mkdir(parents=True, exist_ok=True)