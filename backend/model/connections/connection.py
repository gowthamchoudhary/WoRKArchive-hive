from sqlalchemy import Integer,String,Column,ForeignKey,func,DateTime
from sqlalchemy.orm import relationships,mapped_column,Mapped

from datetime import datetime
from db.session import Base

class Connection(Base):
    __tablename__ = "connections"
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id:Mapped[int]=mapped_column(
        ForeignKey("users.id"),nullable=False)
    provider:Mapped[str]=mapped_column(String(50))
    provider_user_id:Mapped[str]=mapped_column(String)
    username:Mapped[str]=mapped_column(String)
    email:Mapped[str] = mapped_column(String,nullable=True)
    avatar_url:Mapped[str | None] = mapped_column(String)
    profile_url:Mapped[str | None] = mapped_column(String)
    access_token:Mapped[str] = mapped_column(String)
    refresh_token:Mapped[str|None] = mapped_column(nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),nullable=True)
    connected_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now())
    
    




