#!/usr/bin/env bash

# Загружает данные о акциях в базу данных из внешнего API
# ./scripts/dev/load_stock_data.sh

# Вы также можете передать аргумент --update или -U для обновления исторических данных:
# ./scripts/dev/load_stock_data.sh --update
# Или:
# ./scripts/dev/load_stock_data.sh -U

if [[ "$1" == "--update" ]] || [[ "$1" == "-U" ]]; then
  docker-compose -f ./docker/dev/docker-compose.yml exec web python app/manage.py load_stock_data --update
else
  docker-compose -f ./docker/dev/docker-compose.yml exec web python app/manage.py load_stock_data
fi
