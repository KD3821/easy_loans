from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func

from db import Base


class SignInRecord(Base):
    __tablename__ = 'sign_in_records'

    id = Column(Integer, primary_key=True)
    user_email = Column(String, ForeignKey('users.email'))
    user = relationship('User', back_populates="sign_in_records")
    signed_in_at = Column(DateTime, server_default=func.now())
