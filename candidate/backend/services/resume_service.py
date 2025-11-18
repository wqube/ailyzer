import asyncio
import aiofiles
from pathlib import Path
from core.config import UPLOAD_FOLDER, PASSING_SCORE_RESUME
from into_text import extract_text_from_file
from resume_check import analyze_resume
from typing import Dict

async def save_upload_file(upload_file, destination: Path) -> Path:
    async with aiofiles.open(destination, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return destination

async def process_resume_file(upload_file, speciality: str, language: str):
    """
    Сохраняет файл, запускает анализ резюме (в threadpool) и возвращает результат.
    """
    filename = Path(upload_file.filename).name
    dest = UPLOAD_FOLDER / filename

    await save_upload_file(upload_file, dest)

    loop = asyncio.get_running_loop()
    # Запускаем тяжелый CPU/IO-bound анализ в threadpool
    result = await loop.run_in_executor(None, analyze_resume, str(dest), PASSING_SCORE_RESUME, speciality)

    # извлечь текст — тоже синхронная функция, вызвать в executor
    resume_text = await loop.run_in_executor(None, extract_text_from_file, str(dest))
    result['resume_text'] = resume_text
    result['language'] = language
    result['accepted'] = result.get('passed', False)
    return result
