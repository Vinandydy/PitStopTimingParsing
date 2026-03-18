# cli/Dockerfile
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей и установка
COPY cli/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода CLI
COPY cli/ .

# Создание директории для кэша и конфига
RUN mkdir -p /root/.karting

# Переменная окружения по умолчанию
ENV KARTING_API_URL=http://backend:8000/api

# По умолчанию показываем справку
CMD ["python", "-m", "karting", "--help"]