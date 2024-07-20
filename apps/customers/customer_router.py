from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from core import BaseRoute, IsAuthenticated, ErrorDetails, Pagination, pagination_params, HasManagerRole
from .schemas import Customer, NewCustomer, CustomerUpdate, CustomerList
from .cases import CustomerCases
from .containers import Container


router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(IsAuthenticated())],
    responses={
        401: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)


@router.get("/customers", response_model=CustomerList)
@inject
async def get_customers(
    pagination: Annotated[Pagination, Depends(pagination_params)],
    customer_cases: CustomerCases = Depends(Provide[Container.customer_cases])
):
    return await customer_cases.get_customers(pagination)


@router.post("/customers", response_model=Customer)
@inject
async def create_customer(
    data: NewCustomer,
    customer_cases: CustomerCases = Depends(Provide[Container.customer_cases])
):
    return await customer_cases.create(data)


@router.get("/customers/{customer_id}", response_model=Customer)
@inject
async def get_customer(
    customer_id: int,
    customer_cases: CustomerCases = Depends(Provide[Container.customer_cases])
):
    return await customer_cases.get_customer(customer_id)


@router.patch("/customers/{customer_id}", response_model=Customer)
@inject
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    customer_cases: CustomerCases = Depends(Provide[Container.customer_cases])
):
    return await customer_cases.update(customer_id, data)


@router.delete("/customers/{customer_id}",
               response_model=Customer,
               dependencies=[Depends(HasManagerRole())],
               name="delete customer (manager role only)")
@inject
async def delete_customer(
    customer_id: int,
    customer_cases: CustomerCases = Depends(Provide[Container.customer_cases])
):

    return await customer_cases.delete(customer_id)
