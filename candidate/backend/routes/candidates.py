from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
import os

from shared.db.session import db_helper
from shared.db.models import User, Role, Resume

CANDIDATE_ROLE_ID = 1
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
    print("=== /api/candidates/create CALLED ===")
    # 1. Проверяем, что email не занят
    print("1) Checking email")

    q = await session.execute(select(User).where(User.email == email))
    if q.scalars().first():
        raise HTTPException(status_code=400, detail="Email already exists")

    role_id = CANDIDATE_ROLE_ID
    print("2) Creating user")
    user = User(
        email=email,
        password_hash=password_hash,
        role_id=role_id,
        status="active",
        city=None,
    )
    session.add(user)
    await session.flush()
    print("3) Saving file")

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
    print("4) Creating resume")

    # 5. Создаём запись резюме
    db_resume = Resume(
        candidate_id=user.user_id,
        vacancy_id=vacancy_id,
        file_path=file_path,
        parsed_text=parsed_text,
        metadata_json=metadata,
    )
    session.add(db_resume)
    print("5) Commit")

    await session.commit()
    print("=== /api/candidates/create FINISHED ===")
    return {
        "status": "success",
        "candidate_id": user.user_id,
        "resume_id": db_resume.resume_id,
        "file_path": file_path,
    }
