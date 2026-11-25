#!/bin/sh
set -e

echo "Waiting for database at ${DATABASE_HOST:-django-db}:3306..."
until python -c "import socket,os; socket.create_connection((os.environ.get('DATABASE_HOST','django-db'), 3306), timeout=2)" 2>/dev/null; do
  echo "  db not ready yet, retrying in 2s..."
  sleep 2
done
echo "Database is up."

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  echo "Running migrations..."
  python manage.py migrate --noinput
fi

python manage.py collectstatic --noinput

# Run the command from Compose (CMD) if provided; otherwise fall back
if [ "$#" -gt 0 ]; then
  exec "$@"
else
  exec uvicorn e_commerce.asgi:application --host 0.0.0.0 --port 8000 --workers 3
fi