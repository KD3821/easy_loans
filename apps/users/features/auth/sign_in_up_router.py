from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from .schemas import SignIn, AuthResponse, ManagerSignUp, WorkerSignUp, RefreshTokenSchema, AccessTokenSchema
from .cases import AuthCases
from .containers import Container

router = APIRouter()


@router.post("/manager_sign_up", response_model=AuthResponse)
@inject
async def manager_sign_up(data: ManagerSignUp, auth_cases: AuthCases = Depends(Provide[Container.auth_cases])):
    return await auth_cases.manager_sign_up(data)


@router.post("/worker_sign_up", response_model=AuthResponse)
@inject
async def worker_sign_up(data: WorkerSignUp, auth_cases: AuthCases = Depends(Provide[Container.auth_cases])):
    return await auth_cases.worker_sign_up(data)


@router.post("/sign_in", response_model=AuthResponse)
@inject
async def sign_in(data: SignIn, auth_cases: AuthCases = Depends(Provide[Container.auth_cases])):
    return await auth_cases.sign_in(data)


@router.post("/refresh_token", response_model=AccessTokenSchema)
@inject
async def refresh_token(data: RefreshTokenSchema, auth_cases: AuthCases = Depends(Provide[Container.auth_cases])):
    return await auth_cases.refresh_token(data)


container = Container()
container.wire(modules=[__name__])
