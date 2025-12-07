from os import getenv
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class DbSettings(BaseModel):
    url: str = "postgresql+asyncpg://postgres:1@localhost:5432/ailyzer_db"
    # !!!!!!!!!!!!!! ВАЖНО !!!!!!! echo=True только для разработки, когда будем выпускать в прод надо обязательно менять на False !!!!!!!!!!!!!!
    db_echo: bool = True


class MinioSettings(BaseModel):
    endpoint: str = "localhost:9000"
    access_key: str = "ailyzeradmin"
    secret_key: str = "ailyzeradmin123"
    secure: bool = False
    resumes_bucket: str = "resumes"


class Settings(BaseSettings):
     # НАСТРОЙКИ ЧТЕНИЯ .ENV
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # для вложенных моделей db/minio
    )

    # api_v1_prefix: str = "/api/v1"
    db: DbSettings = DbSettings()
    minio: MinioSettings = MinioSettings()


settings = Settings()
