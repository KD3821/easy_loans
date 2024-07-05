from pydantic import BaseModel, EmailStr


class ManagerSignUp(BaseModel):
    email: EmailStr
    username: str
    password: str


class WorkerSignUp(ManagerSignUp):
    access_code: str
