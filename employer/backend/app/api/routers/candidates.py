from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_old.session import get_session
from app.db_old.models.models import User, Resume
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


# ============ ПОЛУЧИТЬ КАНДИДАТОВ ПО ВАКАНСИИ ============

@router.get("/vacancy/{vacancy_id}", response_model=List[CandidateRead])
async def get_candidates_by_vacancy(
    vacancy_id: int,
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу: new, reviewed, interviewed, rejected, hired"),
    search: Optional[str] = Query(None, description="Поиск по имени, email или тексту резюме")
):
    """
    Получить всех кандидатов по конкретной вакансии.
    
    - Требует авторизации
    - Только владелец вакансии может просматривать кандидатов
    """
    
    # Проверяем, что вакансия существует и принадлежит текущему работодателю
    vacancy = await session.get(Vacancy, vacancy_id)
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    if vacancy.hr_id != current_employer.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view candidates for your own vacancies"
        )
    
    # Базовый запрос для получения кандидатов по вакансии
    query = (
        select(
            User.user_id.label("candidate_id"),
            User.user_id,
            User.email,
            Profile.full_name.label("name"),
            Profile.phone,
            Resume.parsed_text.label("resume_text"),
            Resume.file_path.label("resume_file"),
            Resume.vacancy_id,
            Resume.upload_date.label("created_at")
        )
        .select_from(Resume)
        .join(User, User.user_id == Resume.candidate_id)
        .join(Profile, Profile.user_id == User.user_id, isouter=True)
        .where(Resume.vacancy_id == vacancy_id)
    )
    
    # Применяем фильтр по статусу (если передан)
    if status_filter:
        # TODO: Добавить поле статуса в модель Resume или создать отдельную таблицу
        # Пока используем временную логику
        pass
    
    # Применяем поиск (если передан)
    if search:
        search_filter = or_(
            Profile.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            Resume.parsed_text.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Сортируем по дате загрузки (новые сначала)
    query = query.order_by(Resume.upload_date.desc())
    
    result = await session.execute(query)
    candidates = result.all()
    
    # Преобразуем в список словарей
    candidate_list = []
    for candidate in candidates:
        candidate_dict = {
            "candidate_id": candidate.candidate_id,
            "user_id": candidate.user_id,
            "email": candidate.email,
            "name": candidate.name,
            "phone": candidate.phone,
            "resume_text": candidate.resume_text,
            "resume_file": candidate.resume_file,
            "vacancy_id": candidate.vacancy_id,
            "created_at": candidate.created_at,
            "status": "new"  # TODO: Реализовать систему статусов
        }
        candidate_list.append(candidate_dict)
    
    return candidate_list

# ============ ПОЛУЧИТЬ ДЕТАЛЬНУЮ ИНФОРМАЦИЮ О КАНДИДАТЕ ============

@router.get("/{candidate_id}", response_model=CandidateWithResume)
async def get_candidate_details(
    candidate_id: int,
    vacancy_id: Optional[int] = Query(None, description="ID вакансии для проверки прав доступа"),
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Получить детальную информацию о кандидате.
    
    - Требует авторизации
    - Только владелец вакансии может просматривать кандидатов
    """
    
    # Получаем резюме кандидата
    resume_query = select(Resume).where(Resume.candidate_id == candidate_id)
    
    if vacancy_id:
        # Если передан vacancy_id, проверяем что резюме относится к этой вакансии
        resume_query = resume_query.where(Resume.vacancy_id == vacancy_id)
        
        # Проверяем права доступа к вакансии
        vacancy = await session.get(Vacancy, vacancy_id)
        if not vacancy or vacancy.hr_id != current_employer.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    result = await session.execute(resume_query)
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Получаем информацию о пользователе
    user = await session.get(User, candidate_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Получаем профиль пользователя
    profile_result = await session.execute(
        select(Profile).where(Profile.user_id == candidate_id)
    )
    profile = profile_result.scalar_one_or_none()
    
    candidate_data = {
        "candidate_id": user.user_id,
        "user_id": user.user_id,
        "email": user.email,
        "name": profile.full_name if profile else None,
        "phone": profile.phone if profile else None,
        "resume_text": resume.parsed_text,
        "resume_file": resume.file_path,
        "vacancy_id": resume.vacancy_id,
        "status": "new",  # TODO: Реализовать систему статусов
        "created_at": resume.upload_date,
        "parsed_text": resume.parsed_text,
        "metadata_json": resume.metadata_json,
        "upload_date": resume.upload_date
    }
    
    return candidate_data


# ============ ОБНОВИТЬ СТАТУС КАНДИДАТА ============

@router.patch("/{candidate_id}/status", response_model=CandidateRead)
async def update_candidate_status(
    candidate_id: int,
    status_update: CandidateStatusUpdate,
    vacancy_id: int = Query(..., description="ID вакансии"),
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
):
    """
    Обновить статус кандидата.
    
    - Требует авторизации
    - Только владелец вакансии может обновлять статус кандидатов
    """
    
    # Проверяем права доступа к вакансии
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy or vacancy.hr_id != current_employer.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Проверяем, что кандидат откликался на эту вакансию
    resume_result = await session.execute(
        select(Resume).where(
            and_(
                Resume.candidate_id == candidate_id,
                Resume.vacancy_id == vacancy_id
            )
        )
    )
    resume = resume_result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found for this vacancy"
        )
    
    # TODO: Реализовать обновление статуса кандидата
    # Сейчас возвращаем базовую информацию
    
    user = await session.get(User, candidate_id)
    profile_result = await session.execute(
        select(Profile).where(Profile.user_id == candidate_id)
    )
    profile = profile_result.scalar_one_or_none()
    
    candidate_data = {
        "candidate_id": user.user_id,
        "user_id": user.user_id,
        "email": user.email,
        "name": profile.full_name if profile else None,
        "phone": profile.phone if profile else None,
        "resume_text": resume.parsed_text,
        "resume_file": resume.file_path,
        "vacancy_id": resume.vacancy_id,
        "status": status_update.status,
        "created_at": resume.upload_date
    }
    
    return candidate_data


# ============ ПОЛУЧИТЬ ВСЕХ КАНДИДАТОВ РАБОТОДАТЕЛЯ ============

@router.get("/", response_model=List[CandidateRead])
async def get_all_candidates(
    current_employer: User = Depends(get_current_employer),
    session: AsyncSession = Depends(db_helper.get_db),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    Получить всех кандидатов по всем вакансиям работодателя.
    
    - Требует авторизации
    - Возвращает кандидатов только по вакансиям текущего работодателя
    """
    
    # Получаем все вакансии работодателя
    vacancies_result = await session.execute(
        select(Vacancy.vacancy_id).where(Vacancy.hr_id == current_employer.user_id)
    )
    vacancy_ids = [vacancy[0] for vacancy in vacancies_result.all()]
    
    if not vacancy_ids:
        return []
    
    # Получаем кандидатов по всем вакансиям работодателя
    query = (
        select(
            User.user_id.label("candidate_id"),
            User.user_id,
            User.email,
            Profile.full_name.label("name"),
            Profile.phone,
            Resume.parsed_text.label("resume_text"),
            Resume.file_path.label("resume_file"),
            Resume.vacancy_id,
            Resume.upload_date.label("created_at")
        )
        .select_from(Resume)
        .join(User, User.user_id == Resume.candidate_id)
        .join(Profile, Profile.user_id == User.user_id, isouter=True)
        .where(Resume.vacancy_id.in_(vacancy_ids))
    )
    
    # Применяем поиск (если передан)
    if search:
        search_filter = or_(
            Profile.full_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            Resume.parsed_text.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Сортируем по дате загрузки (новые сначала)
    query = query.order_by(Resume.upload_date.desc())
    
    result = await session.execute(query)
    candidates = result.all()
    
    # Преобразуем в список словарей
    candidate_list = []
    for candidate in candidates:
        candidate_dict = {
            "candidate_id": candidate.candidate_id,
            "user_id": candidate.user_id,
            "email": candidate.email,
            "name": candidate.name,
            "phone": candidate.phone,
            "resume_text": candidate.resume_text,
            "resume_file": candidate.resume_file,
            "vacancy_id": candidate.vacancy_id,
            "created_at": candidate.created_at,
            "status": "new"  # TODO: Реализовать систему статусов
        }
        candidate_list.append(candidate_dict)
    
    return candidate_list