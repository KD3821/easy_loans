from datetime import date

from pydantic import BaseModel


class TransactionUpload(BaseModel):
    customer_id: int
    task_id: str
    start_date: date
    finish_date: date


class TransactionUploadCompleted(TransactionUpload):
    id: int
    status: str
