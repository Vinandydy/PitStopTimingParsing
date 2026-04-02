FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

RUN chmod +x cli.py

# Создаем alias и делаем cli.py исполняемым
RUN echo '#!/bin/bash\n\
cd /app\n\
python cli.py "$@"\n\
' > /usr/local/bin/karting && chmod +x /usr/local/bin/karting

# Держим контейнер запущенным
CMD ["sleep", "infinity"]