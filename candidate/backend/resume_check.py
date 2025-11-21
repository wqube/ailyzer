import os
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from .into_text import extract_text_from_file

# модель может загружаться при импорте
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def analyze_resume(file_path, passing_score, speciality):
    text = extract_text_from_file(file_path)

    job_embedding = model.encode(speciality, convert_to_tensor=True)
    resume_embedding = model.encode(text, convert_to_tensor=True)

    similarity = util.cos_sim(job_embedding, resume_embedding).item()
    rating = round(similarity * 100, 2)
    passed = rating > passing_score

    data = {
        'success': True,
        'passed': passed,
        'score': rating,
        'speciality': speciality,
        'candidate_name': os.path.basename(file_path),
        'details': text[:200],
        'analysis_date': datetime.now().isoformat()
    }
    print(data)
    return data
