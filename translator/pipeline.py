from .asr_selector import ASRSelector
from .translator import LocalTranslator
from .tts import NepaliTTS
import uuid, os
from django.conf import settings

class SpeechTranslator:
    def __init__(self, mode=1):
        """
        mode = 1 → English STT
        mode = 2 → Nepali STT
        """
        self.asr = ASRSelector(mode)
        self.translator = LocalTranslator()

    def speech_to_speech(self, audio_file):
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_audio")
        os.makedirs(temp_dir, exist_ok=True)

        # Save input
        input_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.wav")
        with open(input_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # STT
        text, detected_lang = self.asr.transcribe(input_path)

        if not text:
            return {"error": "No speech detected"}

        # Translation
        if detected_lang == "en":
            translated = self.translator.en_to_ne(text)
            out_lang = "ne"
        else:
            translated = self.translator.ne_to_en(text)
            out_lang = "en"

        # TTS
        output_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.mp3")
        NepaliTTS(out_lang).synthesize(translated, output_path)

        return {
            "recognized_text": text,
            "detected_language": detected_lang,
            "translation": translated,
            "audio_url": f"/media/temp_audio/{os.path.basename(output_path)}"
        }
