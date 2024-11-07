# StockSavvy
Stock Savvy is an information system designed for analyzing stock prices. It provides users with tools to track, analyze, and visualize stock market trends.

## Live Demo
Check out the live demo of StockSavvy at [stocksavvy.ru](https://stocksavvy.ru).

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Clone the Repository](#clone-the-repository)
  - [Environment Variables](#environment-variables)
  - [Build and Run the Project](#build-and-run-the-project)
  - [Create a Superuser](#create-a-superuser)
  - [Load Stock Data](#load-stock-data)
  - [Access the Application](#access-the-application)

## Features
- Automatic Data Updates: All data is automatically updated daily.
- Stock Price Tracking: Track the latest stock prices.
- Historical Data Analysis: Analyze historical stock price data.
- Visualizations: Generate charts to visualize stock trends.
- User Authentication: Secure login and registration for users.
- Favorites: Add stocks to your favorites for quick access.

## Prerequisites
- Docker
- Docker Compose

## Getting Started
Follow these instructions to set up and run StockSavvy using Docker.

### Clone the Repository
```sh
git clone https://github.com/stepkacorporation/stocksavvy.git
```
```sh
cd stocksavvy
```

### Environment Variables
Create a `.env` file in the project root directory and add the following environment variables:
```env
SECRET_KEY=[your_secret_key]
DEBUG=True
ALLOWED_HOSTS=127.0.0.1 localhost
CORS_ALLOWED_ORIGINS=http://localhost:8000 https://localhost:8000 http://127.0.0.1:8000 https://127.0.0.1:8000
CSRF_TRUSTED_ORIGINS=http://localhost:8000 https://localhost:8000 http://127.0.0.1:8000 https://127.0.0.1:8000

DB_NAME=stocksavvy
DB_USER=stocksavvy
DB_PASSWORD=[your_database_password]
DB_HOST=postgres
DB_PORT=5432
DATABASE=postgres

EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=[your_email]
EMAIL_HOST_PASSWORD=[your_email_password]
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=stocksavvy@gmail.com

REDIS_BROKER_HOST=redis_broker
REDIS_BROKER_PORT=6379

REDIS_CACHE_HOST=redis_cache
REDIS_CACHE_PORT=6379
```
Make sure to replace the placeholders ([your_secret_key], [your_database_password], [your_email, [your_email_password]) with your actual values.

### Build and Run the Project
Build and run the Docker containers using Docker Compose.
```sh
docker-compose up -d --build
```
This will start the following services:
- django: The Django application server.
- postgres: The PostgreSQL database server.
- redis_broker: The Redis server for background task queue.
- redis_cache: The Redis server for caching.
- celery_worker: The Celery worker for executing asynchronous tasks.
- celery_beat: The Celery beat scheduler for running periodic tasks.

### Create a Superuser
Create a superuser to access the Django admin interface.
```sh
docker-compose exec django python manage.py createsuperuser
```
Follow the prompts to set up your superuser account.

### Load Stock Data
Loading stock data using the `load_stock_data` command may take a significant amount of time depending on your computer's configuration and network speed.

To load stock data for the entire available period, use the following command:
```sh
docker-compose exec django python manage.py load_stock_data
```
To load stock data for the past day, use the following command:
```sh
docker-compose exec django python manage.py load_stock_data --update
```
or
```sh
docker-compose exec django python manage.py load_stock_data -U
```

### Access the Application
Open your web browser and go to http://localhost:8000 to access StockSavvy.

The Django admin interface can be accessed at http://localhost:8000/admin.
