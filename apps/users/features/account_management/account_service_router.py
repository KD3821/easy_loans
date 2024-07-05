from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from .schemas import WorkerCreate, WorkerAccessCode
from .services import AccountService
from .containers import Container
from core import IsAuthenticated, ErrorDetails, BaseRoute


router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(IsAuthenticated())],
    responses={
        401: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    }
)


@router.post("/new_worker", response_model=WorkerAccessCode)
@inject
async def create_worker(
        data: WorkerCreate, account_service: AccountService = Depends(Provide[Container.account_service])
):
    return await account_service.create_worker(data)


container = Container()
container.wire(modules=[__name__])
