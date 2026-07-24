from sqlalchemy import Integer,String,Column
from pydantic import BaseModel
from datetime import datetime,func
from db.session import Base
class User(Base):
    __tablename__ = "users"
    id=Column(Integer,unique=True,index=True,primary_key=True)
    username=Column(Integer,unique=True,nullable=False)
    email=Column(String,unique=True,nullable=False)
    password_hash=Column(String,nullable=False)
    created_at=Column(datetime,server_default=func.utc)
    
