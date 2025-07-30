#!/bin/sh
# wait-for-it.sh

set -e

host="$1"
shift
cmd="$@"

echo "*:*:*:$POSTGRES_USER:$POSTGRES_PASSWORD" > ~/.pgpass
chmod 0600 ~/.pgpass

until psql -h "$host" -U "nokari" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
