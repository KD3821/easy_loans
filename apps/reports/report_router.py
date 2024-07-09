from fastapi import APIRouter, Depends

from core import BaseRoute, IsAuthenticated, ErrorDetails


router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(IsAuthenticated())],
    responses={
        401: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)
