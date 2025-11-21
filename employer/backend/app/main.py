from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from pathlib import Path
from shared.db import Base
from shared.db.session import db_helper
import sys

from .api.routers import router as router_v1
from .core.config import settings

BASE_PATH = "employer.backend.app"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключение к БД при старте
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("База данных успешно инициализирована")

    yield # Тут жизненный цикл приложения

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
app = FastAPI(lifespan=lifespan)

# Настройка CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Альтернативный адрес Vite
        "http://localhost:3000",  # React dev server (если будет)
        "http://127.0.0.1:3000",  # Альтернативный адрес React
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(router=router_v1, prefix=settings.api_v1_prefix)

@app.get("/")
def hello():
    return {
        "message": "hello"
    }

# @app.get("/reg")
# def registration():
#     return {
#         "message": "registration"
#     }

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
