from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.users_crud import (
    create_user, update_user, delete_user,
    activate_user, deactivate_user,
    get_user, get_user_by_email, get_user_by_username,
    get_users,
)
from src.users.users_models import User
from src.users.users_schemas import UserCreate, UserUpdate
from src.users.services.password_service import hash_password


async def create_user_service(
    db: AsyncSession,
    user_data: UserCreate
) -> User:
    if await get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует"
        )
    
    if await get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    hashed_password = hash_password(user_data.password)
    
    return await create_user(db, user_data, hashed_password)


async def update_user_service(
    db: AsyncSession,
    user_id: UUID,
    user_data: UserUpdate
) -> User:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    hashed_password = None
    if user_data.password:
        hashed_password = hash_password(user_data.password)
    
    if user_data.username and user_data.username != user.username:
        if await get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким username уже существует"
            )
    
    if user_data.email and user_data.email != user.email:
        if await get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
    
    return await update_user(db, user, user_data, hashed_password)


async def get_user_service(db: AsyncSession, user_id: UUID) -> User:
    """Сервис для получения пользователя"""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


async def list_users_service(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[User]:
    """Сервис для получения списка всех пользователей"""
    return await get_users(db, skip, limit)


async def delete_user_service(db: AsyncSession, user_id: UUID) -> None:
    """Сервис для удаления пользователя"""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    await delete_user(db, user_id)


async def deactivate_user_service(db: AsyncSession, user_id: UUID) -> User:
    """Сервис для деактивации пользователя"""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже деактивирован"
        )
    
    return await deactivate_user(db, user)


async def activate_user_service(db: AsyncSession, user_id: UUID) -> User:
    """Сервис для активации пользователя"""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже активирован"
        )
    
    return await activate_user(db, user)
