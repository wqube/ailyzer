from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from shared.db.session import db_helper
from shared.db.models import User, Role

from ...schemas.role import RoleCreate, RoleRead

router = APIRouter(prefix="/role", tags=["Role"])


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    session: AsyncSession = Depends(db_helper.get_db),
):
    # Создаём новую роль
    new_role = Role(
        role_id=role.role_id,
        name=role.name,
        # Потом удалить надо будет. Так как будет создаваться автоматически после авторизации
        user=role.user
    )

    session.add(new_role)
    await session.commit()
    await session.refresh(new_role)
    return new_role


@router.get("/", response_model=List[RoleRead])
async def get_roles(session: AsyncSession = Depends(db_helper.get_db)):
    result = await session.execute(select(Role))
    roles = result.scalars().all()
    return roles
