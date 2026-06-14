#!/bin/sh
set -e

echo "Waiting for MongoDB at mongo:27017..."
until python -c "
import socket
s = socket.socket()
s.settimeout(1)
s.connect(('mongo', 27017))
s.close()
" 2>/dev/null; do
  sleep 1
done
echo "MongoDB is ready."

echo "Waiting for Redis at redis:6379..."
until python -c "
import socket
s = socket.socket()
s.settimeout(1)
s.connect(('redis', 6379))
s.close()
" 2>/dev/null; do
  sleep 1
done
echo "Redis is ready."

exec "$@"
