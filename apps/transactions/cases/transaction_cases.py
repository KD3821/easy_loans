from core import Pagination
from apps.reports.storages import RiskStorage
from ..storages import TransactionStorage
from ..schemas import Transaction, TransactionList, TransactionUpdate


class TransactionCases:
    def __init__(self, transaction_repo: TransactionStorage, risk_repo: RiskStorage):
        self._transaction_repo = transaction_repo
        self._risk_repo = risk_repo

    async def list_transactions(self, customer_id: int, pagination: Pagination) -> TransactionList:
        return await self._transaction_repo.get_many(customer_id, pagination)

    async def transaction_details(self, customer_id: int, transaction_id: int) -> Transaction:
        return await self._transaction_repo.get_one(customer_id, transaction_id)

    async def update_transaction(self, customer_id: int, transaction_id: int, data: TransactionUpdate) -> Transaction:
        await self._risk_repo.validate_risk(customer_id, transaction_id)

        return await self._transaction_repo.update_transaction(customer_id, transaction_id, data)
