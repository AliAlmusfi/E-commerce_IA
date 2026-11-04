#!/bin/sh
set -e

echo "Waiting for database at ${DATABASE_HOST:-django-db}:3306..."
until python -c "import socket,os; socket.create_connection((os.environ.get('DATABASE_HOST','django-db'), 3306), timeout=2)" 2>/dev/null; do
  echo "  db not ready yet, retrying in 2s..."
  sleep 2
done
echo "Database is up."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn e_commerce.wsgi:application \
     --bind 0.0.0.0:8000 \
     --workers 3 \
     --timeout 120