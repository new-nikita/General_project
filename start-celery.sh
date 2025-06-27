#!/bin/sh
set -e
echo "запускаю задачи Celery"
celery -A backend.auth.Celery.tasks worker --loglevel=info