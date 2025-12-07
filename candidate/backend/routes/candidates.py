from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
import os

from shared.db.session import db_helper
from shared.db.models import Application, Resume # Удален импорт User

# CANDIDATE_ROLE_ID больше не нужен
router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


@router.post("/create")
async def create_candidate(
    email: str = Form(...),
    full_name: str = Form(...),
    phone: str = Form(...),
    vacancy_id: Optional[int] = Form(None),
    parsed_text: Optional[str] = Form(None),
    # metadata_json теперь будет содержать experience и salary_expectation, 
    # введенные вручную, если резюме не загружено
    metadata_json: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(db_helper.get_db),
):
    print("=" * 60)
    print("=== /api/candidates/create CALLED ===")
    print(f"Email: {email}")
    print(f"Full Name: {full_name}")
    print(f"Phone: {phone}")
    print(f"Vacancy ID: {vacancy_id}")
    print(f"Has resume file: {resume is not None}")
    print(f"Resume filename: {resume.filename if resume else 'None'}")
    print("=" * 60)
    
    # 4. Парсим metadata_json в первую очередь
    print("1) Processing metadata...")
    metadata = {}
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
            print(f"✓ Metadata parsed successfully: {metadata}")
        except Exception as e:
            print(f"❌ Error parsing metadata: {e}")
            metadata = {}
    else:
        print("⚠ No metadata provided")

    # 1. Создаём/находим заявку (Application)
    # Используем данные из формы для создания Application
    
    # 2. Проверяем, нет ли уже заявки с таким email на эту вакансию
    if vacancy_id:
        q = await session.execute(
            select(Application).where(
                Application.email == email,
                Application.vacancy_id == vacancy_id
            )
        )
        existing_app = q.scalars().first()
        
        if existing_app:
            print(f"⚠️ Application already exists! Application ID: {existing_app.application_id}")
            application = existing_app
        else:
            # Создаём новую заявку с данными из формы/метаданных
            application = Application(
                email=email,
                full_name=full_name,
                phone=phone,
                vacancy_id=vacancy_id,
                # Добавляем необязательные поля сразу из метаданных формы
                experience=metadata.get('experience'),
                salary_expectation=metadata.get('salary_expectation'),
            )
            session.add(application)
            await session.flush()
            print(f"✓ Application created with ID: {application.application_id}")
    else:
        # Если нет vacancy_id, создаём заявку без привязки к вакансии
        application = Application(
            email=email,
            full_name=full_name,
            phone=phone,
            vacancy_id=None,
            # Добавляем необязательные поля сразу из метаданных формы
            experience=metadata.get('experience'),
            salary_expectation=metadata.get('salary_expectation'),
        )
        session.add(application)
        await session.flush()
        print(f"✓ Application created (no vacancy) with ID: {application.application_id}")

    print("3) Skipping User creation. Data stored only in Application.")

    # 4. Сохраняем файл резюме
    print("4) Saving resume file...")
    file_path = None
    if resume:
        folder = "uploads/resumes"
        os.makedirs(folder, exist_ok=True)
        # Обязательно используем `application.application_id` после `session.flush()`
        file_path = os.path.join(folder, f"app_{application.application_id}_{resume.filename}")
        
        try:
            with open(file_path, "wb") as f:
                content = await resume.read()
                f.write(content)
            print(f"✓ Resume file saved to: {file_path}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    else:
        print("⚠ No resume file provided")

    # 5. Создаём запись резюме
    # Делаем это, только если есть файл или парсированный текст (хотя бы одно из них)
    if resume or parsed_text:
        print("5) Creating resume record...")
        print(f"   - application_id: {application.application_id}")
        print(f"   - vacancy_id: {vacancy_id}")
        print(f"   - file_path: {file_path}")
        print(f"   - parsed_text length: {len(parsed_text) if parsed_text else 0}")
        
        db_resume = Resume(
            application_id=application.application_id,  
            vacancy_id=vacancy_id,
            file_path=file_path,
            parsed_text=parsed_text,
            metadata_json=metadata,
        )
        session.add(db_resume)
        print("✓ Resume record created")
    else:
        db_resume = None
        print("5) Skipping Resume record creation (no file and no parsed text)")


    # 6. Коммит в БД
    print("6) Committing to database...")
    try:
        # Обновление Application данными из метаданных/парсинга:
        # 1. Если был парсинг, он перепишет опыт/зарплату, введенные вручную
        # 2. Если парсинга не было, Application уже содержит данные из формы
        
        # Обновляем Application данными из parsed_text/metadata (если парсинг прошел)
        # В этом месте мы должны обновить поля, только если пришел результат парсинга
        # (т.е. parsed_text не None), иначе оставляем данные, которые пришли из формы.
        if parsed_text and db_resume and metadata:
            # Применяем данные из метаданных парсинга к Application
            application.position = metadata.get('position', application.position)
            # Применяем опыт и зарплату из метаданных парсинга
            # Если поля не были в Application, они добавятся, если были - обновятся
            application.experience = metadata.get('experience', application.experience)
            application.salary_expectation = metadata.get('salary_expectation', application.salary_expectation)


        await session.commit()
        print("✓ Transaction committed successfully")
    except Exception as e:
        print(f"❌ Error committing transaction: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # 7. Финальный ответ
    print("=" * 60)
    print("=== /api/candidates/create FINISHED SUCCESSFULLY ===")
    print(f"Application ID: {application.application_id}")
    print(f"Resume ID: {db_resume.resume_id if db_resume else 'None'}")
    print(f"Vacancy ID: {vacancy_id}")
    print("=" * 60)
    
    return {
        "status": "success",
        "application_id": application.application_id,
        "resume_id": db_resume.resume_id if db_resume else None,
        "vacancy_id": vacancy_id,
        "file_path": file_path,
    }