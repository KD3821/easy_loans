from fastapi import UploadFile
from pydantic import ValidationError

from core import AppException

from apps.transactions.storages import TransactionStorage
from ..schemas import ReportDates, ReportUploaded
from ..storages import ReportStorage, ReportSettingsStorage
from workers.celery_tasks import upload_csv_report


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

    @staticmethod
    async def check_filename(customer_id: int, filename: str) -> dict:
        if not filename.endswith('.csv'):
            raise AppException("upload_file.unsupported_file_type")

        filename_data = filename.split(".")[0].split("_")
        _, cus_id, start_date, finish_date = filename_data

        if customer_id != int(cus_id):
            raise AppException("upload_file.wrong_customer_id")

        try:
            ReportDates.model_validate({"start_date": start_date, "finish_date": finish_date})
        except ValidationError as e:
            raise AppException(f"upload_file.{e.errors()[0]['msg']}")

        valid_data = {
            "customer_id": customer_id,
            "start_date": start_date,
            "finish_date": finish_date,
        }

        return valid_data

    async def generate(self, customer_id: int, dates: ReportDates):
        gen_data = await self._report_settings_repo.get_report_settings(customer_id)

        return await self._transaction_repo.generate_csv(gen_data, dates)

    async def create_report(self, customer_id: int, file: UploadFile) -> ReportUploaded:
        file_data = await self.check_filename(customer_id, file.filename)

        task = upload_csv_report.delay(customer_id, file.file)

        file_data.update({"task_id": task.id})

        await self._transaction_repo.create_upload(file_data)

        return ReportUploaded(filename=file.filename, task_id=task.id)
