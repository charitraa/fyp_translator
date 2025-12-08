import uuid
import os
from django.conf import settings
from .asr import ASR
from .translator import LocalTranslator
from .tts import NepaliTTS

class SpeechTranslator:
    def __init__(self):
        self.asr = ASR(model_size="medium")
        self.translator = LocalTranslator()

    def speech_to_speech(self, audio_file):
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_audio")
        os.makedirs(temp_dir, exist_ok=True)

        # Save uploaded audio
        input_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.wav")
        with open(input_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # Step 1: Speech → Text
        text, detected_lang = self.asr.transcribe(input_path)

        if not text:
            return {"error": "No speech detected"}

        # Step 2: Decide direction
        if detected_lang.lower().startswith("en"):
            translated = self.translator.en_to_ne(text)
            tts_lang = "ne"
        else:
            translated = self.translator.ne_to_en(text)
            tts_lang = "en"

        # Step 3: Text → Speech
        output_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.mp3")
        NepaliTTS(tts_lang).synthesize(translated, output_path)

        return {
            "recognized_text": text,
            "detected_language": detected_lang,
            "translation": translated,
            "audio_url": f"/media/temp_audio/{os.path.basename(output_path)}"
        }
