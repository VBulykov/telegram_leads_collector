from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from src.config import get_settings


settings = get_settings()


def _load_private_key() -> rsa.RSAPrivateKey:
    """Загружает приватный ключ для подписи токенов"""
    key_path = Path(settings.Auth_JWT.private_key_path)
    if not key_path.exists():
        raise FileNotFoundError(
            f"Приватный ключ не найден: {key_path}. "
            "Создайте пару ключей RSA для JWT. Запустите: bash scripts/generate_jwt_keys.sh"
        )
    
    with open(key_path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )


def _load_public_key() -> rsa.RSAPublicKey:
    """Загружает публичный ключ для проверки токенов"""
    key_path = Path(settings.Auth_JWT.public_key_path)
    if not key_path.exists():
        raise FileNotFoundError(
            f"Публичный ключ не найден: {key_path}. "
            "Создайте пару ключей RSA для JWT. Запустите: bash scripts/generate_jwt_keys.sh"
        )
    
    with open(key_path, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())


def create_access_token(user_id: UUID, username: str) -> str:
    """Создаёт access токен для пользователя"""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=settings.Auth_JWT.access_token_expires_minutes)
    
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    
    private_key = _load_private_key()
    token = jwt.encode(
        payload,
        private_key,
        algorithm=settings.Auth_JWT.algorithm
    )
    
    return token


def create_refresh_token(user_id: UUID, username: str) -> str:
    """Создаёт refresh токен для пользователя"""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=settings.Auth_JWT.refresh_token_expires_days)
    
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    
    private_key = _load_private_key()
    token = jwt.encode(
        payload,
        private_key,
        algorithm=settings.Auth_JWT.algorithm
    )
    
    return token


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """
    Проверяет токен и возвращает payload
    
    Args:
        token: JWT токен
        token_type: Тип токена ("access" или "refresh")
    
    Raises:
        jwt.ExpiredSignatureError: Токен истёк
        jwt.InvalidTokenError: Токен невалиден
    """
    public_key = _load_public_key()
    
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[settings.Auth_JWT.algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Токен истёк")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Невалидный токен: {e}")
    
    if payload.get("type") != token_type:
        raise jwt.InvalidTokenError(f"Неверный тип токена. Ожидается: {token_type}")
    
    return payload


def get_user_id_from_token(token: str, token_type: str = "access") -> UUID:
    """Извлекает user_id из токена"""
    payload = verify_token(token, token_type)
    return UUID(payload["sub"])

