from fastapi import UploadFile

from ..storages import TransactionStorage
from ..schemas import ReportUploaded
from core import AppException


class TransactionCases:
    def __init__(self, transaction_repo: TransactionStorage):
        self._transaction_repo = transaction_repo

    async def upload_transactions(self, file: UploadFile) -> ReportUploaded:
        if file.filename.endswith('.csv'):
            return await self._transaction_repo.import_csv(file)

        elif file.filename.endswith('.xlsx'):
            return await self._transaction_repo.import_xlsx(file)

        else:
            raise AppException("upload_file.unsupported_file_type")
