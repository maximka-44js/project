FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY services/analysis-service/requirements.txt ./requirements.txt
COPY shared/requirements.txt ./shared-requirements.txt

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r shared-requirements.txt

# Копирование кода
COPY services/analysis-service/ /app/
COPY shared/ /app/shared/

# Создание директорий для логов
RUN mkdir -p /app/logs

EXPOSE 8004

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]
