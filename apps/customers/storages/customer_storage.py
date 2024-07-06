from db import async_session
from ..models.customer import Customer as CustomerModel
from ..schemas.customer import NewCustomer, Customer


class CustomerStorage:
    _table = CustomerModel

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
                property_area=customer.property_area,
                credit_history=customer.credit_history,
            )
            session.add(customer_model)
            await session.commit()

        return Customer.model_validate(customer_model)
