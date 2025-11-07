#!/bin/bash
set -e

AUTH_DIR="src/auth/certs"
PRIVATE_KEY="$AUTH_DIR/jwt-private.pem"
PUBLIC_KEY="$AUTH_DIR/jwt-public.pem"

# Создаём директорию, если её нет
mkdir -p "$AUTH_DIR"

# Генерируем приватный ключ RSA 2048 бит
openssl genpkey -algorithm RSA -out "$PRIVATE_KEY" -pkcs8 -pkeyopt rsa_keygen_bits:2048

# Генерируем публичный ключ из приватного
openssl rsa -pubout -in "$PRIVATE_KEY" -out "$PUBLIC_KEY"

# Устанавливаем права доступа (только для чтения владельцем)
chmod 600 "$PRIVATE_KEY"
chmod 644 "$PUBLIC_KEY"

echo "JWT ключи успешно созданы:"
echo "  Приватный ключ: $PRIVATE_KEY"
echo "  Публичный ключ: $PUBLIC_KEY"

