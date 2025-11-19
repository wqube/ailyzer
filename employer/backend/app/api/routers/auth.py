# api/routers/auth.py
"""Роутер для аутентификации: регистрация, вход, обновление токенов, выход"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from jwt.exceptions import InvalidTokenError

from db_old.models.models import User, Role, Token
from db_old.session import db_helper
from schemas.auth import UserRegister, UserLogin, TokenPair, TokenRefresh
from auth.utils import hash_password, validate_password, encode_jwt, decode_jwt
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============ РЕГИСТРАЦИЯ ============

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Регистрация нового пользователя (работодателя).
    
    - Проверяет уникальность email
    - Хеширует пароль
    - Присваивает роль 'employer' (role_id=2)
    - Создаёт пользователя в БД
    """
    
    # 1. Проверяем, что email уникален
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Проверяем, что роль 'employer' существует (role_id=2)
    # Если у вас другая логика назначения ролей - адаптируйте
    employer_role = await session.get(Role, 2)
    if not employer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Employer role not found in database"
        )
    
    # 3. Хешируем пароль
    password_hash = hash_password(user_data.password)
    
    # 4. Создаём пользователя
    new_user = User(
        email=user_data.email,
        password_hash=password_hash.decode('utf-8'),  # bcrypt возвращает bytes
        role_id=2,  # employer
        status="active"
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return {
        "message": "User registered successfully",
        "user_id": new_user.user_id,
        "email": new_user.email
    }


# ============ ВХОД (LOGIN) ============

@router.post("/login", response_model=TokenPair)
async def login_user(
    credentials: UserLogin,
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Вход пользователя.
    
    - Проверяет email и пароль
    - Генерирует access и refresh токены
    - Сохраняет refresh токен в БД
    - Возвращает пару токенов
    """
    
    # 1. Находим пользователя по email
    result = await session.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # 2. Проверяем пароль
    if not validate_password(credentials.password, user.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # 3. Проверяем статус пользователя
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is blocked"
        )
    
    # 4. Создаём access токен (короткий срок жизни)
    access_token_payload = {
        "sub": str(user.user_id),  # 👈 КОНВЕРТИРУЕМ В СТРОКУ!
        "email": user.email,
        "role_id": user.role_id,
    }
    
    access_token = encode_jwt(
        payload=access_token_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )
    
    # 5. Создаём refresh токен (долгий срок жизни)
    refresh_token_payload = {
        "sub": str(user.user_id),  # 👈 КОНВЕРТИРУЕМ В СТРОКУ!
        "email": user.email,
    }
    
    refresh_token = encode_jwt(
        payload=refresh_token_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )
    
    # 6. Сохраняем refresh токен в БД
    expires_at = datetime.utcnow() + timedelta(days=settings.auth_jwt.refresh_token_expire_days)
    
    new_token = Token(
        user_id=user.user_id,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )
    
    session.add(new_token)
    await session.commit()
    
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# ============ ОБНОВЛЕНИЕ ACCESS ТОКЕНА ============

@router.post("/refresh", response_model=TokenPair)
async def refresh_access_token(
    token_data: TokenRefresh,
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Обновление access токена с помощью refresh токена.
    
    - Проверяет refresh токен в БД
    - Проверяет срок действия
    - Генерирует новый access токен
    - Опционально: генерирует новый refresh токен (rotation)
    """
    
    # 1. Декодируем refresh токен
    try:
        payload = decode_jwt(token=token_data.refresh_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id_str = payload.get("sub")
    
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload"
        )
    
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user_id in token"
        )
    
    # 2. Проверяем, что токен есть в БД
    result = await session.execute(
        select(Token).where(Token.refresh_token == token_data.refresh_token)
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    # 3. Проверяем срок действия
    if token_record.expires_at < datetime.utcnow():
        # Удаляем истёкший токен
        await session.delete(token_record)
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # 4. Получаем пользователя
    user = await session.get(User, user_id)
    
    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found or blocked"
        )
    
    # 5. Создаём новый access токен
    access_token_payload = {
        "sub": user.user_id,
        "email": user.email,
        "role_id": user.role_id,
    }
    
    new_access_token = encode_jwt(
        payload=access_token_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )
    
    # 6. Опционально: создаём новый refresh токен (token rotation)
    # Для большей безопасности можно генерировать новый refresh каждый раз
    new_refresh_token = encode_jwt(
        payload={"sub": user.user_id, "email": user.email},
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )
    
    # Обновляем запись в БД
    token_record.refresh_token = new_refresh_token
    token_record.expires_at = datetime.utcnow() + timedelta(days=settings.auth_jwt.refresh_token_expire_days)
    await session.commit()
    
    return TokenPair(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


# ============ ВЫХОД (LOGOUT) ============

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    token_data: TokenRefresh,
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Выход пользователя.
    
    - Удаляет refresh токен из БД
    - После этого токен становится невалидным
    """
    
    # Удаляем токен из БД
    await session.execute(
        delete(Token).where(Token.refresh_token == token_data.refresh_token)
    )
    await session.commit()
    
    return None  # 204 No Content