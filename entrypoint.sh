#!/bin/bash

# Остановка скрипта при любой ошибке
set -e

echo "Запуск миграций Alembic..."
alembic upgrade bcfd2610717d

echo "Запуск сервера Uvicorn..."
# Используем exec, чтобы uvicorn стал основным процессом (PID 1)
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT