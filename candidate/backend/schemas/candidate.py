from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any
from datetime import datetime

# Схема для заявки кандидата
class CandidateApplication(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    position: Optional[str] = None
    experience: Optional[int] = None
    salary_expectation: Optional[int] = None
    cover_letter: Optional[str] = None
    vacancy_id: Optional[int] = None

    @validator('phone')
    def validate_phone(cls, v):
        if not v.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('Phone must contain only digits and valid symbols')
        return v

    @validator('experience')
    def validate_experience(cls, v):
        if v is not None and (v < 0 or v > 50):
            raise ValueError('Experience must be between 0 and 50 years')
        return v

# Схема для ответа после создания заявки
class ApplicationResponse(BaseModel):
    application_id: int
    candidate_id: int
    email: str
    full_name: str
    vacancy_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True