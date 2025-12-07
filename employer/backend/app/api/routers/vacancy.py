"""
CRUD для вакансий с авторизацией и получением данных кандидатов с агрегированными оценками.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
# Добавляем func для агрегационных функций (AVG, COUNT)
from sqlalchemy import select, func
from typing import List, Optional

from shared.db.session import db_helper
# Добавляем InterviewScore, который нужен для агрегации
from shared.db.models import User, Vacancy, Application
# 👈 ИМПОРТИРУЕМ ФУНКЦИЮ ДЛЯ MINIO
from shared.storage.minio_client import generate_presigned_url 

from ...schemas.vacancy import VacancyCreate, VacancyRead, VacancyUpdate
from ...schemas.application import CandidateApplicationRead # Используем новую схему с полями оценок
from ...api.dependencies.auth import get_current_employer

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


# ============ ПОЛУЧИТЬ КОНКРЕТНУЮ АКТИВНУЮ ВАКАНСИЮ ============

@router.get("/{vacancy_id}", response_model=VacancyRead)
async def get_active_vacancy(
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
    
    # Проверяем, что вакансия активна
    if vacancy.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not available"
        )
    
    return vacancy


# ============ ОБНОВИТЬ ВАКАНСИЮ (ЧАСТИЧНО) ============

@router.patch("/{vacancy_id}", response_model=VacancyRead)
async def update_vacancy(
    vacancy_id: int,
    vacancy_update: VacancyUpdate,  # Используем VacancyUpdate
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Обновить вакансию (частично).
    
    - Требует авторизации
    - Только владелец вакансии может её обновить
    - Использует model_dump(exclude_unset=True) для обработки только переданных полей
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
    
    # Используем model_dump для получения только измененных полей
    update_data = vacancy_update.model_dump(exclude_unset=True)

    # Обновляем поля
    for key, value in update_data.items():
        setattr(vacancy, key, value)
    
    await session.commit()
    await session.refresh(vacancy)
    
    return vacancy


# ============ УДАЛИТЬ ВАКАНСИЮ (ПОЛНОЕ УДАЛЕНИЕ ИЗ БД) ============

@router.delete("/delete/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: int,
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Удалить вакансию (полное удаление из БД).
    
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
    
    # Жеское удаление из БД
    await session.delete(vacancy)
    await session.commit()
    
    return None  # 204 No Content


# ============ ПОЛУЧИТЬ КАНДИДАТОВ ДЛЯ ВАКАНСИИ ============

@router.get("/{vacancy_id}/candidates", response_model=List[CandidateApplicationRead])
async def get_candidates_for_vacancy(
    vacancy_id: int,
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Получить список кандидатов (откликов) для вакансии, включая Presigned URL для резюме.
    """
    
    # 1. Проверяем существование и владение вакансией
    vacancy = await session.get(Vacancy, vacancy_id)
    
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")
        
    if vacancy.hr_id != current_employer.user_id:
        raise HTTPException(status_code=403, detail="Not the owner")

    # 2. Простой запрос к Application
    query = (
        select(Application)
        .where(Application.vacancy_id == vacancy_id)
        .order_by(Application.created_at.desc())
    )

    result = await session.execute(query)
    candidates = result.scalars().all()
    
    # 3. Генерируем Presigned URL для каждого кандидата
    candidates_with_url = []
    for candidate in candidates:
        # Копируем атрибуты в словарь, чтобы добавить вычисляемое поле
        candidate_dict = candidate.__dict__.copy()
        
        # Генерируем ссылку, если имя объекта MinIO сохранено
        if candidate.storage_object_name:
            candidate_dict['resume_url'] = generate_presigned_url(
                object_name=candidate.storage_object_name
            )
        else:
            candidate_dict['resume_url'] = None
            
        candidates_with_url.append(candidate_dict)

    # Возвращаем список словарей для обработки Pydantic (с включенным resume_url)
    return candidates_with_url


# ============ ПОЛУЧИТЬ ОДНОГО КАНДИДАТА ПО application_id ============

@router.get("/candidates/{application_id}", response_model=CandidateApplicationRead)
async def get_single_candidate(
    application_id: int,
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Получить детальные данные по конкретному кандидату, включая Presigned URL для резюме.
    """
    
    # 1. Получаем заявку
    application = await session.get(Application, application_id)
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
        
    # 2. Проверяем права через вакансию
    vacancy = await session.get(Vacancy, application.vacancy_id)
    
    if not vacancy or vacancy.hr_id != current_employer.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 3. Генерируем Presigned URL
    application_dict = application.__dict__.copy()
    if application.storage_object_name:
        application_dict['resume_url'] = generate_presigned_url(
            object_name=application.storage_object_name
        )
    else:
        application_dict['resume_url'] = None
    
    # Возвращаем словарь для обработки Pydantic (с включенным resume_url)
    return application_dict