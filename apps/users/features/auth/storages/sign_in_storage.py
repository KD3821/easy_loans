from datetime import datetime

from db import async_session

from apps.users.schemas import TokenUser

from ..models import SignInRecord


class SignInStorage:
    _table = SignInRecord

    @classmethod
    async def create(cls, user: TokenUser) -> None:
        async with async_session() as session:
            sign_in_record = cls._table(
                user_email=user.email, signed_in_at=datetime.now()
            )
            session.add(sign_in_record)
            await session.commit()
