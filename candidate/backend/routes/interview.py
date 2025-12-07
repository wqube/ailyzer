from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import update

from shared.db.models import Application
from ..services.interview_service import InterviewState, start_interview_with_resume, evaluate_answer, create_session, get_session, COUNT_QUESTIONS, PASSING_SCORE_INTERVIEW
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db.session import db_helper

router = APIRouter()

# Добавляем id вакансии на старт интервью
class StartInterviewReq(BaseModel):
    resume_text: str
    language: str = "en"
    topic: str = ""
    application_id: Optional[int] = None  # Теперь мы ждем ID заявки

class AnswerReq(BaseModel):
    session_id: str
    answer: str
    language: str = "en"

@router.post("/api/start_interview")
async def start_interview(req: StartInterviewReq):
    """
    Инициализация сессии интервью.
    Фронтенд должен передать application_id, полученный при создании кандидата.
    """
    state = InterviewState(language=req.language)
    state.resume_text = req.resume_text
    state.topic = req.topic

    # Сохраняем id вакансии и состояние в сессии
    state.application_id = req.application_id

    first_question = await start_interview_with_resume(state)
    session_id = create_session(state)

    return {"session_id": session_id, "question": first_question}

@router.post("/api/answer")
async def post_answer(
    req: AnswerReq,
    # Добавляем зависимость от БД, чтобы сохранить результат
    session: AsyncSession = Depends(db_helper.get_db)
    ):
    # Получаем состояние из памяти
    state = get_session(req.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    # обновить язык, если передан
    if req.language:
        state.language = req.language

    # Оцениваем язык через LLM
    evaluation = await evaluate_answer(req.answer, state)

    # Проверяем условия завершения
    finished = len(state.scores) >= COUNT_QUESTIONS

    # Считаем средний балл
    avg_score = 0.0
    if state.scores:
        avg_score = sum(state.scores) / len(state.scores)

    passed = finished and (sum(state.scores) / len(state.scores) >= PASSING_SCORE_INTERVIEW)

    if finished:
        state.finished = True

        # Если интервью завершилось, сохраняем средний балл в БД
        if state.application_id:
            try:
                print(f"Saving results for App ID {state.application_id}...")
                new_status = "interview_passed" if passed else "interview_failed"
                
                # SQL Update запрос
                stmt = (
                    update(Application)
                    .where(Application.application_id == state.application_id)
                    .values(
                        interview_score=avg_score,
                        status=new_status
                    )
                )
                await session.execute(stmt)
                await session.commit()
                print(f"✓ Application {state.application_id} updated. Score: {avg_score}, Status: {new_status}")
            
            except Exception as e:
                print(f"❌ Error saving interview results to DB: {e}")
                # Мы не прерываем ответ фронтенду, даже если база не ответила,
                # чтобы пользователь увидел результат "Вы прошли/не прошли".
        else:
            print("⚠ Warning: Interview finished but no application_id in state.")
        # --------------------------------

    return {
        "reasoning": evaluation.get("reasoning"),
        "score": evaluation.get("score"),
        "next_question": evaluation.get("next question"),
        "finished": finished,
        "passed": passed,
        "final_score": avg_score if finished else None # Удобно вернуть на фронт
    }
