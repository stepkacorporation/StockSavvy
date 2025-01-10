#!/usr/bin/env bash

# Скрипт для загрузки данных о акциях в базу данных из внешнего API
# ./scripts/dev/load_stock_data.sh

# Примеры использования:
# ./scripts/dev/load_stock_data.sh --start_date 2023-01-01 --end_date 2023-12-31
# ./scripts/dev/load_stock_data.sh -S 2023-01-01 -E 2023-12-31

# Парсинг аргументов
START_DATE=""
END_DATE=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --start_date|-S) START_DATE="$2"; shift ;;
        --end_date|-E) END_DATE="$2"; shift ;;
        *) echo "Неизвестный параметр: $1"; exit 1 ;;
    esac
    shift
done

# Формирование команды
CMD="docker-compose -f ./docker/dev/docker-compose.yml exec web python app/manage.py load_stock_data"

if [[ -n "$START_DATE" ]]; then
    CMD+=" --start_date $START_DATE"
fi

if [[ -n "$END_DATE" ]]; then
    CMD+=" --end_date $END_DATE"
fi

# Выполнение команды
echo "Запуск команды: $CMD"
eval "$CMD"
