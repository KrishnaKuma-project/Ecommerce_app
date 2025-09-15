from sqlalchemy import Column,Integer,String,DateTime
from .database import Base
from datetime import datetime

class product_table (Base):
    __tablename__ ="product_table"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, unique=True,index=True,nullable=False)
    product_description = Column(String,nullable=False)
    product_categorie = Column(String,nullable=False)
    product_price = Column(String)
    product_image = Column(String,default="False")
    product_stock_status = Column(String, default="in stock")
    product_sku = Column (String,nullable=True)
    product_specifications = Column(String,nullable=True)
    product_created_at = Column(DateTime,default=datetime.utcnow)
    product_updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)