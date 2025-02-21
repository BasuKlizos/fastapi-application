from celery import Celery

from app.config import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
MONGO_URI = settings.MONGO_URI

celery_app = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/0",
    broker_connection_retry_on_startup = True
)

celery_app.conf.update(
    result_expire=3600,  # 3600 seconds -> 1 hrs.
)

celery_app.autodiscover_tasks(["app.utils.celery_tasks"])
