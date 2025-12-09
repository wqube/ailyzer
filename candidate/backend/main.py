from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path
import uvicorn
import sys, os

from .routes import interview
from .routes import resume
from .routes import candidate_routes
from .routes import vacancy_routes

from shared.core.config import settings


app = FastAPI(title="AIlyzer API")
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

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


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Подключаем routers
app.include_router(resume.router)
# app.include_router(interview.router)
app.include_router(interview.router)
app.include_router(candidate_routes.router)
app.include_router(vacancy_routes.router)

print("PYTHONPATH:", sys.path)
print("CHECK SHARED:", Path(str(BASE_DIR) + "/shared").exists())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)