from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from . import database

class notification_table(database.Base):
    __tablename__ = "notification_table"

    id = Column(Integer,primary_key=True, index=True)
    email = Column(String,unique=True, index=True)
    otp_number = Column(Integer)
    otp_expiry_time = Column(DateTime)
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)