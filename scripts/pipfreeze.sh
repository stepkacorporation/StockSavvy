#!/usr/bin/env bash

# Скрипт для установки или удаления библиотек с помощью pip и обновления файла ./requirements.txt
# Использование:
# Установка: ./scripts/pipfreeze.sh <название_библиотеки1> <название_библиотеки2> ...
# Удаление: ./scripts/pipfreeze.sh -r <название_библиотеки1> <название_библиотеки2> ...

# Проверка наличия аргументов
if [ $# -eq 0 ]; then
    echo "Ошибка: Необходимо указать хотя бы одну библиотеку."
    echo "Использование для установки: ./scripts/pipfreeze.sh <название_библиотеки1> <название_библиотеки2> ..."
    echo "Использование для удаления: ./scripts/pipfreeze.sh -r <название_библиотеки1> <название_библиотеки2> ..."
    exit 1
fi

# Флаг для удаления библиотек
remove=false

# Проверка на наличие флага -r
if [ "$1" == "-r" ]; then
    remove=true
    shift # Удаление первого аргумента (флага) из списка аргументов
fi

# Установка или удаление библиотек с помощью pip
for library in "$@"; do
    if [ "$remove" = true ]; then
        pip uninstall -y "$library"

        # Проверка успешного удаления библиотеки
        if [ $? -ne 0 ]; then
            echo "Ошибка: Не удалось удалить библиотеку $library."
            exit 1
        fi
    else
        pip install "$library"

        # Проверка успешной установки библиотеки
        if [ $? -ne 0 ]; then
            echo "Ошибка: Не удалось установить библиотеку $library."
            exit 1
        fi
    fi
done

# Обновление requirements.txt
pip freeze > ./requirements.txt

if [ "$remove" = true ]; then
    echo "Библиотеки успешно удалены и зависимости обновлены в ./requirements.txt."
else
    echo "Библиотеки успешно установлены и все зависимости сохранены в ./requirements.txt."
fi
