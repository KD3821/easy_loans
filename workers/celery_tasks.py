from .celery_worker import celery_app
from .celery_db_functions import upload_transactions


@celery_app.task(serializer="pickle", acks_late=True)
def upload_csv_report(customer_id, file_data):
    return upload_transactions(customer_id, file_data)
