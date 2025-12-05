# translator/tts.py
import os
from gtts import gTTS

class NepaliTTS:
    def __init__(self, lang="ne"):
        self.lang = lang

    def synthesize(self, text: str, output_path: str):
        tts = gTTS(text=text, lang=self.lang)
        tts.save(output_path)
        # Boost volume by +15 dB (LM386 needs it!)
        os.system(f"ffmpeg -y -i \"{output_path}\" -filter:a \"volume=15\" \"{output_path}\" > /dev/null 2>&1")