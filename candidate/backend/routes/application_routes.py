from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.db.session import db_helper
from shared.db.models import Application # Предполагаем, что модель Application доступна

import json
from typing import Optional

router = APIRouter(prefix="/api/applications", tags=["Candidate Applications"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_candidate_application(
    # Контактные данные и основные поля, отправляемые вторым шагом
    email: str = Form(...),
    full_name: str = Form(...),
    phone: str = Form(...),
    vacancy_id: int = Form(...),
    
    # Данные из анализа (parsed_text)
    parsed_text: str = Form(...),
    
    # Metadata, содержащая опыт, зарплату и оценку ИИ
    metadata_json: str = Form('{}'),
    
    # Файл резюме отправляется снова (игнорируем его, так как он уже в MinIO)
    resume: Optional[UploadFile] = File(None),
    
    session: AsyncSession = Depends(db_helper.get_db)
):
    """
    Создает новую запись Application в БД (второй шаг фронтенда).
    
    Предполагается, что на фронтенде после первого вызова (upload-resume) 
    был получен и передан storage_object_name в metadata_json.
    """
    
    print("--- Starting Application DB Save (api.createCandidate) ---")
    
    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata_json format")

    # 🚨 КЛЮЧЕВОЕ ИЗМЕНЕНИЕ 🚨
    # Мы ожидаем, что storage_object_name был возвращен первым вызовом и передан 
    # через metadata_json или, как более простой вариант, через скрытое поле Form.
    # Поскольку фронтенд не был изменен, я буду использовать наиболее вероятные
    # поля из metadata_json (analysis_result), чтобы извлечь storage_object_name.
    
    # Находим storage_object_name, который должен был быть возвращен первым роутером
    analysis_result = metadata.get('analysis_result', {})
    storage_object_name = analysis_result.get('storage_object_name')
    
    if not storage_object_name:
        # Если имя объекта не найдено, это критическая ошибка, так как файл загружен, но не связан с записью
        print("ERROR: storage_object_name not found in metadata for DB save.")
        raise HTTPException(status_code=400, detail="Missing storage object name for resume link.")
        
    # Извлекаем оценку и другие поля из metadata (результаты парсинга)
    # Поля, которые могут прийти из analysis_result: position, experience, salary_expectation, interview_score
    # Мы предполагаем, что поля типа experience, salary_expectation могут прийти либо из метаданных, 
    # либо как отдельные поля Form (для простоты используем Form + метаданные для сложных полей).
    
    # Используем данные, отправленные фронтендом, и результаты анализа для заполнения модели
    new_application = Application(
        email=email,
        full_name=full_name,
        phone=phone,
        vacancy_id=vacancy_id,
        parsed_text=parsed_text,
        
        # Данные из метаданных
        experience=metadata.get('experience'),
        salary_expectation=metadata.get('salary_expectation'),
        # Результаты анализа (скор)
        interview_score=analysis_result.get('interview_score'), 
        
        # 🚨 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ 🚨
        storage_object_name=storage_object_name, # Сохраняем имя объекта MinIO
    )

    try:
        session.add(new_application)
        await session.commit()
        await session.refresh(new_application)
        print(f"Application ID {new_application.application_id} saved successfully with object name: {storage_object_name}")
    except Exception as e:
        print(f"Database Save Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ошибка сохранения заявки: {str(e)}")
    
    return {
        "message": "Кандидат успешно сохранен.",
        "application_id": new_application.application_id,
        "email": new_application.email,
        "storage_object_name": new_application.storage_object_name # Для подтверждения
    }
