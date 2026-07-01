import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .model_auth import User


class Base(DeclarativeBase):
    pass


class URL(Base):
    __tablename__ = "url"
    uid: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True), primary_key=True, default=uuid.UUID
    )
    url: Mapped[str] = mapped_column(String)
    user_uid: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), pg.ForeignKey("user.uid"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="url", lazy="selectin", foreign_keys=[user_uid])
