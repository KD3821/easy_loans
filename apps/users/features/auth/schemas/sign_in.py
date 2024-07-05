from pydantic import BaseModel, EmailStr


class SignIn(BaseModel):
    email: EmailStr
    password: str
