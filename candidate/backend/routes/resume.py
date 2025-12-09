from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
import os

# Импортируем Vacancy и db_helper для доступа к БД
from shared.db.models import Vacancy 
from shared.db.session import db_helper 
# Импортируем функцию для загрузки в MinIO и генерации ссылки
# NOTE: generate_presigned_url больше не используется, так как это происходит на этапе чтения
from shared.storage.minio_client import upload_resume_object, generate_presigned_url 

from ..core.utils import allowed_file
from ..services.resume_service import process_resume_file

router = APIRouter()

# @router.post("/api/upload-resume")  
@router.post("/upload-resume")  
async def upload_resume(
    # 🚨 ИСПРАВЛЕНИЕ 422: Удалил email и phone из формы, так как они не отправляются на этом шаге
    fullname: str = Form(...),
    vacancy_id: int = Form(...),
    select_language: str = Form("ru"),
    resume: UploadFile = File(...),
    session: AsyncSession = Depends(db_helper.get_db)
):
    print(f"Received resume for analysis: {resume.filename}")
    
    if not resume or resume.filename == "":
        raise HTTPException(status_code=400, detail="Файл не найден или не выбран")
    if not allowed_file(resume.filename): # type: ignore
        raise HTTPException(status_code=400, detail="Недопустимый формат файла")

    # 1. Получаем информацию о вакансии из БД
    result = await session.execute(
        select(Vacancy).where(Vacancy.vacancy_id == vacancy_id)
    )
    vacancy = result.scalars().first()
    
    if not vacancy:
        raise HTTPException(status_code=404, detail=f"Vacancy с ID {vacancy_id} не найдена")
    
    # 2. Формируем тему для проверки резюме
    topic = (
        f"Вакансия: {vacancy.title}. "
        f"Уровень: {vacancy.level}. "
        f"Требования: {vacancy.requirements}. "
        f"Описание: {vacancy.description}"
    )
    
    # --- Чтение и загрузка файла в MinIO ---
    object_name = None
    try:
        file_content = await resume.read()
        
        file_extension = os.path.splitext(resume.filename)[1] if resume.filename else '.pdf'
        base_filename = os.path.splitext(os.path.basename(resume.filename))[0]
        safe_fullname = fullname.replace(' ', '_').replace('.', '').lower()
        
        object_name = f"vacancy_{vacancy_id}/{uuid4().hex}_{safe_fullname}_{base_filename}{file_extension}"
        
        print(f"Uploading file to MinIO as: {object_name}")
        
        upload_resume_object(
            object_name=object_name,
            data=file_content,
            content_type=resume.content_type
        )
        print("File uploaded successfully to MinIO.")
        
    except Exception as e:
        print(f"MinIO Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла в хранилище: {str(e)}")

    # 3. Передаем содержимое файла, имя файла, тему и язык в сервис для анализа
    try:
        result = await process_resume_file(
            file_content,
            resume.filename,
            topic,
            select_language
        )
        print(f"Analysis result: {result}")
        
        # 4. Возвращаем результат анализа и КЛЮЧЕВОЕ ИМЯ ОБЪЕКТА
        result['vacancy_id'] = vacancy_id
        result['storage_object_name'] = object_name # 👈 Ключевое изменение: возвращаем имя объекта
        
        return result
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки резюме: {str(e)}")