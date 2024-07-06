from pydantic import BaseModel, EmailStr


class WorkerAccessCode(BaseModel):
    email: EmailStr
    access_code: str


class WorkerAccessCodeReset(BaseModel):
    email: EmailStr
