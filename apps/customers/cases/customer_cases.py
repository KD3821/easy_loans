from ..storages import CustomerStorage
from ..schemas import NewCustomer, Customer, CustomerUpdate, CustomerList
from apps.reports.storages import ReportSettingsStorage
from apps.reports.schemas.report_settings import ReportSettingsCreate


class CustomerCases:
    def __init__(self, customer_repo: CustomerStorage, report_settings_repo: ReportSettingsStorage):
        self._customer_repo = customer_repo
        self._report_settings_repo = report_settings_repo

    async def get_customer(self, customer_id: int) -> Customer:
        return await self._customer_repo.get_one(customer_id)

    async def get_customers(self, pagination) -> CustomerList:
        return await self._customer_repo.get_many(pagination)

    async def create(self, data: NewCustomer) -> Customer:
        new_customer = await self._customer_repo.create(data)
        rs_data = ReportSettingsCreate(
            customer_email=data.email, monthly_income=data.monthly_income, employer=data.employer
        )
        await self._report_settings_repo.create(rs_data)
        return new_customer

    async def update(self, customer_id: int, data: CustomerUpdate) -> Customer:
        return await self._customer_repo.update(customer_id, data)

    async def delete(self, customer_id: int) -> Customer:
        return await self._customer_repo.delete(customer_id)
