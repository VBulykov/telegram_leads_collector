from src.database.migration_runner import apply_migrations


async def init_db():
    await apply_migrations()
