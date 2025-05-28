from src.database.base import Base
from src.database.engine import engine
# from src.models


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # только на dev
        await conn.run_sync(Base.metadata.create_all)
