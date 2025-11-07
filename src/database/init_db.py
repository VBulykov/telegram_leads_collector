from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import get_settings
from src.database.migration_runner import apply_migrations


async def _ensure_database_exists():
    settings = get_settings()
    
    admin_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
    )
    
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    
    try:
        async with admin_engine.begin() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": settings.POSTGRES_DB}
            )
            exists = result.scalar() is not None
            
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{settings.POSTGRES_DB}"'))
    finally:
        await admin_engine.dispose()


async def init_db():
    await _ensure_database_exists()
    await apply_migrations()
