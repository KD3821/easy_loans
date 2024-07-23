from typing import List

from sqlalchemy import select, and_

from db import async_session
from core import AppException
from ..schemas import Loan, LoanStatus, LoanCreate, LoanUpdate, LoanStatusUpdate
from ..models import Loan as LoanModel
from apps.users.models import User as UserModel


class LoanStorage:
    _table = LoanModel

    @classmethod
    async def validate_update(cls, customer_id: int, loan_id: id, employee_data: dict) -> LoanModel:
        loan = await cls.get_loan(customer_id, loan_id)
        if loan.status != cls._table.CREATED:
            raise AppException("modify_loan.loan_is_proceeded")
        if loan.processed_by != employee_data.get("email") and employee_data.get("role") != UserModel.MANAGER:
            raise AppException("modify_loan.employee_not_assigned")
        return loan

    @classmethod
    async def get_loan(cls, customer_id: int, loan_id: int) -> LoanModel:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).where(
                    and_(
                        cls._table.customer_id == customer_id,
                        cls._table.id == loan_id
                    )
                )
            )
            loan = query.scalars().first()

            if not loan:
                raise AppException("get_loan.loan_not_found")

        return loan

    @classmethod
    async def list(cls, customer_id: int, status: LoanStatus | None = None) -> List[Loan]:
        async with async_session() as session:
            query = select(cls._table).filter(cls._table.customer_id == customer_id)

            if status:
                query = query.filter_by(status=status)

            result = await session.execute(query)
            loans = result.scalars()

        loans = [Loan.model_validate(loan) for loan in loans]

        return loans

    @classmethod
    async def create(cls, customer_id: int, data: LoanCreate, employee_email: str) -> Loan:
        async with async_session() as session:
            new_loan = LoanModel(
                customer_id=customer_id,
                coapplicant_fullname=data.coapplicant_fullname,
                coapplicant_income=data.coapplicant_income,
                amount=data.amount,
                month_term=data.month_term,
                processed_by=employee_email
            )

            session.add(new_loan)
            await session.commit()
            await session.refresh(new_loan)

        return Loan.model_validate(new_loan)

    @classmethod
    async def update_loan(
            cls, customer_id: int, loan_id: int, data: LoanUpdate | LoanStatusUpdate, employee_data: dict
    ) -> Loan:
        validated_loan = await cls.validate_update(customer_id, loan_id, employee_data)
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).where(
                    and_(
                        cls._table.customer_id == validated_loan.customer_id,
                        cls._table.id == validated_loan.id
                    )
                )
            )
            loan = query.scalars().first()

            for field, value in data.dict().items():
                if field in ("cooapplicant_fullname", "cooplicant_income") or value is not None:
                    setattr(loan, field, value)

            await session.commit()
            await session.refresh(loan)

        return Loan.model_validate(loan)

    @classmethod
    async def delete(cls, customer_id: int, loan_id: int, employee_data: dict) -> None:
        validated_loan = await cls.validate_update(customer_id, loan_id, employee_data)
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).where(
                    and_(
                        cls._table.customer_id == validated_loan.customer_id,
                        cls._table.id == validated_loan.id
                    )
                )
            )
            loan = query.scalars().first()

            await session.delete(loan)
            await session.commit()
