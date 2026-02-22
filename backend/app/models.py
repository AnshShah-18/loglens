from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    patterns: Mapped[list["Pattern"]] = relationship(
        "Pattern",
        back_populates="upload",
        cascade="all, delete-orphan",
    )


class Pattern(Base):
    __tablename__ = "patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), nullable=False, index=True)
    pattern_text: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    sample_line: Mapped[str] = mapped_column(Text, nullable=False)

    upload: Mapped[Upload] = relationship("Upload", back_populates="patterns")
