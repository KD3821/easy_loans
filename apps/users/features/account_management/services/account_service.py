import random
import string

from core import AppException
from db import async_session
from sqlalchemy.future import select

from apps.users.models.user import User as UserModel
from apps.users.schemas import TokenUser
from apps.users.storages.users_storage import get_random_string, hash_password

from ..schemas import (WorkerAccessCode, WorkerAccessCodeReset, WorkerCreate,
                       WorkerVerify)


class AccountService:
    _table = UserModel

    @staticmethod
    def get_access_code(length=8, chars=string.ascii_uppercase + string.digits):
        access_code = "".join(random.choice(chars) for _ in range(length))
        return access_code

    @staticmethod
    def validate_access_code(
        access_code: str, hashed_access_code: str
    ):  # may be done different way
        salt, hashed = hashed_access_code.split("$")
        return hash_password(access_code, salt) == hashed

    @classmethod
    async def check_user_exists(cls, email):
        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(
                    cls._table.email == email and email.lower()
                )
            )
            user = query.scalars().first()

        return user

    @classmethod
    async def create_worker(cls, user: WorkerCreate) -> WorkerAccessCode:
        if cls.check_user_exists(user.email) is not None:
            raise AppException("create_worker.user_already_exists")

        access_code = cls.get_access_code()
        salt = get_random_string()
        hashed_access_code = hash_password(
            access_code, salt
        )  # may be done different way

        async with async_session() as session:
            user = cls._table(
                email=user.email,
                username=user.username,
                hashed_password=f"{salt}${hashed_access_code}",
                role=UserModel.WORKER,
                is_verified=False,
            )
            session.add(user)
            await session.commit()

        user = user and TokenUser.model_validate(user)
        return WorkerAccessCode(email=user.email, access_code=access_code)

    @classmethod
    async def reset_worker_access_code(
        cls, worker: WorkerAccessCodeReset
    ) -> WorkerAccessCode:
        user = await cls.check_user_exists(worker.email)

        if user is None:
            raise AppException("reset_access_code.user_not_found")

        if user.is_verified:
            raise AppException("reset_access_code.user_is_verified")

        access_code = cls.get_access_code()
        salt = get_random_string()
        hashed_access_code = hash_password(access_code, salt)

        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(
                    cls._table.email == worker.email and worker.email.lower()
                )
            )
            user = query.scalars().first()
            user.hashed_password = f"{salt}${hashed_access_code}"
            await session.commit()

        return WorkerAccessCode(email=worker.email, access_code=access_code)

    @classmethod
    async def verify_worker(cls, verified_user: WorkerVerify) -> TokenUser:
        salt = get_random_string()
        hashed_password = hash_password(verified_user.password, salt)

        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(
                    cls._table.email == verified_user.email
                    and verified_user.email.lower()
                )
            )
            user = query.scalars().first()
            user.username = verified_user.username
            user.hashed_password = f"{salt}${hashed_password}"
            user.is_verified = True
            await session.commit()

        user = user and TokenUser.model_validate(user)
        return user
