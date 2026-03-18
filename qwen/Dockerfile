FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей и установка
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY backend .

# Создание директории для логов
RUN mkdir -p /app/logs

# Проверка здоровья (опционально)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/ || exit 1

# Запуск сервера
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]