from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from shared.db.session import db_helper
from shared.db.models import User, Application
from ...api.dependencies.auth import get_current_employer

router = APIRouter(prefix="/interview_scores", tags=["Interview Scores"])

# Схема для входящего запроса оценки
class ScoreUpdate(BaseModel):
    application_id: int
    score: float = Field(..., ge=0, le=100) # Оценка от 0 до 100 (или 10)

@router.post("/", status_code=status.HTTP_200_OK)
async def set_interview_score(
    score_data: ScoreUpdate,
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Установить (или обновить) оценку интервью для кандидата.
    Обновляет поле interview_score в таблице Application.
    """
    
    # 1. Получаем заявку
    application = await session.get(Application, score_data.application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # 2. Проверяем права (вакансия должна принадлежать этому HR)
    # application.vacancy (lazy load) или делаем запрос к вакансии, если relationship не подгружен
    # Для надежности лучше загрузить вакансию, если она не eager loaded
    if application.vacancy_id:
        from shared.db.models import Vacancy
        vacancy = await session.get(Vacancy, application.vacancy_id)
        if not vacancy or vacancy.hr_id != current_employer.user_id:
             raise HTTPException(status_code=403, detail="Not authorized to grade this candidate")
    
    # 3. Обновляем оценку
    application.interview_score = score_data.score
    
    # Обновляем статус, если это первая оценка
    if application.status == "new":
        application.status = "interviewed"

    await session.commit()
    await session.refresh(application)
    
    return {"message": "Score updated", "new_score": application.interview_score}