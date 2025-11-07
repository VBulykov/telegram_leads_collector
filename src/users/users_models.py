from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)  # Хэшированный пароль
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="NOW()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default="NOW()")
