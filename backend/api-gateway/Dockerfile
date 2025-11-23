FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements (только их сначала) и установка зависимостей
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остального кода (после установки зависимостей)
COPY . .

# Создание пользователя для безопасности
RUN useradd -r -s /bin/false apigateway
# USER apigateway  # Отключено для live-монтирования и прав записи

# Экспорт порта
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
