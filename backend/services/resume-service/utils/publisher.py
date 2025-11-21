import os
import json
import pika
import logging

log = logging.getLogger("resume-publisher")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
ANALYSIS_QUEUE = os.getenv("ANALYSIS_QUEUE", "analysis.start")

def publish_resume(resume_id: str, user_id: str | None = None):
    return {"queued": False, "resume_id": resume_id}