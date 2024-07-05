from pydantic import BaseModel
from apps.users.schemas import User


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: User
