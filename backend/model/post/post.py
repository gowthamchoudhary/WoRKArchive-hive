from db.session import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from datetime import datetime


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    work_summary_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("work_summaries.id"),
        nullable=False
    )

    platform: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )