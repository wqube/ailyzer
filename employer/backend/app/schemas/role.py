from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class RoleBase(BaseModel):
    pass


class RoleCreate(RoleBase):
    role_id: int
    name: str
    # Потом удалить надо будет. Так как будет создаваться автоматически после авторизации
    user: str


class RoleRead(RoleBase):
    role_id: int
    name: str
    users: str

    class Config:
        orm_mode = True
