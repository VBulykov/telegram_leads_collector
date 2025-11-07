from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.users_models import User
from src.users.users_schemas import UserCreate, UserUpdate


async def get_user(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[User]:
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user_data: UserCreate, hashed_password: str) -> User:
    """Создание нового пользователя"""
    new_user = User(
        username=user_data.username,
        password=hashed_password,
        email=user_data.email,
        phone_number=user_data.phone_number,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(
    db: AsyncSession,
    user: User,
    user_data: UserUpdate,
    hashed_password: str | None = None
) -> User:
    """Обновление пользователя"""
    update_data = user_data.model_dump(exclude_unset=True)
    
    if hashed_password:
        update_data["password"] = hashed_password
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: UUID) -> None:
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()


async def deactivate_user(db: AsyncSession, user: User) -> User:
    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(user)
    return user


async def activate_user(db: AsyncSession, user: User) -> User:
    user.is_active = True
    user.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(user)
    return user
