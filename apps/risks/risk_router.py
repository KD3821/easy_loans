from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from core import HasManagerRole, ErrorDetails, BaseRoute, Pagination, pagination_params
from .containers import Container
from .cases import RiskCases
from .schemas import RiskList


router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(HasManagerRole())],
    responses={
        401: {"model": ErrorDetails},
        403: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)


@router.get("/risks", response_model=RiskList, name="list risks (manager role only)")
@inject
async def list_risks(
    pagination: Annotated[Pagination, Depends(pagination_params)],
    risk_cases: RiskCases = Depends(Provide[Container.risk_cases])
):
    return await risk_cases.list_risks(pagination)
