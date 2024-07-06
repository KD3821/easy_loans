from ..storages import CustomerStorage
from ..schemas import NewCustomer, Customer


class CustomerCases:
    def __init__(self, customer_repo: CustomerStorage):
        self._customer_repo = customer_repo

    async def create(self, data: NewCustomer) -> Customer:
        return await self._customer_repo.create(data)
