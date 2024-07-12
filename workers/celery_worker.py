from celery import Celery

from settings import CELERY_BROKER_URL, CELERY_ACCEPT_CONTENT


celery_app = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend="rpc://",
    include=["workers.celery_tasks"],
    accept_content=CELERY_ACCEPT_CONTENT
)
