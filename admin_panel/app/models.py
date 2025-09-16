from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from .database import Base

class admin_activity(Base):
    __tablename__="admin_activity"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True, index=True)
    last_activity = Column(String,nullable=True, index=True)
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow, onupdate=datetime.utcnow)

class user_block_unblock_details (Base):
    __tablename__="user_block_unblock_details"

    id = Column(Integer, primary_key=True, index= True)
    email = Column (String, index=True)
    blocked_user_email = Column(String,index=True,nullable=True)
    unblocked_user_email = Column(String, index=True, nullable=True)
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,onupdate=datetime.utcnow)