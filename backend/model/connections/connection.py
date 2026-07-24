from sqlalchemy import Integer,String,Column,ForeignKey
from sqlalchemy.orm import relationships,mapped_column,Mapped

from datetime import datetime,func
from db.session import Base

class Connection(Base):
    __tablename__ = "connections"
    id:Mapped[int] = mapped_column(index=True)
    userid:Mapped[int]=mapped_column(
        ForeignKey("users.id"),nullable=True)
    provider:Mapped[str]=mapped_column(String(50))
    access_token:Mapped[str] = mapped_column()
    refresh_token:Mapped[str|None] = mapped_column(nullable=True)
    expires_at:Mapped[datetime] = mapped_column()




