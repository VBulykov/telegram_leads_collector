#!/usr/bin/env python3
"""
Скрипт для генерации RSA ключей для JWT токенов
Работает на Windows, Linux и macOS
"""
import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_jwt_keys():
    """Генерирует пару RSA ключей для JWT"""
    # Определяем путь к директории с ключами
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    auth_dir = project_root / "src" / "auth" / "certs"
    private_key_path = auth_dir / "jwt-private.pem"
    public_key_path = auth_dir / "jwt-public.pem"
    
    # Создаём директорию, если её нет
    auth_dir.mkdir(parents=True, exist_ok=True)
    
    # Проверяем, существуют ли уже ключи
    if private_key_path.exists() or public_key_path.exists():
        response = input(
            f"Ключи уже существуют в {auth_dir}.\n"
            "Перезаписать? (y/n): "
        )
        if response.lower() != 'y':
            print("Отменено.")
            return
    
    # Генерируем приватный ключ RSA 2048 бит
    print("Генерация RSA ключей...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Сохраняем приватный ключ в формате PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open(private_key_path, "wb") as f:
        f.write(private_pem)
    
    # Генерируем публичный ключ из приватного
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open(public_key_path, "wb") as f:
        f.write(public_pem)
    
    # Устанавливаем права доступа (только для Unix-систем)
    if os.name != 'nt':  # не Windows
        os.chmod(private_key_path, 0o600)
        os.chmod(public_key_path, 0o644)
    
    print("✅ JWT ключи успешно созданы:")
    print(f"  Приватный ключ: {private_key_path}")
    print(f"  Публичный ключ: {public_key_path}")


if __name__ == "__main__":
    generate_jwt_keys()

