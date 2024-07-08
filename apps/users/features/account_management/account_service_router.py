from core import BaseRoute, ErrorDetails, HasManagerRole
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from .containers import Container
from .schemas import WorkerAccessCode, WorkerAccessCodeReset, WorkerCreate
from .services import AccountService

router = APIRouter(
    route_class=BaseRoute,
    dependencies=[Depends(HasManagerRole())],
    responses={
        401: {"model": ErrorDetails},
        403: {"model": ErrorDetails},
        404: {"model": ErrorDetails},
    },
)


@router.post("/new_worker", response_model=WorkerAccessCode)
@inject
async def create_worker(
    data: WorkerCreate,
    account_service: AccountService = Depends(Provide[Container.account_service]),
):
    return await account_service.create_worker(data)


@router.post("/access_code", response_model=WorkerAccessCode)
@inject
async def reset_access_code(
    data: WorkerAccessCodeReset,
    account_service: AccountService = Depends(Provide[Container.account_service]),
):
    return await account_service.reset_worker_access_code(data)


container = Container()
container.wire(modules=[__name__])
