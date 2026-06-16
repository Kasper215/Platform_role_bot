from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database
from auth_router import router as auth_router
from characters import router as characters_router
from chats import router as chats_router

# Создаём таблицы и безопасно дополняем существующие новыми колонками
database.init_db()
database.run_migrations()

app = FastAPI(title="TriumphRoll API")

# Разрешаем все нужные источники
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, PUT, DELETE, OPTIONS)
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(auth_router)
app.include_router(characters_router)
app.include_router(chats_router)

@app.get("/")
def root():
    return {"message": "TriumphRoll API работает", "status": "ok"}