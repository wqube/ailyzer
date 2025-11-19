from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.interview_service import InterviewState, start_interview_with_resume, evaluate_answer, create_session, get_session, COUNT_QUESTIONS, PASSING_SCORE_INTERVIEW

router = APIRouter()

class StartInterviewReq(BaseModel):
    resume_text: str
    language: str = "en"
    topic: str = ""

class AnswerReq(BaseModel):
    session_id: str
    answer: str
    language: str = "en"

@router.post("/api/start_interview")
async def start_interview(req: StartInterviewReq):
    state = InterviewState(language=req.language)
    state.resume_text = req.resume_text
    state.topic = req.topic

    first_question = await start_interview_with_resume(state)
    session_id = create_session(state)
    return {"session_id": session_id, "question": first_question}

@router.post("/api/answer")
async def post_answer(req: AnswerReq):
    state = get_session(req.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    # обновить язык, если передан
    if req.language:
        state.language = req.language

    evaluation = await evaluate_answer(req.answer, state)

    finished = len(state.scores) >= COUNT_QUESTIONS
    passed = finished and (sum(state.scores) / len(state.scores) >= PASSING_SCORE_INTERVIEW)

    if finished:
        state.finished = True

    return {
        "reasoning": evaluation.get("reasoning"),
        "score": evaluation.get("score"),
        "next_question": evaluation.get("next question"),
        "finished": finished,
        "passed": passed
    }
