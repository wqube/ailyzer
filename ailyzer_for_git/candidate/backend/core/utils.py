import os
from pathlib import Path
from typing import Set
import asyncio
import functools
import sounddevice as sd
from TTS.api import TTS

ALLOWED_EXTENSIONS: Set[str] = {'pdf', 'doc', 'docx', 'txt', 'rtf'}

# TTS init (shared)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def speak_text_local(text: str, language: str = "en"):
    """
    Выполняет синтез и воспроизведение в отдельном потоке (не блокирует event loop).
    Если ты не хочешь воспроизводить звук на сервере — просто не вызывать эту функцию.
    """
    if not language:
        language = "en"

    loop = asyncio.get_running_loop()
    # сгенерировать аудиобайт в потоковом режиме
    def _synth_and_play():
        audio = tts.tts(
            text=text,
            speaker="Claribel Dervla",
            language=language
        )
        sd.play(audio, samplerate=tts.synthesizer.output_sample_rate)
        sd.wait()
    await loop.run_in_executor(None, _synth_and_play)
