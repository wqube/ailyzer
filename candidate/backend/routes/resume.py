from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..core.utils import allowed_file
from ..services.resume_service import process_resume_file

router = APIRouter()

@router.post("/api/upload-resume")  
async def upload_resume(
    fullname: str = Form(...),
    interview_topic: str = Form(...),
    select_language: str = Form("ru"),
    resume: UploadFile = File(...)
):
    print(f"Received resume: {resume.filename}")
    print(f"Fullname: {fullname}")
    print(f"Topic: {interview_topic}")
    print(f"Language: {select_language}")
    
    if not resume:
        raise HTTPException(status_code=400, detail="Файл не найден")
    if resume.filename == "":
        raise HTTPException(status_code=400, detail="Файл не выбран")
    if not allowed_file(resume.filename):
        raise HTTPException(status_code=400, detail="Недопустимый формат файла")

    try:
        result = await process_resume_file(resume, interview_topic, select_language)
        print(f"Analysis result: {result}")
        return result
    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки резюме: {str(e)}")