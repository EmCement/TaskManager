#!/bin/bash
set -e
echo "Запуск Task Manager API..."
echo "Ожидание готовности PostgreSQL..."
while ! pg_isready -h postgres -p 5432 > /dev/null 2>&1; do
    sleep 1
done
echo "Инициализация тестовых пользователей..."
python init_users.py || echo "Пользователи уже существуют или произошла ошибка"
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
