from sqlalchemy import Column, String, Integer, DateTime
from .database import Base
from datetime import datetime

class user_details (Base):
    __tablename__ = "user_details"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    username = Column(String,unique=True,index=True)
    password = Column(String)
    email = Column(String,unique=True,index=True)
    mobile = Column(String,unique=True,index=True)
    user_type = Column(String, nullable=False)
    otp = Column(String,nullable=False, default="user")
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)