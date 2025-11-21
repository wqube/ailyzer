import os
from pathlib import Path
from dotenv import load_dotenv

# путь до candidate/backend/.env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# загружаем .env
load_dotenv(ENV_PATH)

# ключ OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")

# параметры интервью
COUNT_QUESTIONS = int(os.getenv("COUNT_QUESTIONS", 5))
PASSING_SCORE_INTERVIEW = int(os.getenv("PASSING_SCORE_INTERVIEW", 3))

# параметры резюме
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
PASSING_SCORE_RESUME = int(os.getenv("PASSING_SCORE_RESUME", 0))

# клиент OpenAI
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)
