#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Генерация структуры проекта для передачи в чат.
Игнорирует бинарные файлы, зависимости, кэши.
"""

import os
import sys
from pathlib import Path

# Папки и файлы для игнорирования
IGNORE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', 'env', '.venv',
    '.idea', '.vscode', 'dist', 'build', '.next', 'out',
    'logs', 'tmp', 'temp', 'coverage', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', '.turbo'
}
IGNORE_FILES = {
    '.pyc', '.pyo', '.so', '.dll', '.exe', '.bin',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mkv', '.mov',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.iso', '.img', '.db', '.sqlite', '.sqlite3',
    '.log', '.lock', '.pid'
}
# Дополнительно игнорируем целые файлы по имени
IGNORE_NAMES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'poetry.lock', 'requirements.txt', 'Pipfile.lock',
    '.env', '.env.local', '.env.*.local'
}

def should_ignore(path: Path) -> bool:
    """Проверяет, нужно ли игнорировать путь."""
    if path.name in IGNORE_NAMES:
        return True
    if path.is_dir():
        if path.name in IGNORE_DIRS:
            return True
    else:
        ext = path.suffix.lower()
        if ext in IGNORE_FILES:
            return True
    return False

def walk_dir(path: Path, prefix: str = "", depth: int = 0, max_depth: int = 5) -> None:
    """Рекурсивный обход с выводом дерева."""
    if depth > max_depth:
        return
    try:
        items = sorted([p for p in path.iterdir() if not should_ignore(p)],
                       key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return

    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{item.name}{'/' if item.is_dir() else ''}")
        if item.is_dir():
            new_prefix = prefix + ("    " if is_last else "│   ")
            walk_dir(item, new_prefix, depth + 1, max_depth)

if __name__ == "__main__":
    root = Path.cwd()
    print(f"Структура проекта: {root}\n")
    walk_dir(root, max_depth=5)