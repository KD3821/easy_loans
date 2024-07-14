from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from core import IsAuthenticated, ErrorDetails, BaseRoute
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
