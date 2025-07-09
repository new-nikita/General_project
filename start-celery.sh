#!/bin/sh
set -e
echo "Запускаю задачи Celery"
celery -A backend.auth.Celery.tasks worker --loglevel=info &

echo "Запуск Celery beat..."
celery -A backend.auth.Celery.tasks beat --loglevel=info