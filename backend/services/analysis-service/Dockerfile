FROM python:3.11-slim

WORKDIR /app

# Установка локали и системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Настройка локали для поддержки UTF-8
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

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
