import string
import random

from sqlalchemy.future import select

from db import async_session
from ..schemas import WorkerCreate, WorkerVerify, WorkerAccessCode
from apps.users.schemas import User
from apps.users.storages.users_storage import get_random_string, hash_password
from apps.users.models.user import User as UserModel


class AccountService:
    _table = UserModel

    @staticmethod
    def get_access_code(length=8, chars=string.ascii_uppercase + string.digits):
        access_code = "".join(random.choice(chars) for _ in range(length))
        return access_code

    @staticmethod
    def validate_access_code(access_code: str, hashed_access_code: str):  # may be done different way
        salt, hashed = hashed_access_code.split("$")
        return hash_password(access_code, salt) == hashed

    @classmethod
    async def create_worker(cls, user: WorkerCreate) -> WorkerAccessCode:
        access_code = cls.get_access_code()
        salt = get_random_string()
        hashed_access_code = hash_password(access_code, salt)  # may be done different way

        async with async_session() as session:
            user = cls._table(
                email=user.email,
                username=user.username,
                hashed_password=f"{salt}${hashed_access_code}",
                role=UserModel.WORKER,
                is_verified=False  # todo change to False in production
            )
            session.add(user)
            await session.commit()

        user = user and User.model_validate(user)
        return WorkerAccessCode(email=user.email, access_code=access_code)

    @classmethod
    async def reset_worker_access_code(cls, user: WorkerCreate) -> WorkerAccessCode:
        access_code = cls.get_access_code()
        salt = get_random_string()
        hashed_access_code = hash_password(access_code, salt)

        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.email == user.email and user.email.lower())
            )
            user = query.scalars().first()
            user.hashed_password = hashed_access_code
            await session.commit()

        return WorkerAccessCode(email=user.email, access_code=access_code)

    @classmethod
    async def verify_worker(cls, verified_user: WorkerVerify):
        salt = get_random_string()
        hashed_password = hash_password(verified_user.password, salt)

        async with async_session() as session:
            query = await session.execute(
                select(cls._table).filter(cls._table.email == verified_user.email and verified_user.email.lower())
            )
            user = query.scalars().first()
            user.username = verified_user.username
            user.hashed_password = f"{salt}${hashed_password}"
            user.is_verified = True
            await session.commit()

        user = user and User.model_validate(user)
        return user
