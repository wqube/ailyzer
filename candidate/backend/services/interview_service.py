import uuid
import json
import asyncio
from typing import Dict, Any
from dataclasses import dataclass, field

from ..core.config import client, COUNT_QUESTIONS, PASSING_SCORE_INTERVIEW
from ..core.utils import speak_text_local


@dataclass
class InterviewState:
    language: str = "en"
    topic: str = ""
    resume_text: str = ""
    story_messages: list = field(default_factory=list)
    scores: list = field(default_factory=list)
    finished: bool = False
    # Добавляем поле для хранения id вакансии
    application_id: int | None = None


# Временное хранение сессий (можно заменить на Redis)
sessions: Dict[str, InterviewState] = {}


async def start_interview_with_resume(state: InterviewState) -> str:
    """Создаёт system prompt и получает первый вопрос от GPT"""
    language_prompt = ""
    # ... (остается без изменений)

    system_prompt = (
        "Ты — строгий технический интервьюер.\n"
        "Задавай вопросы на основе резюме кандидата и **указанной темы/вакансии**.\n"
        "Формат: только текст вопроса, без нумерации, без Markdown, без жирного текста.\n\n"
        "После ответа кандидата ты должен оценить его по системе:\n"
        "1 = очень плохо, 2 = плохо, 3 = средне, 4 = хорошо, 5 = отлично.\n"
        "Ты должен выдавать JSON с оценкой: {\"score\": int, \"reasoning\": str}.\n"
        f"Вот резюме кандидата:\n{state.resume_text}\n\n"
        # Передаем подробное описание вакансии как тему
        f"Вот **вакансия (тема, уровень, описание, требования)** для кандидата:\n{state.topic}\n\n" 
        f"{language_prompt}\n\n"
        "Выдели направление и начни интервью с первого вопроса по ней."
        "Ты можешь задавать более углублённые вопросы исходя из предыдущих вопросов."
    )

    state.story_messages = [
        {"role": "system", "content": system_prompt},
    ]

    loop = asyncio.get_running_loop()

    def _call_openai_start():
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=state.story_messages
        )

    response = await loop.run_in_executor(None, _call_openai_start)
    first_question = response.choices[0].message.content.strip() # type: ignore

    # синтез речи (в фоне)
    asyncio.create_task(speak_text_local(first_question, state.language))
    state.story_messages.append({"role": "assistant", "content": first_question})

    return first_question


async def evaluate_answer(answer: str, state: InterviewState) -> dict:
    """Оценивает ответ кандидата и генерирует следующий вопрос"""
    state.story_messages.append({"role": "user", "content": answer})

    # Определяем, является ли это последним вопросом (если уже есть COUNT_QUESTIONS - 1 оценок)
    is_final_question = len(state.scores) >= (COUNT_QUESTIONS - 1)
    
    language_prompt = ""
    if state.language == "ru":
        language_prompt = "Отвечай на русском языке."
    elif state.language == "en":
        language_prompt = "Respond in English."

    # Составляем промпт и формат ответа LLM в зависимости от того, последний ли это вопрос
    if is_final_question:
        # Для последнего вопроса запрашиваем только оценку и причину
        system_instruction = (
            "Ты интервьюер. Это последний ответ кандидата. "
            f"Проанализируй историю общения:\n{state.story_messages}\n\n"
            "Оцени последний ответ кандидата строго в JSON: "
            "{\"score\": int, \"reasoning\": str}. "
            "НЕ ГЕНЕРИРУЙ ПОЛЕ \"next question\". "
            f"{language_prompt}"
        )
        required_response_format = {
            "type": "json_object",
            "schema": {
                "type": "object",
                "properties": {
                    "score": {"type": "integer"},
                    "reasoning": {"type": "string"},
                },
                "required": ["score", "reasoning"],
            },
        }
    else:
        # Для обычного вопроса запрашиваем следующий вопрос
        system_instruction = (
            "Ты интервьюер."
            f"Проанализируй историю общения:\n{state.story_messages}\n\n"
            "и составь следующий вопрос собеседования. "
            "Оцени последний ответ кандидата строго в JSON: "
            "{\"score\": int, \"reasoning\": str, \"next question\": str}. "
            f"{language_prompt}"
            "Не задавай вопросы, не пиши лишний текст."
        )
        # required_response_format = {"type": "json_object"} # Используем простой тип, т.к. схема сложнее


    loop = asyncio.get_running_loop()

    def _call_openai_eval():
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {"role": "user", "content": answer}
            ],
            response_format={"type": "json_object"}
        )

    eval_answer = await loop.run_in_executor(None, _call_openai_eval)

    try:
        evaluation = json.loads(eval_answer.choices[0].message.content) # type: ignore
    except Exception as e:
        # Fallback, если парсинг не удался
        evaluation = {
            "score": 1,
            "reasoning": f"Ошибка парсинга ответа AI: {str(e)}",
            "next question": "Поясните, пожалуйста, подробнее ваш ответ."
        }
    
    # Гарантируем, что поле next_question отсутствует, если это финальный вопрос
    if is_final_question:
        evaluation.pop("next question", None)
    
    next_question = evaluation.get("next question", "")
    if next_question:
        # Если вопрос сгенерирован (и это не финал), добавляем его в историю
        asyncio.create_task(speak_text_local(next_question, state.language))
        state.story_messages.append({"role": "assistant", "content": next_question})

    # Добавляем оценку за текущий (только что полученный) ответ
    state.scores.append(evaluation.get("score", 1))

    return evaluation


def create_session(state: InterviewState) -> str:
    session_id = str(uuid.uuid4())
    sessions[session_id] = state
    return session_id


def get_session(session_id: str) -> InterviewState | None:
    return sessions.get(session_id)