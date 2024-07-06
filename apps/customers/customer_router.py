from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from core import BaseRoute, IsAuthenticated, ErrorDetails
from .schemas.customer import Customer, NewCustomer
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


@router.post("/customer", response_model=Customer)
@inject
async def create_customer(
    data: NewCustomer,
    customer_cases: CustomerCases = Depends(Provide[Container.customer_cases])
):
    return await customer_cases.create(data)
