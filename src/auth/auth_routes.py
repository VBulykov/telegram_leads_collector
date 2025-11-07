from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_crud import (
    create_refresh_token_record,
    get_refresh_token_by_token,
    revoke_refresh_token,
)
from src.auth.auth_dependencies import get_current_user
from src.auth.auth_jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from src.auth.auth_schemas import LoginRequest, RefreshTokenRequest, TokenResponse
from src.config import get_settings
from src.database.dependencies import get_db
from src.users.services.password_service import verify_password
from src.users.users_models import User
from src.users.users_schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Авторизация пользователя по username/email и паролю"""
    # Ищем пользователя по username или email
    result = await db.execute(
        select(User).where(
            (User.username == login_data.username) | (User.email == login_data.username)
        )
    )
    user = result.scalar_one_or_none()
    
    if user is None or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный username/email или password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    
    # Создаём access и refresh токены
    access_token = create_access_token(user.id, user.username)
    refresh_token_str = create_refresh_token(user.id, user.username)
    
    # Сохраняем refresh токен в БД
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.Auth_JWT.refresh_token_expires_days
    )
    await create_refresh_token_record(db, user.id, refresh_token_str, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление access токена с помощью refresh токена"""
    # Проверяем refresh токен
    try:
        payload = verify_token(refresh_data.refresh_token, token_type="refresh")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Невалидный refresh токен: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, что токен существует в БД и не отозван
    refresh_token_record = await get_refresh_token_by_token(db, refresh_data.refresh_token)
    
    if refresh_token_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if refresh_token_record.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен отозван",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, что токен не истёк (по дате в БД)
    if refresh_token_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен истёк",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Получаем пользователя
    user_id = UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден или деактивирован"
        )
    
    # Создаём новые токены
    access_token = create_access_token(user.id, user.username)
    new_refresh_token_str = create_refresh_token(user.id, user.username)
    
    # Отзываем старый refresh токен
    await revoke_refresh_token(db, refresh_token_record)
    
    # Сохраняем новый refresh токен
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.Auth_JWT.refresh_token_expires_days
    )
    await create_refresh_token_record(db, user.id, new_refresh_token_str, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token_str
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user

