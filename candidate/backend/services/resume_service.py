import asyncio
import aiofiles
from pathlib import Path
from ..core.config import UPLOAD_FOLDER, PASSING_SCORE_RESUME
from ..into_text import extract_text_from_file
from ..resume_check import analyze_resume
from typing import Dict

async def save_upload_file(upload_file, destination: Path) -> Path:
    async with aiofiles.open(destination, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return destination

async def process_resume_file(upload_file, speciality: str, language: str): # speciality - теперь тема вакансии
    print(">>> process_resume_file called")

    filename = Path(upload_file.filename).name
    dest = UPLOAD_FOLDER / filename

    print(f">>> Saving to: {dest}")
    await save_upload_file(upload_file, dest)
    print(">>> File saved")

    loop = asyncio.get_running_loop()

    # ВАЖНО: speciality (полное описание вакансии) передается в analyze_resume
    print(">>> Running analyze_resume...")
    result = await loop.run_in_executor(None, analyze_resume, str(dest), PASSING_SCORE_RESUME, speciality)
    print(f">>> analyze_resume result: {result}")

    print(">>> Extracting text...")
    resume_text = await loop.run_in_executor(None, extract_text_from_file, str(dest))
    print(f">>> resume_text length: {len(resume_text)}")

    result['resume_text'] = resume_text
    result['language'] = language
    result['accepted'] = result.get('passed', False)
    # Возвращаем результат, включая resume_text для последующего собеседования
    return result