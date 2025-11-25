from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
import os

from shared.db.session import db_helper
from shared.db.models import User, Application, Resume

CANDIDATE_ROLE_ID = 1
router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


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
    print("=" * 60)
    print("=== /api/candidates/create CALLED ===")
    print(f"Email: {email}")
    print(f"Full Name: {full_name}")
    print(f"Phone: {phone}")
    print(f"Vacancy ID: {vacancy_id}")
    print(f"Has resume file: {resume is not None}")
    print(f"Resume filename: {resume.filename if resume else 'None'}")
    print("=" * 60)
    
    # 1. Создаём заявку (Application)
    print("1) Creating application...")
    
    # Проверяем, нет ли уже заявки с таким email на эту вакансию
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
            # Можно либо вернуть ошибку, либо использовать существующую заявку
            # raise HTTPException(status_code=400, detail="Application already exists for this vacancy")
            application = existing_app
        else:
            # Создаём новую заявку
            application = Application(
                email=email,
                full_name=full_name,
                phone=phone,
                vacancy_id=vacancy_id,
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
        )
        session.add(application)
        await session.flush()
        print(f"✓ Application created (no vacancy) with ID: {application.application_id}")

    # 2. Проверяем/создаём пользователя (опционально)
    print("2) Checking/Creating user...")
    q = await session.execute(select(User).where(User.email == email))
    user = q.scalars().first()
    
    if not user:
        # Создаём пользователя только если его нет
        user = User(
            email=email,
            password_hash="TEMP_PASSWORD_HASH",  # Временный хеш
            role_id=CANDIDATE_ROLE_ID,
            status="active",
            city=None,
        )
        session.add(user)
        await session.flush()
        print(f"✓ User created with ID: {user.user_id}")
    else:
        print(f"✓ User already exists with ID: {user.user_id}")

    # 3. Сохраняем файл резюме
    print("3) Saving resume file...")
    file_path = None
    if resume:
        folder = "uploads/resumes"
        os.makedirs(folder, exist_ok=True)
        # Используем application_id для имени файла
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

    # 4. Парсим metadata_json
    print("4) Processing metadata...")
    metadata = None
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
            print(f"✓ Metadata parsed successfully")
        except Exception as e:
            print(f"❌ Error parsing metadata: {e}")
            metadata = {}
    else:
        print("⚠ No metadata provided")

    # 5. Создаём запись резюме (НОВАЯ СТРУКТУРА)
    print("5) Creating resume record...")
    print(f"   - candidate_id: {user.user_id}")
    print(f"   - application_id: {application.application_id}")
    print(f"   - vacancy_id: {vacancy_id}")
    print(f"   - file_path: {file_path}")
    print(f"   - parsed_text length: {len(parsed_text) if parsed_text else 0}")
    
    db_resume = Resume(
        candidate_id=user.user_id,
        application_id=application.application_id,  # НОВОЕ ПОЛЕ
        vacancy_id=vacancy_id,
        file_path=file_path,
        parsed_text=parsed_text,
        metadata_json=metadata,
    )
    session.add(db_resume)
    print("✓ Resume record created")

    # 6. Коммит в БД
    print("6) Committing to database...")
    try:
        await session.commit()
        print("✓ Transaction committed successfully")
    except Exception as e:
        print(f"❌ Error committing transaction: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    print("=" * 60)
    print("=== /api/candidates/create FINISHED SUCCESSFULLY ===")
    print(f"User ID: {user.user_id}")
    print(f"Application ID: {application.application_id}")
    print(f"Resume ID: {db_resume.resume_id}")
    print(f"Vacancy ID: {vacancy_id}")
    print("=" * 60)
    
    return {
        "status": "success",
        "user_id": user.user_id,
        "application_id": application.application_id,
        "resume_id": db_resume.resume_id,
        "vacancy_id": vacancy_id,
        "file_path": file_path,
    }
