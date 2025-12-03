from gtts import gTTS
import os

class NepaliTTS:
    def __init__(self, lang='ne'):
        self.lang = lang

    def synthesize(self, text, output_path):
        tts = gTTS(text=text, lang=self.lang)
        tts.save(output_path)
        print(f"✅ Synthesized speech saved to {output_path}")



# Example usage:
if __name__ == "__main__":
    tts = NepaliTTS(lang='ne')
    tts.synthesize("नमस्ते, तपाईंलाई कस्तो छ?", "output_ne.mp3")