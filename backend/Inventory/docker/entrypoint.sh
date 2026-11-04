#!/bin/sh
set -e

# Wait for DB to be ready
until python -c "import socket,sys; socket.create_connection(('${DATABASE_HOST:-flask-db}', 3306), timeout=2)" 2>/dev/null; do
  echo "waiting for db…"
  sleep 2
done

# Run migrations at runtime, not build time
flask db upgrade

exec "$@"