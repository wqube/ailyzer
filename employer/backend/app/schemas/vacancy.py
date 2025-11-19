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

# schemas/vacancy.py
# from pydantic import BaseModel, validator
# from datetime import datetime
# from typing import Optional

# class VacancyCreate(BaseModel):
#     title: str
#     description: str
#     requirements: str
#     level: str
    
#     @validator('level')
#     def validate_level(cls, v):
#         allowed_levels = ['junior', 'middle', 'senior']
#         if v not in allowed_levels:
#             raise ValueError(f'Level must be one of: {", ".join(allowed_levels)}')
#         return v

# class VacancyRead(BaseModel):
#     vacancy_id: int
#     title: str
#     description: str
#     requirements: str
#     level: str
#     status: str
#     hr_id: int
#     created_at: datetime
    
#     class Config:
#         from_attributes = True