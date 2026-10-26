# Лабораторная работа: Docker Compose — вариант 2

## Тема
Курсы валют. Четыре контейнера: frontend (Nginx/HTML/JS), backend (Flask), db (PostgreSQL), web-service (Flask, внешний API курсов валют).

## Запуск
1. Установите Docker Desktop и запустите его.
2. Откройте терминал в папке проекта.
3. Выполните `docker compose up --build -d`.
4. Откройте http://localhost:8080.
5. Введите сумму, выберите валюты и нажмите «Конвертировать».
6. Нажмите «История операций», чтобы увидеть журнал из PostgreSQL.

## Проверка
- `docker compose ps` — четыре запущенных контейнера.
- `docker compose logs backend` — логи бэкенда.
- `docker compose down` — остановка; данные в volume сохраняются.
- `docker compose down -v` — удаление, включая историю операций.

## Архитектура
Браузер → frontend:8080 → backend:5000 → web-service:5001 → внешний API https://open.er-api.com/v6/latest/USD. Backend также сохраняет операции в PostgreSQL (db:5432).

## API
- `POST /api/convert`: JSON `{"amount":100,"source":"USD","target":"EUR"}`.
- `GET /api/history`: последние 30 операций.

