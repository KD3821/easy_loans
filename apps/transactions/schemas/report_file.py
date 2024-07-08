from pydantic import BaseModel


class ReportUploaded(BaseModel):
    filename: str
