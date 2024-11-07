#!/usr/bin/env bash

# Запускает контейнеры для разработки
# ./scripts/dev/up.sh

# Вы также передавать различные аргументы, например:
# ./scripts/dev/up.sh -d --build

docker-compose -f ./docker/dev/docker-compose.yml up "$@"
