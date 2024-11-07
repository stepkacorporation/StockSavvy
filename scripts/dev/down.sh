#!/usr/bin/env bash

# Останавливает и удаляет контейнеры для разработки
# ./scripts/dev/down.sh

# Вы также можете передать различные аргументы, например:
# ./scripts/dev/down.sh -v

docker-compose -f ./docker/dev/docker-compose.yml down "$@"
