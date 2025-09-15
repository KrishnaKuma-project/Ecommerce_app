from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
import os
import time

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
sessionlocal = sessionmaker(autocommit =False, autoflush= False, bind = engine)
Base = declarative_base()


def get_db ():
    db = sessionlocal()
    try :
        yield db
    finally :
        db.close()