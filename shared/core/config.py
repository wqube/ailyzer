from os import getenv
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]


class DbSettings(BaseModel):
    url: str = "postgresql+asyncpg://postgres:1@localhost:5432/ailyzer_db"
    # !!!!!!!!!!!!!! ВАЖНО !!!!!!! echo=True только для разработки, когда будем выпускать в прод надо обязательно менять на False !!!!!!!!!!!!!!
    db_echo: bool = True



class Settings(BaseSettings):
    # api_v1_prefix: str = "/api/v1"
    db: DbSettings = DbSettings()
    

settings = Settings()
