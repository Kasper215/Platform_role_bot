"""
Точка входа FastAPI-приложения.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import CORS_ORIGINS, AVATARS_DIR
from app.core.database import init_db
from app.api.auth import router as auth_router
from app.api.characters import router as characters_router
from app.api.chats import router as chats_router
from app.system_middleware import SystemMonitorMiddleware

# Инициализация БД
init_db()

app = FastAPI(
    title="Role Bot API — Chai-style",
    description="Полноценный ролевой AI-чат, аналог Chai",
    version="2.0.0",
)

# Middleware логирования (до CORS, чтобы логировать все запросы)
app.add_middleware(SystemMonitorMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы (аватарки)
app.mount("/static", StaticFiles(directory=str(AVATARS_DIR.parent)), name="static")

# Роутеры
app.include_router(auth_router, prefix="/api")
app.include_router(characters_router, prefix="/api")
app.include_router(chats_router, prefix="/api")


@app.get("/api")
def root():
    return {"message": "Role Bot API работает", "version": "2.0.0", "status": "ok"}


@app.get("/system/health")
def system_health():
    from app.system_monitor import get_stats
    return get_stats()
