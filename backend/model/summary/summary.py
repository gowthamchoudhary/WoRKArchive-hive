from sqlalchemy import Integer,String,Column,ForeignKey,func,DateTime,JSON,Text
from sqlalchemy.orm import relationships,mapped_column,Mapped

from datetime import datetime
from db.session import Base

class WorkSummary(Base):
    __tablename__ = "work_summaries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    summary: Mapped[str] = mapped_column(Text, nullable=False)

    projects: Mapped[dict] = mapped_column(JSON, nullable=True)
    technologies: Mapped[dict] = mapped_column(JSON, nullable=True)
    activities: Mapped[dict] = mapped_column(JSON, nullable=True)
    accomplishments: Mapped[dict] = mapped_column(JSON, nullable=True)
    problems_solved: Mapped[dict] = mapped_column(JSON, nullable=True)

    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )