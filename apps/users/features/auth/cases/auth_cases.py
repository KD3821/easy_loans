from core import AppException, AuthToken

from apps.users.features.account_management.schemas import WorkerVerify
from apps.users.features.account_management.services import AccountService
from apps.users.schemas import TokenUser
from apps.users.schemas.user_create import ManagerCreate
from apps.users.storages import UsersStorage
from apps.users.storages.users_storage import validate_password

from ..schemas import (AccessTokenSchema, AuthResponse, ManagerSignUp,
                       RefreshTokenSchema, SignIn, WorkerSignUp)
from ..storages import SignInStorage


class AuthCases:
    def __init__(
        self,
        users_repo: UsersStorage,
        sign_in_repo: SignInStorage,
        account_service: AccountService,
    ):
        self._users_repo = users_repo
        self._sign_in_repo = sign_in_repo
        self._account_service = account_service

    async def sign_in(self, data: SignIn) -> AuthResponse:
        user = await self._users_repo.get_full_user(data.email)

        if not user:
            raise AppException("auth.user_not_found")

        if not user.is_verified:
            raise AppException("auth.user_not_verified")

        if not user or not validate_password(data.password, user.hashed_password):
            raise AppException("auth.email_password_invalid")

        token_user = TokenUser(email=user.email, role=user.role)
        tokens_pair = AuthToken.generate_pair(token_user.dict())
        await self._track_sign_in(token_user)

        return AuthResponse(user=user, **tokens_pair)

    async def _track_sign_in(self, user: TokenUser) -> None:
        await self._sign_in_repo.create(user)

    async def manager_sign_up(self, data: ManagerSignUp):
        user = await self._users_repo.get_token_user(data.email)

        if user:
            raise AppException("sign_up.user_exists")

        user = await self._users_repo.create_manager(ManagerCreate(**data.dict()))
        tokens_pair = AuthToken.generate_pair(user.dict())
        return AuthResponse(user=user, **tokens_pair)

    async def worker_sign_up(self, data: WorkerSignUp):
        user = await self._users_repo.get_full_user(data.email)

        if not user or not self._account_service.validate_access_code(
            data.access_code, user.hashed_password
        ):
            raise AppException("sign_up.invalid_access_code")

        if user.is_verified:
            raise AppException("sign_up.user_is_verified")

        user = await self._account_service.verify_worker(WorkerVerify(**data.dict()))
        token_pair = AuthToken.generate_pair(user.dict())

        return AuthResponse(user=user, **token_pair)

    async def refresh_token(self, data: RefreshTokenSchema) -> AccessTokenSchema:
        data = AuthToken.decrypt_token(data.refresh_token)

        user = await self._users_repo.get_full_user(data.get('email'))

        if not user.is_verified:
            raise AppException("auth.user_not_verified")

        return AccessTokenSchema(access_token=AuthToken.generate_access_token(data))
