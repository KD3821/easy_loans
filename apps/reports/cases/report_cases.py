from typing import List

from fastapi import UploadFile
from pydantic import ValidationError

from core import AppException
from apps.transactions.storages import TransactionStorage
from apps.transactions.schemas import TransactionUploadCompleted
from ..schemas import ReportDates, ReportUploaded, ReportStatus, ReportDeleted
from ..storages import ReportStorage, ReportSettingsStorage
from workers.celery_tasks import upload_csv_report, delete_uploaded_report
from workers.dag_triggers import analyze_report


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
            "task_id": "N/A"
        }

        return valid_data

    async def generate(self, customer_id: int, dates: ReportDates):
        gen_data = await self._report_settings_repo.get_report_settings(customer_id)

        return await self._transaction_repo.generate_csv(gen_data, dates)

    async def create_upload(self, customer_id: int, file: UploadFile) -> ReportUploaded:
        file_data = await self.check_filename(customer_id, file.filename)

        await self._transaction_repo.check_overlapping_dates(
            customer_id,
            ReportDates(start_date=file_data.get("start_date"), finish_date=file_data.get("finish_date"))
        )

        txn_upload = await self._transaction_repo.create_upload(file_data)

        task = upload_csv_report.delay(customer_id, file.file, upload_id=txn_upload.id)

        return ReportUploaded(id=txn_upload.id, filename=file.filename, task_id=task.id)

    async def check_upload(self, customer_id: int, upload_id: int) -> ReportStatus:
        upload_result = await self._transaction_repo.check_upload_status(customer_id, upload_id)

        return ReportStatus(
            id=upload_id, status=upload_result.get("status"), result=upload_result.get("result").info
        )

    async def get_uploads(self, customer_id: int) -> List[TransactionUploadCompleted]:
        return await self._transaction_repo.get_uploads(customer_id)

    async def delete_upload(self, customer_id: int, upload_id: int):
        upload = await self._transaction_repo.get_upload(customer_id, upload_id)

        task = delete_uploaded_report.delay(customer_id, upload.id)

        return ReportDeleted(id=upload.id, task_id=task.id)

    async def init_analysis(self, customer_id: int, upload_id: int):
        upload = await self._transaction_repo.get_upload(customer_id, upload_id)

        analysis_id = await analyze_report(upload)

        return {'upload_id': upload_id, 'details': {'customer_id': customer_id, 'analysis_id': analysis_id}}
