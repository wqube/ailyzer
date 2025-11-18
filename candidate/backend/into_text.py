import os
import PyPDF2
from docx import Document
from striprtf.striprtf import rtf_to_text

def extract_text_from_file(filename: str) -> str:
    """
    Универсальная функция извлечения текста из .txt, .pdf, .docx и .rtf файлов.
    Возвращает строку текста.
    """
    _, file_extension = os.path.splitext(filename)
    file_extension = file_extension.lower()
    
    extractors = {
        '.txt': _extract_txt,
        '.pdf': _extract_pdf,
        '.docx': _extract_docx,
        '.rtf': _extract_rtf,
    }

    extractor = extractors.get(file_extension)
    if extractor is None:
        return f"Unsupported file format: {file_extension}"

    try:
        return extractor(filename)
    except Exception as e:
        return f"Ошибка при обработке файла {filename}: {str(e)}"


def _extract_txt(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def _extract_pdf(filename: str) -> str:
    text = ""
    with open(filename, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def _extract_docx(filename: str) -> str:
    doc = Document(filename)
    return '\n'.join(p.text for p in doc.paragraphs).strip()


def _extract_rtf(filename: str) -> str:
    """
    Извлекает текст из RTF через striprtf.
    """
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    return rtf_to_text(content).strip()
