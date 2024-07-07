from ..storages import CustomerStorage
from ..schemas import NewCustomer, Customer, CustomerUpdate, CustomerList


class CustomerCases:
    def __init__(self, customer_repo: CustomerStorage):
        self._customer_repo = customer_repo

    async def get_customer(self, customer_id: int) -> Customer:
        return await self._customer_repo.get_one(customer_id)

    async def get_customers(self, pagination) -> CustomerList:
        return await self._customer_repo.get_many(pagination)

    async def create(self, data: NewCustomer) -> Customer:
        return await self._customer_repo.create(data)

    async def update(self, customer_id: int, data: CustomerUpdate) -> Customer:
        return await self._customer_repo.update(customer_id, data)

    async def delete(self, customer_id: int) -> Customer:
        return await self._customer_repo.delete(customer_id)
