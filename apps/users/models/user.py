from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from db import Base


class User(Base):
    __tablename__ = 'users'
    MANAGER = 'manager'
    WORKER = 'worker'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    username = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    activated_at = Column(DateTime(timezone=True), onupdate=func.now())
    role = Column(String, default=WORKER)
    is_verified = Column(Boolean, default=False)
    sign_in_records = relationship('SignInRecord')
