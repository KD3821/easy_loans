from pydantic import BaseModel, EmailStr, ConfigDict


class FullUser(BaseModel):
    id: int
    email: EmailStr
    username: str
    hashed_password: str

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)
