from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.submission import Submission


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    security_score: Mapped[int] = mapped_column(Integer, nullable=False)
    performance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    maintainability_score: Mapped[int] = mapped_column(Integer, nullable=False)
    readability_score: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    submission: Mapped["Submission"] = relationship(back_populates="review")
    comments: Mapped[list["ReviewComment"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )


class ReviewComment(Base):
    __tablename__ = "review_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    review: Mapped["Review"] = relationship(back_populates="comments")
