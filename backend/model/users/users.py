from sqlalchemy import Integer,String,Column,func
from sqlalchemy.orm import mapped_column,Mapped
from datetime import datetime
from db.session import Base
class User(Base):
    __tablename__ = "users"
    id:Mapped[int]=mapped_column(unique=True,index=True,primary_key=True)
    username:Mapped[str]=mapped_column(unique=True,nullable=False)
    email:Mapped[str]=mapped_column(unique=True,nullable=False)
    password_hash:Mapped[str]=mapped_column(nullable=False)
    created_at:Mapped[datetime]=mapped_column(server_default=func.now())
    
