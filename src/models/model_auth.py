import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base

if TYPE_CHECKING:
    from .model_url import URL


class User(Base):
    __tablename__ = "user"
    uid: Mapped[uuid.UUID] = mapped_column(
        pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True)
    full_name: Mapped[str] = mapped_column(String(30))
    password_hashed: Mapped[str] = mapped_column(String)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    urls: Mapped[list["URL"]] = relationship(
        "URL", back_populates="user", lazy="selectin"
    )
