from datetime import datetime

from ..models import SignInRecord

from apps.users.schemas import FullUser
from db import async_session


class SignInStorage:
    _table = SignInRecord

    @classmethod
    async def create(cls, user: FullUser) -> None:
        async with async_session() as session:
            sign_in_record = cls._table(user_email=user.email, signed_in_at=datetime.now())
            session.add(sign_in_record)
            await session.commit()
