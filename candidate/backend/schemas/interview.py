from pydantic import BaseModel, Field, conint
from typing import Optional, List
from datetime import datetime

# Схема для создания/обновления оценки интервью (HR -> Backend)
class InterviewScoreCreate(BaseModel):
    """Схема для POST запроса оценки интервью."""
    score: conint(ge=0, le=10) = Field(..., description="Оценка от 0 до 10") # type: ignore
    comment: Optional[str] = Field(None, max_length=1000, description="Комментарий к оценке")
    stage: str = Field(default="general", description="Этап интервью (e.g., 'screening', 'technical')")

# Схема для чтения оценки интервью (Backend -> HR)
class InterviewScoreRead(BaseModel):
    """Схема для отображения сохраненной оценки интервью."""
    score_id: int
    application_id: int
    hr_id: int
    score: int
    comment: Optional[str]
    stage: str
    created_at: datetime
    
    class Config:
        from_attributes = True