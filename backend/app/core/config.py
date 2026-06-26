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
        env_file_encoding="utf-8-sig",
        extra="ignore"
    )


# Инициализируем настройки
settings = Settings()

# --- Пути ---
AVATARS_DIR: Path = BASE_DIR / "app" / "static" / "avatars"
AVATARS_DIR.mkdir(parents=True, exist_ok=True)