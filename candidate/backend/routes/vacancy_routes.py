from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.db.session import db_helper
from shared.db.models import Vacancy

# router = APIRouter(prefix="/api/vacancies", tags=["Vacancies"])
router = APIRouter(prefix="/vacancies", tags=["Vacancies"])

@router.get("/{vacancy_id}")
async def get_vacancy_by_id(
    vacancy_id: int,
    session: AsyncSession = Depends(db_helper.get_db)
):
    """
    Получить вакансию по ID (публичный эндпоинт для кандидатов)
    """
    print(f"=== GET VACANCY BY ID: {vacancy_id} ===")
    
    # Находим вакансию
    result = await session.execute(
        select(Vacancy).where(Vacancy.vacancy_id == vacancy_id)
    )
    vacancy = result.scalars().first()
    
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    
    # Проверяем статус вакансии
    if vacancy.status != "active":
        raise HTTPException(status_code=400, detail="Vacancy is not active")
    
    return {
        "vacancy_id": vacancy.vacancy_id,
        "title": vacancy.title,
        "description": vacancy.description,
        "requirements": vacancy.requirements,
        "level": vacancy.level,
        "created_at": vacancy.created_at.isoformat() if vacancy.created_at else None,
        "status": vacancy.status
    }
