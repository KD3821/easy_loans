import csv

from fastapi import UploadFile

from db import async_session
from ..schemas import NewTransaction, ReportUploaded
from ..models import Transaction as TransactionModel
from scripts.seeds.transactions import create_csv_report
from apps.reports.schemas import ReportDates, ReportSettingsGenerate


class TransactionStorage:
    _table = TransactionModel

    @classmethod
    async def generate_csv(cls, rs: ReportSettingsGenerate, dates: ReportDates):
        data = (
            rs.customer_id,
            float(rs.monthly_income),
            float(rs.starting_balance),
            rs.first_income_day,
            rs.second_income_day,
            float(rs.rental_rate),
            rs.employer,
            rs.have_risks
        )
        filepath, filename = create_csv_report(
            data=data,
            dates=[dates.start_date, dates.finish_date],
            first_income=float(rs.first_income),
            second_income=float(rs.second_income),
            save_balance=float(rs.save_balance),
            risks=rs.risks
        )
        return filepath, filename

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
