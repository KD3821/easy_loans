from core import AuthToken, AppException
from apps.users.schemas import FullUser
from apps.users.storages import UsersStorage
from apps.users.schemas.user_create import ManagerCreate
from apps.users.storages.users_storage import validate_password
from apps.users.features.account_management.services import AccountService
from apps.users.features.account_management.schemas import WorkerVerify
from ..storages import SignInStorage
from ..schemas import AuthResponse,  AccessTokenSchema, RefreshTokenSchema, SignIn, ManagerSignUp, WorkerSignUp


class AuthCases:
    def __init__(self, users_repo: UsersStorage, sign_in_repo: SignInStorage, account_service: AccountService):
        self._users_repo = users_repo
        self._sign_in_repo = sign_in_repo
        self._account_service = account_service

    async def sign_in(self, data: SignIn) -> AuthResponse:
        user = await self._users_repo.get_user_by_identity(data.email)

        if not user or not validate_password(data.password, user.hashed_password):
            raise AppException("auth.email_password_invalid")

        tokens_pair = AuthToken.generate_pair(user.dict())
        await self._track_sign_in(user)
        return AuthResponse(user=user, **tokens_pair)

    async def _track_sign_in(self, user: FullUser) -> None:
        await self._sign_in_repo.create(user)

    async def manager_sign_up(self, data: ManagerSignUp):
        user = await self._users_repo.get_user_by_identity(data.email)

        if user:
            raise AppException("sign_up.user_exists")

        user = await self._users_repo.create_manager(ManagerCreate(**data.dict()))
        tokens_pair = AuthToken.generate_pair(user.dict())
        return AuthResponse(user=user, **tokens_pair)

    async def worker_sign_up(self, data: WorkerSignUp):
        user = await self._users_repo.get_user_by_identity(data.email)

        if not user or not self._account_service.validate_access_code(data.access_code, user.hashed_password):
            raise AppException("sign_up.user_not_found")

        user = await self._account_service.verify_worker(WorkerVerify(**data.dict()))
        token_pair = AuthToken.generate_pair(user.dict())
        return AuthResponse(user=user, **token_pair)

    @staticmethod
    async def refresh_token(data: RefreshTokenSchema) -> AccessTokenSchema:
        data = AuthToken.decrypt_token(data.refresh_token)
        return AccessTokenSchema(access_token=AuthToken.generate_access_token(data))
