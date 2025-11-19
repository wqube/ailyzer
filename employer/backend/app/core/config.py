from os import getenv
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from shared.core.config import settings as shared_settings

BASE_DIR = Path(__file__).parent.parent


class DbSettings(BaseModel):
    url: str = "postgresql+asyncpg://postgres:1@localhost:5432/ailyzer_db"
    # !!!!!!!!!!!!!! ВАЖНО !!!!!!! echo=True только для разработки, когда будем выпускать в прод надо обязательно менять на False !!!!!!!!!!!!!!
    db_echo: bool = True


class AuthJWT(BaseModel):
    # private_key_path: str = "/app/certs/jwt-private.pem"
    # public_key_path: str = "/app/certs/jwt-public.pem"
    # private_key_path: Path = Path("/app/certs/jwt-private.pem")
    # public_key_path: Path = Path("/app/certs/jwt-public.pem")
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30 * 60 * 24 # пока что 30 минут



class Settings(BaseSettings):
    # Подключение общих настроек (базы данных)
    shared: object = shared_settings
    api_v1_prefix: str = "/api/v1"
    # db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    

settings = Settings()
