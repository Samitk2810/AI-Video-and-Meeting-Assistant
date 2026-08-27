from dotenv import load_dotenv
load_dotenv()   # MUST be before any core/ imports

from utils.audio_processor import process_input
from core.transcriber import transcribe_all



source = "https://www.youtube.com/watch?v=UabBYexBD4k&t=34s"
language = "english"   # "english" → Whisper, "hinglish" → Sarvam



chunks = process_input(source)


transcript = transcribe_all(chunks, language=language)
print(transcript)