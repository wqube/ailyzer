from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from pathlib import Path
from shared.db import Base
from shared.db.session import db_helper
import sys

from .api.routers import router as router_v1
from shared.core.config import settings

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


# --- ДИНАМИЧЕСКАЯ НАСТРОЙКА CORS ---
allowed_origins = [
    "http://localhost:5173",    # Dev server employer
    "http://127.0.0.0:5173",
    "http://localhost:3000",    # Dev server candidate
    "http://127.0.0.1:3000",
]

# Добавляем продакшн URL из общего конфига
if settings.employer_frontend_url:
    allowed_origins.append(settings.employer_frontend_url)
if settings.candidate_frontend_url:
    allowed_origins.append(settings.candidate_frontend_url)


# Настройка CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
