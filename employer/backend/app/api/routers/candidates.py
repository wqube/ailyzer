from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.db.models.models import User, Resume
from app.core.security import get_password_hash
from sqlalchemy import select
import json
import os


router = APIRouter(
    prefix="/api/candidates",
    tags=["candidates"]
)


@router.post("/create")
async def create_candidate(
    email: str = Form(...),
    password: str = Form(...),
    vacancy_id: int | None = Form(None),
    parsed_text: str | None = Form(None),
    metadata_json: str | None = Form(None),
    file: UploadFile | None = File(None),
    session: AsyncSession = Depends(get_session)
):
    # Проверяем уникальность e-mail
    q = await session.execute(select(User).where(User.email == email))
    if q.scalars().first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Создание пользователя
    new_user = User(
        email=email,
        password=get_password_hash(password),
        role_id=2  # роль кандидата
    )
    session.add(new_user)
    await session.flush()  # получаем user_id

    # --- Обработка файла резюме ---
    file_path = None
    if file:
        folder = "uploads/resumes"
        os.makedirs(folder, exist_ok=True)
        file_path = f"{folder}/{new_user.user_id}_{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

    # --- Обработка metadata_json ---
    metadata = None
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
        except:
            raise HTTPException(status_code=400, detail="metadata_json must be valid JSON")

    # --- Создание резюме ---
    resume = Resume(
        candidate_id=new_user.user_id,
        vacancy_id=vacancy_id,
        file_path=file_path,
        parsed_text=parsed_text,
        metadata_json=metadata
    )

    session.add(resume)
    await session.commit()

    return {
        "status": "success",
        "candidate_id": new_user.user_id,
        "resume_id": resume.resume_id,
        "file_path": file_path
    }
