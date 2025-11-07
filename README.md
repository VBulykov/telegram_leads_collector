# 📥 Telegram Lead Parser

Парсер лидов (контактной информации) из сообщений Telegram-чатов и каналов на базе **FastAPI**, **Telethon**, **SQLAlchemy 2.0**, **Pydantic 2**, и **Redis**.

---

## 🚀 Возможности

- Извлечение email-адресов и телефонов из сообщений
- Асинхронная обработка сообщений через Telethon
- API для запуска парсинга
- Хранение лидов в PostgreSQL
- Авторизация через JWT (access + refresh токены)
- Управление пользователями (CRUD операции)

---

## 🧱 Стек технологий

- [FastAPI](https://fastapi.tiangolo.com/)
- [Telethon](https://docs.telethon.dev/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 2](https://docs.pydantic.dev/latest/)
- [Redis](https://redis.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [Arq](https://arq-docs.helpmanual.io/)
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

---

## 📋 Требования

- **Docker** и **Docker Compose**

---

## 🛠️ Локальный запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/VBulykov/telegram_leads_collector.git
cd telegram_leads_collector
```

### 2. Создание файла `.env`

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=telegram_leads
DB_ECHO=true or false

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis

# Fernet Key (для шифрования токенов)
# Сгенерируйте ключ командой: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY=your-fernet-key-here

# Telegram API (опционально, для будущего функционала)
# API_ID=your_api_id
# API_HASH=your_api_hash

# PgAdmin (опционально, для разработки)
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050
```

**Важно:** 
- Для Docker Compose используйте `POSTGRES_HOST=db` и `REDIS_HOST=redis`
- Сгенерируйте `FERNET_KEY` командой:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

### 3. Генерация JWT ключей

Для работы авторизации необходимо сгенерировать RSA ключи:

**Windows:**
```bash
python scripts/generate_jwt_keys.py
```

**Linux/macOS:**
```bash
python scripts/generate_jwt_keys.py
# или
bash scripts/generate_jwt_keys.sh
```

Ключи будут созданы в `src/auth/certs/`:
- `jwt-private.pem` - приватный ключ (для подписи токенов)
- `jwt-public.pem` - публичный ключ (для проверки токенов)

### 4. Запуск через Docker Compose

```bash
# Запуск всех сервисов
docker-compose -f docker-compose.development.yml up -d

# Просмотр логов
docker-compose -f docker-compose.development.yml logs -f

# Остановка сервисов
docker-compose -f docker-compose.development.yml down

# Остановка с удалением volumes (очистка БД)
docker-compose -f docker-compose.development.yml down -v
```

**Сервисы будут доступны:**
- FastAPI: http://localhost:8000
- API документация: http://localhost:8000/docs
- PgAdmin: http://localhost:5050
- PostgreSQL: localhost:5432
- Redis: localhost:6379

**Примечание:** Миграции применяются автоматически при первом запуске приложения.

---

## 📚 API Документация

После запуска приложения доступна интерактивная документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---


### Подключение к БД через PgAdmin

1. Откройте http://localhost:5050
2. Войдите с учетными данными из `.env` (`PGADMIN_EMAIL` и `PGADMIN_PASSWORD`)
3. Добавьте новый сервер:
   - **Host**: `db`
   - **Port**: `5432`
   - **Username**: `postgres` (или значение из `POSTGRES_USER`)
   - **Password**: `postgres` (или значение из `POSTGRES_PASSWORD`)
   - **Database**: `telegram_leads` (или значение из `POSTGRES_DB`)

---

## 🔧 Разработка

### Структура проекта

```
telegram_leads_collector/
├── src/
│   ├── auth/              # Модуль авторизации
│   │   ├── auth_models.py
│   │   ├── auth_schemas.py
│   │   ├── auth_routes.py
│   │   ├── auth_crud.py
│   │   ├── auth_dependencies.py
│   │   ├── auth_jwt_utils.py
│   │   └── certs/          # JWT ключи
│   ├── users/              # Модуль пользователей
│   │   ├── users_models.py
│   │   ├── users_schemas.py
│   │   ├── users_routes.py
│   │   ├── users_crud.py
│   │   └── services/
│   ├── database/           # Работа с БД
│   │   ├── engine.py
│   │   ├── base.py
│   │   ├── dependencies.py
│   │   ├── init_db.py
│   │   └── migration_runner.py
│   ├── config.py           # Конфигурация
│   └── main.py             # Точка входа
├── migrations/             # SQL миграции
├── scripts/                # Вспомогательные скрипты
├── docker-compose.development.yml
├── Dockerfile
└── requirements.txt
```

### Hot Reload

При запуске через `docker-compose.development.yml` включен hot reload - изменения в коде автоматически применяются без перезапуска контейнера.

### Логи

```bash
# Просмотр логов всех сервисов
docker-compose -f docker-compose.development.yml logs -f

# Логи только FastAPI
docker-compose -f docker-compose.development.yml logs -f web

# Логи только БД
docker-compose -f docker-compose.development.yml logs -f db
```

---
