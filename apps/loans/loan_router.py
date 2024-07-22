from typing import List

from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import inject, Provide

from core import BaseRoute, IsAuthenticated, ErrorDetails
from .schemas import Loan, LoanStatus, LoanCreate, LoanUpdate
from .containers import Container
from .cases import LoanCases


router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(IsAuthenticated())],
    responses={
        401: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)


@router.get("/loans/{customer_id}", response_model=List[Loan])
@inject
async def list_loans(
    customer_id: int,
    status: LoanStatus | None = None,
    loan_case: LoanCases = Depends(Provide[Container.loan_cases])
):
    return await loan_case.list_loans(customer_id, status)


@router.post("/loans/{customer_id}", response_model=Loan)
@inject
async def create_loan(
    customer_id: int,
    data: LoanCreate,
    request: Request,
    loan_cases: LoanCases = Depends(Provide[Container.loan_cases])
):
    employee_email = request.state.user.email
    return await loan_cases.create_loan(customer_id, data, employee_email)


@router.get("/loans/{customer_id}/{loan_id}", response_model=Loan)
@inject
async def get_loan_details(
    customer_id: int,
    loan_id: int,
    loan_cases: LoanCases = Depends(Provide[Container.loan_cases])
):
    return await loan_cases.get_loan_details(customer_id, loan_id)


@router.patch("/loans/{customer_id}/{loan_id}", response_model=Loan)
@inject
async def update_loan(
    customer_id: int,
    loan_id: int,
    data: LoanUpdate,
    request: Request,
    loan_cases: LoanCases = Depends(Provide[Container.loan_cases])
):
    employee_data = {
        "email": request.state.user.email,
        "role": request.state.user.role
    }
    return await loan_cases.update_loan(customer_id, loan_id, data, employee_data)


@router.delete("/loans/{customer_id}/{loan_id}", status_code=204)
@inject
async def delete_loan(
    customer_id: int,
    loan_id: int,
    request: Request,
    loan_cases: LoanCases = Depends(Provide[Container.loan_cases])
):
    employee_data = {
        "email": request.state.user.email,
        "role": request.state.user.role
    }
    return await loan_cases.delete_loan(customer_id, loan_id, employee_data)


@router.post("/loans/{customer_id}/{loan_id}/process", response_model=Loan)
@inject
async def process_loan(
    customer_id: int,
    loan_id: int,
    request: Request,
    loan_cases: LoanCases = Depends(Provide[Container.loan_cases])
):
    employee_data = {
        "email": request.state.user.email,
        "role": request.state.user.role
    }
    return await loan_cases.process_loan(customer_id, loan_id, employee_data)
