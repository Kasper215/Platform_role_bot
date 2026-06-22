import requests

url = "http://localhost:8001/auth/login"

# Отправляем как form-data, а не JSON
data = {
    "username": "test@docker.com",
    "password": "mysecret"
}

try:
    response = requests.post(url, data=data)  # ← data=, а не json=
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text}")
except Exception as e:
    print(f"Ошибка: {e}")