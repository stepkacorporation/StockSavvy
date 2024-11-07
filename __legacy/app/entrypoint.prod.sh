#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Postgres еще не запущен..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 10
    done

    echo "PostgreSQL запущен"
fi

exec "$@"