#!/usr/bin/env bash

# Создает суперпользователя в окружении разработки
# ./scripts/dev/createsuperuser.sh

# Вы также можете передать дополнительные аргументы:
# ./scripts/dev/createsuperuser.sh --username admin --email admin@example.com --noinput

# Или создать суперпользователя по умолчанию:
# ./scripts/dev/createsuperuser.sh --default

if [[ "$1" == "--default" ]]; then
  docker-compose -f ./docker/dev/docker-compose.yml exec web python manage.py create_default_superuser
else
  winpty docker-compose -f ./docker/dev/docker-compose.yml exec web python manage.py createsuperuser "$@"
fi
