from pydantic import BaseModel, ConfigDict, EmailStr


class FullUser(BaseModel):
    id: int
    email: EmailStr
    username: str
    hashed_password: str
    role: str
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class TokenUser(BaseModel):
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)
