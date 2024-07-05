import hashlib
import random
import string

from passlib.context import CryptContext
from sqlalchemy.future import select

from ..schemas import User, FullUser, ManagerCreate
from ..models.user import User as UserModel

from db import async_session


def get_random_string(length=12):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()


def validate_password(password: str, hashed_password: str):
    salt, hashed = hashed_password.split("$")
    return hash_password(password, salt) == hashed


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersStorage:
    _table = UserModel
    """
    This class is responsible for CRUDL operations for User entity
    and responsible only for CRUDL with minimal validations and mostly
    with queries to DB
    """
    @classmethod
    async def create_manager(cls, user: ManagerCreate) -> User:
        salt = get_random_string()
        hashed_password = hash_password(user.password, salt)

        async with async_session() as session:
            user = cls._table(
                email=user.email,
                username=user.username,
                hashed_password=f"{salt}${hashed_password}",
                role=UserModel.MANAGER,
                is_verified=True  # todo change to False in production (will need verification by owner)
            )
            session.add(user)
            await session.commit()

        user = user and User.model_validate(user)
        return user

    @classmethod
    async def get_user_by_identity(cls, email: str) -> FullUser:
        async with async_session() as session:
            query = await session.execute(select(cls._table).filter(cls._table.email == email and email.lower()))
            user = query.scalars().first()
        result = user and FullUser.model_validate(user)
        return result
