from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from core import IsAuthenticated, ErrorDetails, BaseRoute, Pagination, pagination_params
from .schemas import TransactionList, Transaction, TransactionUpdate
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


@router.get("/transactions/{customer_id}", response_model=TransactionList)
@inject
async def list_transactions(
    customer_id: int,
    pagination: Annotated[Pagination, Depends(pagination_params)],
    transaction_cases: TransactionCases = Depends(Provide[Container.transaction_cases])
):
    return await transaction_cases.list_transactions(customer_id, pagination)


@router.get("/transactions/{customer_id}/{transaction_id}", response_model=Transaction)
@inject
async def transaction_details(
    customer_id: int,
    transaction_id: int,
    transaction_cases: TransactionCases = Depends(Provide[Container.transaction_cases])
):
    return await transaction_cases.transaction_details(customer_id, transaction_id)


@router.patch("/transactions/{customer_id}/{transaction_id}", response_model=Transaction)
@inject
async def update_transaction(
    customer_id: int,
    transaction_id: int,
    data: TransactionUpdate,
    transaction_cases: TransactionCases = Depends(Provide[Container.transaction_cases])
):
    return await transaction_cases.update_transaction(customer_id, transaction_id, data)
