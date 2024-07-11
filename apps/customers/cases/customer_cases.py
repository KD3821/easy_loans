from ..storages import CustomerStorage
from ..schemas import NewCustomer, Customer, CustomerUpdate, CustomerList
from apps.reports.storages import ReportSettingsStorage
from apps.reports.schemas.report_settings import ReportSettingsCreate, ReportSettingsUpdate


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
            customer_id=new_customer.id, monthly_income=new_customer.monthly_income, employer=new_customer.employer
        )
        await self._report_settings_repo.create(rs_data)
        return new_customer

    async def update(self, customer_id: int, data: CustomerUpdate) -> Customer:
        updated_customer = await self._customer_repo.update(customer_id, data)
        if data.monthly_income is not None or data.employer is not None:
            rs_data = ReportSettingsUpdate(
                monthly_income=data.monthly_income, employer=data.employer
            )
            rs = await self._report_settings_repo.update(customer_id, rs_data)
            print(f"{rs=}")
        return updated_customer

    async def delete(self, customer_id: int) -> Customer:
        return await self._customer_repo.delete(customer_id)
