from datetime import datetime

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)  # Хэшированный пароль
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default="NOW()")
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False, server_default="NOW()")

