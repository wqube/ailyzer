# schemas/auth.py
"""Схемы для аутентификации и авторизации"""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Схема для регистрации нового пользователя"""
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    """Пара токенов: access и refresh"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Схема для обновления access токена"""
    refresh_token: str


class TokenPayload(BaseModel):
    """Полезная нагрузка из JWT токена"""
    sub: int  # user_id
    email: str
    role_id: int
    exp: int
    iat: int