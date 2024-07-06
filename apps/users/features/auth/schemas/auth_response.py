from pydantic import BaseModel

from apps.users.schemas import TokenUser


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: TokenUser
