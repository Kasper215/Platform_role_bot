#!/bin/bash
set -e

PROJECT_DIR="/root/role_bot"
LOG_FILE="/var/log/role_bot_deploy.log"
LOCK_FILE="/tmp/role_bot_deploy.lock"

if [ -f "$LOCK_FILE" ]; then
    echo "$(date) - Деплой уже запущен" >> "$LOG_FILE"
    exit 1
fi
touch "$LOCK_FILE"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "🚀 Начинаем деплой..."
cd "$PROJECT_DIR" || { log "❌ Не удалось перейти в $PROJECT_DIR"; rm -f "$LOCK_FILE"; exit 1; }

log "📥 Git pull..."
git fetch origin
git reset --hard origin/main

log "🔨 Пересборка контейнеров..."
docker compose build --no-cache

log "🔄 Перезапуск сервисов..."
docker compose up -d --force-recreate

log "⏳ Ожидание запуска..."
sleep 10

log "📊 Статус контейнеров:"
docker compose ps >> "$LOG_FILE"

log "🧹 Очистка старых образов..."
docker image prune -f

log "✨ Деплой завершён успешно!"
rm -f "$LOCK_FILE"
