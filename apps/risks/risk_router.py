from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from core import HasManagerRole, ErrorDetails, BaseRoute, Pagination, pagination_params
from .containers import Container
from .cases import RiskCases
from .schemas import RiskList, Risk, RiskCreate, RiskUpdate


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


@router.post("/risks", response_model=Risk, name="create risk (manager role only)")
@inject
async def create_risk(
    data: RiskCreate,
    risk_cases: RiskCases = Depends(Provide[Container.risk_cases])
):
    return await risk_cases.create_risk(data)


@router.get("/risks/{risk_id}", response_model=Risk, name="risk info (manager role only)")
@inject
async def get_risk(
    risk_id: int,
    risk_cases: RiskCases = Depends(Provide[Container.risk_cases])
):
    return await risk_cases.get_risk(risk_id)


@router.patch("/risks/{risk_id}", response_model=Risk, name="update risk (manager role only)")
@inject
async def update_risk(
    risk_id: int,
    data: RiskUpdate,
    risk_cases: RiskCases = Depends(Provide[Container.risk_cases])
):
    return await risk_cases.update_risk(risk_id, data)


@router.delete("/risks/{risk_id}", status_code=204, name="delete risk (manager role only)")
@inject
async def delete_risk(
    risk_id: int,
    risk_cases: RiskCases = Depends(Provide[Container.risk_cases])
):
    return await risk_cases.delete_risk(risk_id)
