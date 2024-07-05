from pydantic import BaseModel, EmailStr


class WorkerVerify(BaseModel):
    email: EmailStr
    username: str
    password: str
    access_code: str
