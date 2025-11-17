from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from db import Base
from db.session import db_helper

from api.routers import router as router_v1
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключение к БД при старте
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("База данных успешно инициализирована")

    yield # Тут жизненный цикл приложения

app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api_v1_prefix)

@app.get("/")
def hello():
    return {
        "message": "hello"
    }

@app.get("/reg")
def registration():
    return {
        "message": "registration"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
