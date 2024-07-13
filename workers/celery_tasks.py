from .celery_worker import celery_app
from .celery_db_functions import upload_transactions


@celery_app.task(serializer="pickle", bind=True, acks_late=True)
def upload_csv_report(self, customer_id, file_data, upload_id):
    return upload_transactions(customer_id, file_data, upload_id, task_id=self.request.id)
