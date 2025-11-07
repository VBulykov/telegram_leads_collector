from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database.init_db import init_db
from src.users.users_routes import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Telegram Leads Collector",
    description="Парсер лидов из Telegram-чатов и каналов",
    lifespan=lifespan
)

app.include_router(users_router)
