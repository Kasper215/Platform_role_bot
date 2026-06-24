"""
Точка входа (корневой main для совместимости).
Перенаправляет в новую структуру backend/app/main.py
"""
import sys
from pathlib import Path

# Добавляем backend в путь
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.main import app  # noqa