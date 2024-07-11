from ..storages import ReportStorage, ReportSettingsStorage
from ..schemas import ReportDates
from apps.transactions.storages import TransactionStorage


class ReportCases:
    def __init__(
        self,
        report_settings_repo: ReportSettingsStorage,
        transaction_repo: TransactionStorage,
        report_repo: ReportStorage,
    ):
        self._report_settings_repo = report_settings_repo
        self._transaction_repo = transaction_repo
        self._report_repo = report_repo

    async def generate(self, customer_id: int, dates: ReportDates):
        rs_gen = await self._report_settings_repo.get_report_settings(customer_id)
        return await self._transaction_repo.generate_csv(rs_gen, dates)

