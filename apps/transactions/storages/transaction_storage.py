import csv

from fastapi import UploadFile

from db import async_session
from ..schemas import NewTransaction, ReportUploaded
from ..models import Transaction as TransactionModel


class TransactionStorage:
    _table = TransactionModel

    @classmethod
    async def import_csv(cls, file: UploadFile) -> ReportUploaded:
        reader = csv.DictReader(
            (line.decode() for line in file.file)
        )
        transactions = []
        next(reader)  # to skip reading of header part
        for row in reader:
            transaction_data = NewTransaction.model_validate(row)
            transactions.append(cls._table(**transaction_data.dict()))
        async with async_session() as session:
            session.add_all(transactions)
            await session.commit()
        file.file.close()
        return ReportUploaded(filename=file.filename)

    @classmethod
    async def import_xlsx(cls, file: UploadFile):
        pass
