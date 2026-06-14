from celery import Celery

from app.core.config import settings

celery_app = Celery("enterpriseos", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.notifications"])


@celery_app.task(name="enterpriseos.ping")
def ping() -> str:
    return "pong"
