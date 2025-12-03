# translator/pipeline.py
import uuid
import os
from .asr import ASR
from .translator import LocalTranslator
from .tts import NepaliTTS

class SpeechTranslator:
    def __init__(self):
        self.asr = ASR(model_size="small")
        self.translator = LocalTranslator()

    def speech_to_speech(self, audio_file):
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        input_path = os.path.join(temp_dir, f"input_{uuid.uuid4().hex}.wav")

        with open(input_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # 1. ASR
        text, lang = self.asr.transcribe(input_path)
        if not text:
            return {"error": "No speech detected"}

        # 2. Direction
        direction = "en2ne" if lang.startswith("en") else "ne2en"

        # 3. Translate
        if direction == "en2ne":
            translated = self.translator.en_to_ne(text)
            tts_lang = "ne"
        else:
            translated = self.translator.ne_to_en(text)
            tts_lang = "en"

        # 4. TTS
        output_path = os.path.join(temp_dir, f"output_{uuid.uuid4().hex}.mp3")
        NepaliTTS(lang=tts_lang).synthesize(translated, output_path)

        return {
            "detected_language": lang,
            "recognized_text": text,
            "translation": translated,
            "output_audio": f"/{temp_dir}/{os.path.basename(output_path)}"
        }