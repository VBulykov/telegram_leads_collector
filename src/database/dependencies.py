from sqlalchemy.ext.asyncio import AsyncSession

from src.database.engine import async_session


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

