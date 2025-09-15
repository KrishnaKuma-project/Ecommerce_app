from .database import Base
from sqlalchemy import Column,String,Integer,DateTime, JSON
from datetime import datetime, timedelta

class order_details(Base):
    __tablename__ = "order_details"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,index=True)
    items = Column(JSON)
    address = Column(String)
    payment_options = Column(String,index=True)
    price = Column (Integer)
    discount_price = Column (Integer)
    discount_type = Column (String)
    delivery_date = Column(DateTime,default=lambda: datetime.utcnow() + timedelta(days=2))
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    