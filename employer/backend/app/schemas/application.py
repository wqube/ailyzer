from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from datetime import datetime

# ============================================
# Схемы для Кандидата (Applicant)
# ============================================

class CandidateApplication(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    position: Optional[str] = None
    experience: Optional[int] = None
    salary_expectation: Optional[int] = None
    cover_letter: Optional[str] = None
    vacancy_id: Optional[int] = None
    interview_score: Optional[float] = None
    # 👈 ДОБАВЛЕНО: имя файла в MinIO, передается после успешной загрузки файла
    storage_object_name: Optional[str] = None 

    @validator('phone')
    def validate_phone(cls, v):
        # Простая очистка для валидации
        clean = v.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not clean.isdigit():
            raise ValueError('Phone must contain only digits and valid symbols')
        return v

    @validator('experience')
    def validate_experience(cls, v):
        if v is not None and (v < 0 or v > 50):
            raise ValueError('Experience must be between 0 and 50 years')
        return v

class ApplicationResponse(BaseModel):
    application_id: int
    email: str
    full_name: str
    vacancy_id: Optional[int]
    interview_score: Optional[float]
    created_at: datetime
    # 👈 ДОБАВЛЕНО: для соответствия модели БД
    storage_object_name: Optional[str] = None 

    class Config:
        from_attributes = True

# ============================================
# Схема для Работодателя (Employer view)
# ============================================

class CandidateApplicationRead(BaseModel):
    # Маппинг application_id -> id для фронтенда
    id: int = Field(alias="application_id") 
    full_name: str
    email: EmailStr
    phone: str
    experience: Optional[int] = None
    
    # Прямое поле из модели Application
    interview_score: Optional[float] = None
    
    # Дополнительные поля
    position: Optional[str] = None
    salary_expectation: Optional[int] = None
    cover_letter: Optional[str] = None
    # 👈 ДОБАВЛЕНО: для соответствия модели БД
    storage_object_name: Optional[str] = None 

    # Поля, ожидаемые фронтендом
    status: str
    applied_at: datetime = Field(alias="created_at")
    # 👈 ИЗМЕНЕНО: Удалено дефолтное значение-заглушка
    resume_url: Optional[str] = Field(None, title="Presigned URL для скачивания резюме")
    
    class Config:
        from_attributes = True
        populate_by_name = True