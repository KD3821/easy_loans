from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from core import BaseRoute, ErrorDetails, IsAuthenticated, verify_api_key
from .containers import Container
from .schemas import LoanStatusUpdate, DecisionNotification, Decision
from .cases import LoanCases


router = APIRouter(
    route_class=BaseRoute,
    responses={
        401: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)


@router.post("/decisions/notify", dependencies=[Depends(verify_api_key)], response_model=LoanStatusUpdate)
@inject
async def decisions_webhook(
    data: DecisionNotification,
    loan_cases: LoanCases = Depends(Provide[Container.loan_cases])
):
    return await loan_cases.process_notification(data)


@router.get("/decisions/{decision_uid}", dependencies=[Depends(IsAuthenticated())], response_model=Decision)
@inject
async def get_decision_details(
    decision_uid: str,
    loan_cases: LoanCases = Depends(Provide[Container.loan_cases])
):
    return await loan_cases.get_decision_details(decision_uid)
