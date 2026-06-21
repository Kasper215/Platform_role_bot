#!/usr/bin/env python3
from db_capture import save_capture, init_db, count_captures, get_all_captures

init_db()

test_data = {
    'email': 'testuser@example.com',
    'password': 'supersecret123',
    'ip': '192.168.1.1',
    'path': '/auth/login',
    'user_agent': 'Mozilla/5.0',
    'full_data': {}
}

print("📝 Сохранение тестовой записи...")
save_capture(test_data)

print(f"📊 Всего записей: {count_captures()}")

print("\n📋 Последние записи:")
for row in get_all_captures(5):
    print(f"  {row[1]} | {row[2]} | {row[3]}")