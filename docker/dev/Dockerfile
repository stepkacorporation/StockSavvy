FROM python:3.12

# Устанавливаем необходимые переменные окружения
ENV HOME=/home \
    APP_HOME=/home/app \
    PYTHONPATH="$PYTHONPATH:$HOME" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Создаем рабочую директорию
RUN mkdir -p $APP_HOME \
    && groupadd -r stocksavvy \
    && useradd -r -g stocksavvy stocksavvy

# Обновляем пакеты и устанавливаем зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Node.js и npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Переходим в рабочу директорию
WORKDIR $HOME

# Копируем Python зависимости
COPY ../../requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем Frontend зависимости
COPY ../../package.json ./
COPY ../../package-lock.json ./
RUN npm install

# Копируем Tailwind и DaisyUI конфигурацию
COPY ../../tailwind.config.js ./

# Копируем все приложение
COPY ./app/ $APP_HOME

# Копируем дополнительные папки
COPY ../../scripts/wait-for-it.sh ./scripts/wait-for-it.sh

# Меняем права на файлы
RUN chown -R stocksavvy:stocksavvy $HOME

# Запускаем контейнер от пользователя stocksavvy
USER stocksavvy