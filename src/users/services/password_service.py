import bcrypt


BCRYPT_ROUNDS = 12


def hash_password(password: str, rounds: int = BCRYPT_ROUNDS) -> str:
    if not password:
        raise ValueError("Пароль не может быть пустым")
    
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except (ValueError, TypeError):
        return False
