FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование shared модулей
COPY ../../shared ./shared

# Копирование кода приложения
COPY . .

# Создание пользователя для безопасности
RUN useradd -r -s /bin/false userservice
USER userservice

# Экспорт порта
EXPOSE 8001

# Команда запуска
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
