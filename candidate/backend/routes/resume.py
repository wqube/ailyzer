# routes/resume.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# Импортируем Vacancy и db_helper для доступа к БД
from shared.db.models import Vacancy 
from shared.db.session import db_helper 

from ..core.utils import allowed_file
from ..services.resume_service import process_resume_file

router = APIRouter()

@router.post("/api/upload-resume")  
async def upload_resume(
    fullname: str = Form(...),
    # interview_topic: str = Form(...), # Убираем, так как будет браться из вакансии
    vacancy_id: int = Form(...), # <-- ДОБАВЛЯЕМ ID ВАКАНСИИ
    select_language: str = Form("ru"),
    resume: UploadFile = File(...),
    session: AsyncSession = Depends(db_helper.get_db) # <-- ДОБАВЛЯЕМ ДОСТУП К БД
):
    print(f"Received resume: {resume.filename}")
    print(f"Fullname: {fullname}")
    print(f"Vacancy ID: {vacancy_id}")
    print(f"Language: {select_language}")
    
    if not resume:
        raise HTTPException(status_code=400, detail="Файл не найден")
    if resume.filename == "":
        raise HTTPException(status_code=400, detail="Файл не выбран")
    if not allowed_file(resume.filename):
        raise HTTPException(status_code=400, detail="Недопустимый формат файла")

    # 1. Получаем информацию о вакансии из БД
    print(f"1) Fetching Vacancy {vacancy_id}...")
    result = await session.execute(
        select(Vacancy).where(Vacancy.vacancy_id == vacancy_id)
    )
    vacancy = result.scalars().first()
    
    if not vacancy:
        raise HTTPException(status_code=404, detail=f"Vacancy с ID {vacancy_id} не найдена")
    
    # 2. Формируем тему для проверки резюме и собеседования
    # Собираем все ключевые данные в одну строку для LLM
    topic = (
        f"Вакансия: {vacancy.title}. "
        f"Уровень: {vacancy.level}. "
        f"Требования: {vacancy.requirements}. "
        f"Описание: {vacancy.description}"
    )
    print(f"2) Generated topic based on vacancy.")
    
    try:
        # 3. Передаем сформированную тему в сервис
        result = await process_resume_file(
            resume, 
            topic, # <-- ПЕРЕДАЁМ СФОРМИРОВАННУЮ ТЕМУ
            select_language
        )
        print(f"Analysis result: {result}")
        # Дополнительно можно добавить vacancy_id в результат, если нужно
        result['vacancy_id'] = vacancy_id
        return result
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки резюме: {str(e)}")