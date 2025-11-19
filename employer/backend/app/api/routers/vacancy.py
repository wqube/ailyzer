# api/routers/vacancy.py
"""CRUD для вакансий с авторизацией"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from db.models.models import Vacancy, User
from db.session import db_helper
from schemas.vacancy import VacancyCreate, VacancyRead
from api.dependencies.auth import get_current_employer

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])


# ============ СОЗДАНИЕ ВАКАНСИИ ============

@router.post("/", response_model=VacancyRead, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy: VacancyCreate,
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Создать новую вакансию.
    
    - Требует авторизации (Bearer token)
    - Только для работодателей (role_id=2)
    - hr_id назначается автоматически из токена
    """
    
    # Создаём вакансию от имени текущего работодателя
    new_vacancy = Vacancy(
        title=vacancy.title,
        description=vacancy.description,
        requirements=vacancy.requirements,
        level=vacancy.level,
        hr_id=current_employer.user_id,  # 👈 Автоматически из токена
        status="active",
    )
    
    session.add(new_vacancy)
    await session.commit()
    await session.refresh(new_vacancy)
    
    return new_vacancy


# ============ ПОЛУЧИТЬ МОИ ВАКАНСИИ ============

@router.get("/my", response_model=List[VacancyRead])
async def get_my_vacancies(
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Получить все вакансии текущего работодателя.
    
    - Требует авторизации
    - Возвращает только вакансии, созданные текущим пользователем
    """
    
    result = await session.execute(
        select(Vacancy)
        .where(Vacancy.hr_id == current_employer.user_id)
        .order_by(Vacancy.created_at.desc())
    )
    
    vacancies = result.scalars().all()
    return vacancies


# ============ ПОЛУЧИТЬ ВСЕ ВАКАНСИИ (публичный эндпоинт) ============

@router.get("/", response_model=List[VacancyRead])
async def get_all_vacancies(
    session: AsyncSession = Depends(db_helper.get_db),
    status_filter: str | None = None,  # Опциональный фильтр по статусу
):
    """
    Получить все активные вакансии (публичный эндпоинт).
    
    - Не требует авторизации
    - Можно фильтровать по статусу: ?status_filter=active
    """
    
    query = select(Vacancy)
    
    if status_filter:
        query = query.where(Vacancy.status == status_filter)
    else:
        # По умолчанию показываем только активные
        query = query.where(Vacancy.status == "active")
    
    query = query.order_by(Vacancy.created_at.desc())
    
    result = await session.execute(query)
    vacancies = result.scalars().all()
    
    return vacancies


# ============ ПОЛУЧИТЬ КОНКРЕТНУЮ ВАКАНСИЮ ============

@router.get("/{vacancy_id}", response_model=VacancyRead)
async def get_vacancy(
    vacancy_id: int,
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Получить вакансию по ID.
    
    - Не требует авторизации
    """
    
    vacancy = await session.get(Vacancy, vacancy_id)
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    return vacancy


# ============ ОБНОВИТЬ ВАКАНСИЮ ============

@router.patch("/{vacancy_id}", response_model=VacancyRead)
async def update_vacancy(
    vacancy_id: int,
    vacancy_update: VacancyCreate,  # Можно создать отдельную схему VacancyUpdate
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Обновить вакансию.
    
    - Требует авторизации
    - Только владелец вакансии может её обновить
    """
    
    vacancy = await session.get(Vacancy, vacancy_id)
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    # Проверяем, что пользователь - владелец вакансии
    if vacancy.hr_id != current_employer.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own vacancies"
        )
    
    # Обновляем поля
    vacancy.title = vacancy_update.title
    vacancy.description = vacancy_update.description
    vacancy.requirements = vacancy_update.requirements
    vacancy.level = vacancy_update.level
    
    await session.commit()
    await session.refresh(vacancy)
    
    return vacancy


# ============ УДАЛИТЬ ВАКАНСИЮ ============

@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: int,
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Удалить вакансию (или закрыть - изменить статус на 'closed').
    
    - Требует авторизации
    - Только владелец вакансии может её удалить
    """
    
    vacancy = await session.get(Vacancy, vacancy_id)
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    # Проверяем владельца
    if vacancy.hr_id != current_employer.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own vacancies"
        )
    
    # Вариант 1: Мягкое удаление (закрытие)
    vacancy.status = "closed"
    await session.commit()
    
    # Вариант 2: Полное удаление
    # await session.delete(vacancy)
    # await session.commit()
    
    return None  # 204 No Content