from pydantic import BaseModel, EmailStr


class WorkerCreate(BaseModel):
    email: EmailStr
    username: str
