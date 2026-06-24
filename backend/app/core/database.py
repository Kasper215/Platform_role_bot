"""
Настройка БД и фабрика сессий.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — получение сессии БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создание всех таблиц (идемпотентно)."""
    import app.models.user  # noqa
    import app.models.character  # noqa
    import app.models.chat  # noqa
    Base.metadata.create_all(bind=engine)
