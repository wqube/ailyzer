# schemas/vacancy.py
"""Схемы для вакансий"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class VacancyBase(BaseModel):
    """Базовые поля вакансии"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    level: Optional[str] = Field(None, description="Уровень: Intern, Junior, Middle, Senior, Lead")


class VacancyCreate(VacancyBase):
    """
    Схема для создания вакансии.
    
    hr_id НЕ передаётся - назначается автоматически из токена.
    """
    pass


class VacancyUpdate(BaseModel):
    """Схема для обновления вакансии (все поля опциональны)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    level: Optional[str] = None
    status: Optional[str] = Field(None, description="active или closed")


class VacancyRead(VacancyBase):
    """Схема для чтения вакансии (возвращается из API)"""
    vacancy_id: int
    hr_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (было orm_mode в v1)