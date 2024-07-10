from sqlalchemy.future import select
from sqlalchemy import desc, asc, func

from core import AppException, PaginationOrder
from db import async_session
from ..models.customer import Customer as CustomerModel
from ..schemas import NewCustomer, Customer, CustomerUpdate, CustomerList


class CustomerStorage:
    _table = CustomerModel

    @classmethod
    async def get_one(cls, customer_id: int) -> Customer:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.id == customer_id)
            )
            customer = query.scalars().first()

            if customer is None:
                raise AppException("customer_one.customer_not_found")

        return Customer.model_validate(customer)

    @classmethod
    async def get_many(cls, pagination) -> CustomerList:
        async with async_session() as session:
            order = desc if pagination.order == PaginationOrder.DESC else asc
            query = await session.execute(
                select(cls._table)
                .limit(pagination.per_page)
                .offset(pagination.page - 1 if pagination.page == 1 else (pagination.page - 1) * pagination.per_page)
                .order_by(order(cls._table.id))
            )
            customers = query.scalars()
            count = await session.execute(
                select(func.count())
                .select_from(select(cls._table.id).subquery())
            )
            customer_count = count.scalar_one()

        customer_list = [Customer.model_validate(customer) for customer in customers]

        return CustomerList(total=customer_count, customers=customer_list)

    @classmethod
    async def create(cls, customer: NewCustomer) -> Customer:
        async with async_session() as session:
            customer_model = cls._table(
                fullname=customer.fullname,
                email=customer.email,
                gender=customer.gender,
                birthdate=customer.birthdate,
                education=customer.education,
                children=customer.children,
                self_employed=customer.self_employed,
                employer=customer.employer,
                monthly_income=customer.monthly_income,
                property_area=customer.property_area,
                credit_history=customer.credit_history,
            )

            session.add(customer_model)
            await session.commit()

        return Customer.model_validate(customer_model)

    @classmethod
    async def update(cls, customer_id: int, data: CustomerUpdate) -> Customer:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.id == customer_id)
            )
            customer = query.scalars().first()

            if customer is None:
                raise AppException("customer_update.customer_not_found")

            for field, value in data.dict().items():
                if value is not None:
                    setattr(customer, field, value)

            await session.commit()

        return Customer.model_validate(customer)

    @classmethod
    async def delete(cls, customer_id: int) -> Customer:
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.id == customer_id)
            )
            customer = query.scalars().first()

            if customer is None:
                raise AppException("customer_delete.customer_not_found")

            await session.delete(customer)
            await session.commit()

        return Customer.model_validate(customer)
