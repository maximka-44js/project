import os
from celery import Celery
from kombu import Queue

# Получаем настройки Redis из переменных окружения
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

# URL для подключения к Redis
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Создаем экземпляр Celery
celery_app = Celery(
    "analysis-service",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['tasks.analysis_tasks']  # Импортируем наши задачи
)

# Настройки Celery для продакшена
celery_app.conf.update(
    # Результаты задач хранятся 24 часа
    result_expires=86400,
    
    # Настройки сериализации
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Настройки очередей для анализа резюме
    task_routes={
        'tasks.analysis_tasks.*': {'queue': 'analysis'},
    },
    
    # Определяем очереди
    task_queues=(
        Queue('analysis', routing_key='analysis'),
    ),
    
    # Настройки воркера для стабильной работы
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,  # Перезапуск воркера после 1000 задач
    
    # Логирование
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks()

if __name__ == '__main__':
    celery_app.start()