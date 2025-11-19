from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
import os

from shared.db.session import db_helper
from shared.db.models import User, Role, Resume


router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


@router.post("/create")
async def create_candidate(
    email: str = Form(...),
    password_hash: str = Form(...),
    vacancy_id: Optional[int] = Form(None),
    parsed_text: Optional[str] = Form(None),
    metadata_json: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(db_helper.get_db),
):
    # 1. Проверяем, что email не занят
    q = await session.execute(select(User).where(User.email == email))
    if q.scalars().first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # 2. роль "candidate" (у тебя = 3 в employer)
    role_id = 3

    user = User(
        email=email,
        password_hash=password_hash,
        role_id=role_id,
        status="active",
        city=None,
    )
    session.add(user)
    await session.flush()

    # 3. Сохраняем файл резюме
    file_path = None
    if resume:
        folder = "uploads/resumes"
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"{user.user_id}_{resume.filename}")
        with open(file_path, "wb") as f:
            f.write(await resume.read())

    # 4. metadata_json
    metadata = None
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
        except:
            raise HTTPException(status_code=400, detail="metadata_json must be valid JSON")

    # 5. Создаём запись резюме
    db_resume = Resume(
        candidate_id=user.user_id,
        vacancy_id=vacancy_id,
        file_path=file_path,
        parsed_text=parsed_text,
        metadata_json=metadata,
    )
    session.add(db_resume)

    await session.commit()

    return {
        "status": "success",
        "candidate_id": user.user_id,
        "resume_id": db_resume.resume_id,
        "file_path": file_path,
    }
