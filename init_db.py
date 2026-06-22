#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from db_capture import init_db

if __name__ == "__main__":
    print("Инициализация базы данных...")
    init_db()
    print("✅ База данных создана!")