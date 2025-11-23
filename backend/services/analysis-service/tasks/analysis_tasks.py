import time
import logging
from celery import current_task
from celery_app import celery_app

log = logging.getLogger(__name__)


# Здесь будут настоящие задачи для анализа резюме
# Примеры задач удалены для продакшена