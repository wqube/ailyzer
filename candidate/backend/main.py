from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from pathlib import Path
import uvicorn
import sys, os

from .routes import interview
from .routes import resume
from .routes import candidates


app = FastAPI(title="AIlyzer API")
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))
                
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем routers
app.include_router(resume.router)
# app.include_router(interview.router)
app.include_router(interview.router)
app.include_router(candidates.router)

print("PYTHONPATH:", sys.path)
print("CHECK SHARED:", Path(str(BASE_DIR) + "/shared").exists())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)