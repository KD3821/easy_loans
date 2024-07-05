from pydantic import BaseModel, EmailStr


class ManagerCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
