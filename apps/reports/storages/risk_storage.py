from sqlalchemy import select, and_, or_

from db import async_session
from core import AppException
from apps.transactions.models import Transaction as TransactionModel
from ..models import Risk as RiskModel


class RiskStorage:
    _table = RiskModel
    _transaction_table = TransactionModel

    @classmethod
    async def validate_risk(cls, customer_id: int, transaction_id: int) -> TransactionModel:
        async with async_session() as session:
            sub_query = select(cls._transaction_table).where(
                and_(
                    cls._transaction_table.customer_id == customer_id,
                    cls._transaction_table.id == transaction_id
                )
            ).subquery()

            query = await session.execute(
                select(cls._table.id).where(
                    or_(
                        cls._table.details == sub_query.c.details,
                        cls._table.category == sub_query.c.category
                    )
                ).select_from(sub_query)
            )

            transaction = query.scalars().first()

            if transaction is None:
                raise AppException("validate_risk.no_risk_transaction")

        return transaction
