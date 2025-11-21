# api/dependencies/auth.py
"""Dependencies для проверки авторизации пользователей"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError

<<<<<<< Updated upstream
from db.models.models import User
from db.session import db_helper
from auth.utils import decode_jwt
=======
from shared.db.models import User
from shared.db.session import db_helper
from employer.backend.app.auth.utils import decode_jwt
>>>>>>> Stashed changes


# Схема для извлечения токена из заголовка Authorization
http_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(db_helper.get_db),
) -> User:
    """
    Извлекает текущего пользователя из JWT access токена.
    
    Использование:
    ```python
    @router.get("/protected")
    async def protected_route(current_user: User = Depends(get_current_user)):
        return {"user_id": current_user.user_id}
    ```
    """
    
    token = credentials.credentials
    
    # 1. Декодируем токен
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Извлекаем user_id (он приходит как строка, конвертируем в int)
    user_id_str: str | None = payload.get("sub")
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token contains invalid user_id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Получаем пользователя из БД
    user = await session.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # 4. Проверяем статус
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is blocked",
        )
    
    return user


async def get_current_employer(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, что текущий пользователь - работодатель (role_id=2).
    
    Использование:
    ```python
    @router.post("/vacancies")
    async def create_vacancy(
        current_employer: User = Depends(get_current_employer)
    ):
        # Только работодатели могут создавать вакансии
    ```
    """
    
    # Проверяем роль (employer = 2)
    if current_user.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can perform this action",
        )
    
    return current_user
