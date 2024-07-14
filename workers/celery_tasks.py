from typing import BinaryIO

from .celery_worker import celery_app
from .celery_db_functions import upload_transactions, delete_transactions


@celery_app.task(serializer="pickle", bind=True, acks_late=True)
def upload_csv_report(self, customer_id: int, file_data: BinaryIO, upload_id: int):
    return upload_transactions(customer_id, file_data, upload_id, task_id=self.request.id)


@celery_app.task(acks_late=True)
def delete_uploaded_report(customer_id: int, upload_id: int):
    return delete_transactions(customer_id, upload_id)
