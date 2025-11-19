# app/api/routers/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from db_old.models.models import User, Role
from db_old.session import db_helper
from schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(db_helper.get_db),
):
    # Проверяем, что email уникален
    result = await session.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Проверяем, что роль существует (если передаётся role_id)
    if user.role_id:
        role = await session.get(Role, user.role_id)
        if not role:
            raise HTTPException(status_code=400, detail=f"Role {user.role_id} not found")
    else:
        raise HTTPException(status_code=400, detail="role_id is required")

    # Создаём нового пользователя
    new_user = User(
        email=user.email,
        password=user.password,
        role_id=user.role_id,
        status="active",
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.get("/", response_model=List[UserRead])
async def get_users(session: AsyncSession = Depends(db_helper.get_db)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users

