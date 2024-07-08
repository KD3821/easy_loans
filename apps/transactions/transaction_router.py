from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, File, UploadFile

from core import IsAuthenticated, ErrorDetails, BaseRoute
from .schemas import ReportUploaded
from .cases import TransactionCases
from .containers import Container


router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(IsAuthenticated())],
    responses={
        401: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)


@router.post("/report", response_model=ReportUploaded)
@inject
async def upload_report(
    file: UploadFile = File(...),
    transaction_cases: TransactionCases = Depends(Provide[Container.transaction_cases])
):
    return await transaction_cases.upload_transactions(file)
