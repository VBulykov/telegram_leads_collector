from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_models import RefreshToken


async def create_refresh_token_record(
    db: AsyncSession,
    user_id: UUID,
    token: str,
    expires_at: datetime
) -> RefreshToken:
    """Создаёт запись refresh токена в БД"""
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return refresh_token


async def get_refresh_token_by_token(
    db: AsyncSession,
    token: str
) -> RefreshToken | None:
    """Получает refresh токен по значению токена"""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token)
    )
    return result.scalar_one_or_none()


async def revoke_refresh_token(
    db: AsyncSession,
    token: RefreshToken
) -> RefreshToken:
    """Отзывает refresh токен"""
    token.is_revoked = True
    token.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(token)
    return token


async def revoke_all_user_tokens(
    db: AsyncSession,
    user_id: UUID
) -> None:
    """Отзывает все refresh токены пользователя"""
    await db.execute(
        delete(RefreshToken).where(RefreshToken.user_id == user_id)
    )
    await db.commit()

