from typing import List

from ..storages import LoanStorage
from ..schemas import Loan, LoanStatus, LoanCreate, LoanUpdate, LoanStatusUpdate
from ..models import Loan as LoanModel
from workers.dag_triggers import process_loan


class LoanCases:
    def __init__(self, loan_repo: LoanStorage):
        self._loan_repo = loan_repo

    async def list_loans(self, customer_id: int, status: LoanStatus) -> List[Loan]:
        return await self._loan_repo.list(customer_id, status)

    async def create_loan(self, customer_id: int, data: LoanCreate, employee_email: str) -> Loan:
        return await self._loan_repo.create(customer_id, data, employee_email)

    async def get_loan_details(self, customer_id: int, loan_id: int) -> Loan:
        loan = await self._loan_repo.get_loan(customer_id, loan_id)
        return Loan.model_validate(loan)

    async def update_loan(self, customer_id: int, loan_id: int, data: LoanUpdate, employee_data: dict) -> Loan:
        return await self._loan_repo.update_loan(customer_id, loan_id, data, employee_data)

    async def delete_loan(self, customer_id: int, loan_id: int, employee_data: dict) -> None:
        await self._loan_repo.delete(customer_id, loan_id, employee_data)

    async def process_loan(self, customer_id, loan_id, employee_data: dict) -> Loan:
        validated_loan = await self._loan_repo.validate_update(customer_id, loan_id, employee_data)

        decision_uid = await process_loan(validated_loan)

        data = LoanStatusUpdate(status=LoanModel.PROCESSING, decision_uid=decision_uid)

        return await self._loan_repo.update_loan(customer_id, loan_id, data, employee_data)
