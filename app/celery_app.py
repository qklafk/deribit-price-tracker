"""Конфигурация Celery."""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "deribit_price_tracker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "fetch-prices-every-minute": {
            "task": "app.tasks.fetch_prices",
            "schedule": 60.0,  # каждую минуту (ровно 60 секунд)
        },
    },
    # Настройки для точного выполнения задач
    beat_schedule_filename="celerybeat-schedule",
    worker_prefetch_multiplier=1,  # Обрабатывать по одной задаче за раз
    task_acks_late=True,  # Подтверждать задачу только после выполнения
    worker_max_tasks_per_child=50,  # Перезапускать worker после N задач для стабильности
)
