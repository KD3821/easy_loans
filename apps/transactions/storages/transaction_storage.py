from sqlalchemy import select, or_, and_

from db import async_session
from core.exceptions import AppException
from ..schemas import TransactionUpload
from ..models import Transaction as TransactionModel
from ..models import TransactionUpload as TransactionUploadModel
from scripts.seeds.transactions import create_csv_report
from apps.reports.schemas import ReportDates, ReportSettingsGenerate


class TransactionStorage:
    _table = TransactionModel
    _upload_table = TransactionUploadModel

    @classmethod
    async def check_overlapping_dates(cls, customer_id: int, dates: ReportDates) -> ReportDates:
        async with async_session() as session:
            query = await session.execute(
                select(cls._upload_table).where(
                    or_(
                        and_(
                            cls._upload_table.customer_id == customer_id,
                            cls._upload_table.start_date <= dates.start_date,
                            cls._upload_table.finish_date >= dates.start_date
                        ),
                        and_(
                            cls._upload_table.customer_id == customer_id,
                            cls._upload_table.start_date <= dates.finish_date,
                            cls._upload_table.finish_date >= dates.finish_date,
                        )
                    )
                )
            )
            partial_overlap = query.scalar()

            if partial_overlap:
                raise AppException("gen_csv.partial_overlapping_existing_reports")

            query = await session.execute(
                select(cls._upload_table).filter(
                    and_(
                        cls._upload_table.customer_id == customer_id,
                        cls._upload_table.start_date >= dates.start_date,
                        cls._upload_table.finish_date <= dates.finish_date
                    )
                )
            )
            total_overlap = query.scalar()

            if total_overlap:
                raise AppException("gen_csv.total_overlapping_existing_reports")
        return dates

    @classmethod
    async def generate_csv(cls, gen_data: ReportSettingsGenerate, dates: ReportDates):
        dates = await cls.check_overlapping_dates(gen_data.customer_id, dates)
        data = (
            gen_data.customer_id,
            float(gen_data.monthly_income),
            float(gen_data.starting_balance),
            gen_data.first_income_day,
            gen_data.second_income_day,
            float(gen_data.rental_rate),
            gen_data.employer,
            gen_data.have_risks
        )
        filepath, filename = create_csv_report(
            data=data,
            dates=[dates.start_date, dates.finish_date],
            first_income=float(gen_data.first_income),
            second_income=float(gen_data.second_income),
            save_balance=float(gen_data.save_balance),
            risks=gen_data.risks
        )
        return filepath, filename

    @classmethod
    async def create_upload(cls, data: dict) -> TransactionUploadModel:
        valid_upload = TransactionUpload(**data)

        async with async_session() as session:
            new_txn_upload = TransactionUploadModel(**valid_upload.dict())
            session.add(new_txn_upload)
            await session.commit()

        return new_txn_upload
