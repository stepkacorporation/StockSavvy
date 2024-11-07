#!/usr/bin/env bash

# Создает суперпользователя в продакшене
# ./scripts/prod/createsuperuser.sh

# Вы также можете передать дополнительные аргументы:
# ./scripts/prod/createsuperuser.sh --username admin --email admin@example.com --noinput

winpty docker-compose -f ./docker/prod/docker-compose.yml exec -it web python manage.py createsuperuser "$@"
