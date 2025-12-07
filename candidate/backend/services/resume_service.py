import asyncio
import aiofiles
from pathlib import Path
from typing import Dict

# Вам нужно убедиться, что эти импорты верны в вашей структуре проекта
from ..core.config import UPLOAD_FOLDER, PASSING_SCORE_RESUME
from ..into_text import extract_text_from_file
from ..resume_check import analyze_resume


async def save_file_content(content: bytes, destination: Path) -> Path:
    """
    Сохраняет содержимое файла (байты) в указанное место.
    Заменяет старую save_upload_file.
    """
    async with aiofiles.open(destination, 'wb') as out_file:
        await out_file.write(content)
    return destination


async def process_resume_file(
    file_content: bytes,    # Теперь принимает содержимое файла в виде байтов
    filename: str,          # Теперь принимает имя файла в виде строки
    speciality: str, 
    language: str
) -> Dict:
    """
    Обрабатывает содержимое резюме.
    """
    print(">>> process_resume_file called")

    # Используем переданное имя файла
    safe_filename = Path(filename).name
    dest = UPLOAD_FOLDER / safe_filename

    print(f">>> Saving to temporary path: {dest}")
    # Используем новую функцию для сохранения байтов
    await save_file_content(file_content, dest)
    print(">>> File saved to disk for processing")

    loop = asyncio.get_running_loop()

    # ВАЖНО: speciality (полное описание вакансии) передается в analyze_resume
    print(">>> Running analyze_resume...")
    # analyze_resume и extract_text_from_file работают с путем к локальному файлу
    result = await loop.run_in_executor(None, analyze_resume, str(dest), PASSING_SCORE_RESUME, speciality)
    print(f">>> analyze_resume result: {result}")

    print(">>> Extracting text...")
    resume_text = await loop.run_in_executor(None, extract_text_from_file, str(dest))
    print(f">>> resume_text length: {len(resume_text)}")

    # Очистка: удаление временного файла после обработки
    try:
        if dest.exists():
            dest.unlink()
            print(">>> Temporary file removed.")
    except Exception as e:
        # Логируем ошибку, но не прерываем работу, так как анализ завершен
        print(f"Warning: Could not delete temporary file {dest}. Error: {e}")

    result['resume_text'] = resume_text
    result['language'] = language
    result['accepted'] = result.get('passed', False)
    # Возвращаем результат, включая resume_text для последующего собеседования
    return result