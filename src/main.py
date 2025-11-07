from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.database.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
