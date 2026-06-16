from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./triumphroll.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создаёт все таблицы, описанные в моделях (идемпотентно)."""
    Base.metadata.create_all(bind=engine)


# Карта новых колонок, добавляемых к уже существующим таблицам: {таблица: [(колонка, SQL-тип)]}.
# SQLite позволяет ADD COLUMN только для новых столбцов (безопасно, данные не теряются).
_COLUMN_ADDITIONS = {
    "users": [
        ("display_name", "VARCHAR(100)"),
        ("bio", "TEXT"),
    ],
    "characters": [
        ("description", "TEXT"),
        ("tags", "VARCHAR(500)"),
        ("is_featured", "BOOLEAN DEFAULT 0"),
        ("chat_count", "INTEGER DEFAULT 0"),
        ("like_count", "INTEGER DEFAULT 0"),
        ("views", "INTEGER DEFAULT 0"),
    ],
}


def _existing_columns(conn, table: str) -> set[str]:
    result = conn.execute(text(f"PRAGMA table_info({table})"))
    return {row[1] for row in result}


def run_migrations():
    """Дополняет существующие таблицы новыми колонками через ALTER TABLE.
    Новые таблицы (character_likes, chat_meta) создаются через create_all в init_db."""
    with engine.begin() as conn:
        for table, columns in _COLUMN_ADDITIONS.items():
            # Если таблицы ещё нет — её создаст create_all, пропускаем здесь.
            try:
                existing = _existing_columns(conn, table)
            except Exception:
                continue
            for col_name, col_type in columns:
                if col_name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"))
