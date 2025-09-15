from .database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime


class cart_list(Base):
    __tablename__="cart_list"

    id = Column(Integer,primary_key=True, index=True)
    email = Column(String,index=True)
    product_id = Column(Integer,index=True)
    product_name = Column (String, index=True)
    product_price = Column (String)
    product_count = Column(Integer,default=1)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)