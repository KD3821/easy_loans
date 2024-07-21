from typing import List

from ..storages import LoanStorage
from ..schemas import Loan, LoanStatus, LoanCreate, LoanUpdate


class LoanCases:
    def __init__(self, loan_repo: LoanStorage):
        self._loan_repo = loan_repo

    async def list_loans(self, customer_id: int, status: LoanStatus) -> List[Loan]:
        return await self._loan_repo.list(customer_id, status)

    async def create_loan(self, customer_id: int, data: LoanCreate, employee_email: str) -> Loan:
        return await self._loan_repo.create(customer_id, data, employee_email)

    async def get_loan_details(self, customer_id: int, loan_id: int) -> Loan:
        return await self._loan_repo.get_loan(customer_id, loan_id)

    async def update_loan(self, customer_id: int, loan_id: int, data: LoanUpdate, employee_data: dict) -> Loan:
        return await self._loan_repo.update_loan(customer_id, loan_id, data, employee_data)

    async def delete_loan(self, customer_id: int, loan_id: int, employee_data: dict) -> None:
        await self._loan_repo.delete(customer_id, loan_id, employee_data)
