from typing import List

from sqlalchemy import select, or_, and_, desc, asc, func
from celery.result import AsyncResult

from db import async_session
from core import AppException, Pagination, PaginationOrder
from ..schemas import TransactionUpload, Transaction, TransactionList, TransactionUpdate
from ..models import Transaction as TransactionModel
from ..models import TransactionUpload as TransactionUploadModel
from scripts.seeds.transactions import create_csv_report
from apps.reports.schemas import ReportDates, ReportSettingsGenerate


class TransactionStorage:
    _table = TransactionModel
    _upload_table = TransactionUploadModel

    @classmethod
    async def check_overlapping_dates(cls, customer_id: int, dates: ReportDates) -> ReportDates:
        overlap_exc = AppException("generate_csv.overlapping_existing_reports")
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
                raise overlap_exc

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
                raise overlap_exc

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

    @classmethod
    async def check_upload_status(cls, customer_id: int, upload_id: int) -> dict:
        upload = await cls.get_upload(customer_id, upload_id)

        return {"status": upload.status, "result": AsyncResult(upload.task_id)}

    @classmethod
    async def get_upload(cls, customer_id: int, upload_id: int) -> TransactionUploadModel:
        async with async_session() as session:
            query = await session.execute(
                select(cls._upload_table).where(
                    and_(
                        cls._upload_table.id == upload_id,
                        cls._upload_table.customer_id == customer_id
                    )
                )
            )
            upload = query.scalars().first()

        if upload is None:
            raise AppException("check_upload.upload_not_found")

        return upload

    @classmethod
    async def get_uploads(cls, customer_id: int) -> List[TransactionUploadModel]:
        async with async_session() as session:
            query = await session.execute(
                select(cls._upload_table).filter(cls._upload_table.customer_id == customer_id)
            )
            uploads = query.scalars()

        return uploads

    @classmethod
    async def get_txn(cls, customer_id: int, transaction_id: int) -> TransactionModel:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).where(
                    and_(
                        cls._table.customer_id == customer_id,
                        cls._table.id == transaction_id
                    )
                )
            )
            transaction = query.scalars().first()

        if transaction is None:
            raise AppException("transaction_details.transaction_not_found")

        return transaction

    @classmethod
    async def get_one(cls, customer_id: int, transaction_id: int) -> Transaction:
        transaction = await cls.get_txn(customer_id, transaction_id)
        return Transaction.model_validate(transaction)

    @classmethod
    async def get_many(cls, customer_id: int, pagination: Pagination) -> TransactionList:
        async with async_session() as session:
            order = desc if pagination.order == PaginationOrder.DESC else asc
            query = await session.execute(
                select(cls._table)
                .filter(cls._table.customer_id == customer_id)
                .limit(pagination.per_page)
                .offset(pagination.page - 1 if pagination.page == 1 else (pagination.page - 1) * pagination.per_page)
                .order_by(order(cls._table.id))
            )
            transactions = query.scalars()
            count = await session.execute(
                select(func.count())
                .select_from(select(cls._table.id).where(
                    cls._table.customer_id == customer_id
                ).subquery())
            )
            transaction_count = count.scalar_one()

        transaction_list = [Transaction.model_validate(transaction) for transaction in transactions]

        return TransactionList(total=transaction_count, transactions=transaction_list)

    @classmethod
    async def update_transaction(cls, customer_id: int, transaction_id: int, data: TransactionUpdate) -> Transaction:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).where(
                    and_(
                        cls._table.customer_id == customer_id,
                        cls._table.id == transaction_id
                    )
                )
            )
            transaction = query.scalars().first()

            if data.category is not None:
                transaction.category = data.category
            if data.details is not None:
                transaction.details = data.details

            await session.commit()

        return Transaction.model_validate(transaction)
