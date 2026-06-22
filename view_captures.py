#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Просмотр сохранённых перехватов из SQLite.
"""

from db_capture import get_all_captures, get_by_email, count_captures

def show_all(limit=20):
    """Показывает последние записи."""
    rows = get_all_captures(limit)
    print(f"\n📋 Последние {len(rows)} записей:\n")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]}. {row[1]} | {row[2]} | {row[3]}")
    print("-" * 80)
    print(f"Всего записей: {count_captures()}")

def search_email(email):
    """Ищет по email."""
    rows = get_by_email(email)
    print(f"\n🔍 Найдено {len(rows)} записей для '{email}':\n")
    for row in rows:
        print(f"{row[0]}. {row[1]} | {row[2]} | {row[3]}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        search_email(sys.argv[1])
    else:
        show_all()