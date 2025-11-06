#!/bin/sh
# wait-for-it.sh - Waits for a TCP host/port to be available

set -e

TARGET="$1"
shift

# Separate host and port
HOST=$(printf "%s\n" "$TARGET" | cut -d: -f1)
PORT=$(printf "%s\n" "$TARGET" | cut -d: -f2)

until nc -z "$HOST" "$PORT"; do
  >&2 echo "Waiting for $HOST:$PORT..."
  sleep 1
done

>&2 echo "$HOST:$PORT is up - executing command"
exec "$@"
