from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from dependency_injector.wiring import inject, Provide

from core import BaseRoute, IsAuthenticated, ErrorDetails
from apps.transactions.schemas import TransactionUpload
from .cases.report_cases import ReportCases
from .schemas import ReportDates, ReportUploaded
from .containers import Container

router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(IsAuthenticated())],
    responses={
        401: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)


@router.post("/reports/{customer_id}/csv", response_class=FileResponse)
@inject
async def generate_transactions_csv(
    customer_id: int,
    report_dates: ReportDates,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    filepath, filename = await report_cases.generate(customer_id, report_dates)
    return FileResponse(
        filepath,
        media_type='application/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@router.post("/reports/{customer_id}/uploads", response_model=ReportUploaded)
@inject
async def create_report(
    customer_id: int,
    file: UploadFile = File(...),
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.create_report(customer_id, file)


@router.get("/reports/{customer_id}/uploads", response_model=List[TransactionUpload])
@inject
async def list_uploads(
    customer_id: int,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.get_uploads(customer_id)


@router.get("/reports/{customer_id}/uploads/{upload_id}/check")
@inject
async def check_upload_status(
    customer_id: int,
    upload_id: int,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.check_upload(customer_id, upload_id)
