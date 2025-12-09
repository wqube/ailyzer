from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
import os

from shared.db.session import db_helper
from shared.db.models import Application, Resume 
from shared.storage.minio_client import generate_presigned_url 
from sqlalchemy.exc import SQLAlchemyError 

# router = APIRouter(prefix="/api/candidates", tags=["Candidates"])
router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("/create")
async def create_candidate(
    email: str = Form(...),
    full_name: str = Form(...),
    phone: str = Form(...),
    vacancy_id: Optional[int] = Form(None),
    parsed_text: Optional[str] = Form(None),
    metadata_json: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Создает новую заявку кандидата. 
    (Исправленная версия, где убран лишний аргумент из Resume и добавлена детальная обработка ошибок)
    """
    print("=" * 60)
    print("=== /api/candidates/create CALLED (MinIO FLOW) ===")
    
    # 1. Парсим metadata_json
    metadata = {}
    storage_object_name = None
    
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
            analysis_result = metadata.get('analysis_result', {})
            storage_object_name = analysis_result.get('storage_object_name')
            print(f"✓ Metadata parsed. Storage Object Name found: {storage_object_name}")
        except Exception as e:
            print(f"❌ Error parsing metadata: {e}")
            metadata = {}

    # 2. Создаём/находим заявку (Application)
    application = None
    if vacancy_id:
        q = await session.execute(
            select(Application).where(
                Application.email == email,
                Application.vacancy_id == vacancy_id
            )
        )
        existing_app = q.scalars().first()
        
        if existing_app:
            print(f"⚠️ Application already exists! ID: {existing_app.application_id}. Updating...")
            application = existing_app
        
    if not application:
        # Создаём новую заявку
        application = Application(
            email=email,
            full_name=full_name,
            phone=phone,
            vacancy_id=vacancy_id,
            experience=metadata.get('experience'),
            salary_expectation=metadata.get('salary_expectation'),
            storage_object_name=storage_object_name, 
        )
        session.add(application)
        await session.flush()
        print(f"✓ New Application created with ID: {application.application_id}")
    else:
        # Обновляем существующую заявку
        application.full_name = full_name
        application.phone = phone
        if storage_object_name:
             application.storage_object_name = storage_object_name
        application.experience = metadata.get('experience', application.experience)
        application.salary_expectation = metadata.get('salary_expectation', application.salary_expectation)


    # 3. Создаём запись Resume (для связывания с Application)
    db_resume = None
    if parsed_text: 
        print("3) Creating resume record...")
        db_resume = Resume(
            application_id=application.application_id,  
            vacancy_id=vacancy_id,
            # storage_object_name удален, так как он не существует в модели Resume
            parsed_text=parsed_text,
            metadata_json=metadata,
        )
        session.add(db_resume)
        print("✓ Resume record created")
    else:
        print("3) Skipping Resume record creation (no parsed text)")

    # 4. Коммит в БД с подробной обработкой ошибок
    print("4) Committing to database...")
    try:
        await session.commit()
        await session.refresh(application)
        if db_resume:
            await session.refresh(db_resume)
        print("✓ Transaction committed successfully")
    except SQLAlchemyError as e:
        await session.rollback()
        print(f"❌ CRITICAL DB ERROR during commit: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Ошибка сохранения данных: Нарушение ограничений БД или дублирование записи. Детали: {type(e).__name__}"
        )
    except Exception as e:
        await session.rollback()
        print(f"❌ CRITICAL UNKNOWN ERROR during commit: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )
    
    # 5. Финальный ответ
    resume_link = None
    if application.storage_object_name:
        try:
            resume_link = generate_presigned_url(application.storage_object_name)
        except Exception as e:
             print(f"Warning: Could not generate presigned URL: {e}")
    
    print("=" * 60)
    
    return {
        "status": "success",
        "application_id": application.application_id,
        "resume_id": db_resume.resume_id if db_resume else None,
        "vacancy_id": vacancy_id,
        "minio_link": resume_link, 
    }


# 🚨 НОВЫЙ МАРШРУТ ДЛЯ ПОДСЧЕТА КАНДИДАТОВ 🚨
@router.get("/vacancy/{vacancy_id}")
async def get_candidates_by_vacancy(
    vacancy_id: int, 
    session: AsyncSession = Depends(db_helper.get_db)
):
    """
    Возвращает список всех заявок (Application) для указанной вакансии.
    Используется для подсчета общего количества кандидатов на дашборде.
    """
    print(f"--- Fetching Candidates for Vacancy ID: {vacancy_id} ---")
    
    # Запрос всех заявок, связанных с данным vacancy_id
    query = select(Application).where(Application.vacancy_id == vacancy_id)
    
    try:
        result = await session.execute(query)
        applications = result.scalars().all()
        
        # Преобразуем объекты Application в формат, понятный фронтенду
        candidate_list = []
        for app in applications:
            # Возвращаем только необходимые поля для дашборда
            candidate_list.append({
                "id": app.application_id,
                "email": app.email,
                "full_name": app.full_name,
                "vacancy_id": app.vacancy_id,
                "created_at": app.created_at.isoformat() if app.created_at else None,
            })
            
        print(f"--- Found {len(candidate_list)} candidates for Vacancy ID {vacancy_id} ---")
        return candidate_list
        
    except Exception as e:
        print(f"Error fetching candidates for vacancy {vacancy_id}: {e}")
        # Возвращаем 500 ошибку, если запрос к БД не удался
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось получить кандидатов для вакансии {vacancy_id}. Ошибка БД: {str(e)}"
        )