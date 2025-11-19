from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Annotated, Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role_id: int  # 👈 добавлено, потому что в модели User он обязателен


class UserRead(UserBase):
    user_id: int
    role_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


# !!!!!!!!!!!!!!!!!!!!!! ДЛЯ ПРИМЕРА !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class UserSchema(BaseModel):
    # Указываем, что указанные типы должны быть строго сюда переданы
    model_config = ConfigDict(strict=True)

    username: Annotated[str, MinLen(1), MaxLen(20)]
    password: bytes
    email: EmailStr | None = None
    active: bool = True
