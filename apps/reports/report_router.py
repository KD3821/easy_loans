from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from dependency_injector.wiring import inject, Provide

from core import BaseRoute, IsAuthenticated, ErrorDetails
from .cases.report_cases import ReportCases
from .schemas import ReportDates
from .containers import Container

router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(IsAuthenticated())],
    responses={
        401: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)


@router.post("/reports/{customer_id}", response_class=FileResponse)
@inject
async def generate_report(
    customer_id: int,
    report_dates: ReportDates,
    report_cases: ReportCases = Depends(Provide[Container.report_cases])
):
    return await report_cases.generate(customer_id, report_dates)
