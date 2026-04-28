from sqlalchemy import Boolean, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.backend.database import Base


class ReviewRecord(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, default="user_submitted")
    asin: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="skincare")
    review_text: Mapped[str] = mapped_column(Text, nullable=False)
    skin_type: Mapped[str] = mapped_column(String(50), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    is_ad: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
