# schemas/candidate.py
"""Схемы для кандидатов"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, Any


class CandidateBase(BaseModel):
    """Базовые поля кандидата"""
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None


class CandidateRead(CandidateBase):
    """Схема для чтения данных кандидата"""
    candidate_id: int
    user_id: int
    status: str = "new"
    resume_text: Optional[str] = None
    resume_file: Optional[str] = None
    vacancy_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateWithResume(CandidateRead):
    """Кандидат с полной информацией о резюме"""
    parsed_text: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    upload_date: Optional[datetime] = None


class CandidateStatusUpdate(BaseModel):
    """Схема для обновления статуса кандидата"""
    status: str = Field(..., description="new, reviewed, interviewed, rejected, hired")


class CandidateFilter(BaseModel):
    """Схема для фильтрации кандидатов"""
    vacancy_id: Optional[int] = None
    status: Optional[str] = None
    search: Optional[str] = None