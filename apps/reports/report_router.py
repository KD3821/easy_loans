from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from dependency_injector.wiring import inject, Provide

from core import BaseRoute, IsAuthenticated, ErrorDetails
from apps.transactions.schemas import TransactionUploadCompleted
from .cases.report_cases import ReportCases
from .schemas import ReportDates, ReportUploaded, ReportResult
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
async def create_upload(
    customer_id: int,
    file: UploadFile = File(...),
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.create_upload(customer_id, file)


@router.get("/reports/{customer_id}/uploads", response_model=List[TransactionUploadCompleted])
@inject
async def list_uploads(
    customer_id: int,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.get_uploads(customer_id)


@router.get("/reports/{customer_id}/upload/{upload_id}/analyse")
@inject
async def analyse_upload(
    customer_id: int,
    upload_id: int,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.init_analysis(customer_id, upload_id)


@router.delete("/reports/{customer_id}/uploads/{upload_id}")
@inject
async def remove_upload(
    customer_id: int,
    upload_id: int,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.delete_upload(customer_id, upload_id)


@router.get("/reports/{customer_id}/uploads/{upload_id}/check")
@inject
async def check_upload_status(
    customer_id: int,
    upload_id: int,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.check_upload(customer_id, upload_id)


@router.get("/reports/{customer_id}/results", response_model=List[ReportResult])
@inject
async def list_analysis_results(
    customer_id: int,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.list_results(customer_id)


@router.get("/reports/{customer_id}/results/{analysis_id}", response_model=ReportResult)
@inject
async def get_analysis_result(
    customer_id: int,
    analysis_id: str,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.get_result_details(customer_id, analysis_id)
