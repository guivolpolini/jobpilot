import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "jobpilot_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
)

# Importação de tarefas para registro do worker
celery_app.autodiscover_tasks(["app.workers"])
