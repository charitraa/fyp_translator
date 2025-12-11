# translator/asr_selector.py
from .stt_english import EnglishSTT
from .stt_nepali import NepaliSTT

class ASRSelector:
    def __init__(self, mode=1):
        """
        mode = 1 → English model (NVIDIA Parakeet)
        mode = 2 → Nepali model (Wav2Vec2 Nepali)
        """
        self.mode = int(mode)

        if self.mode == 1:
            print("👉 Using English STT Model (Parakeet)")
            self.model = EnglishSTT()
        elif self.mode == 2:
            print("👉 Using Nepali STT Model (Wav2Vec2)")
            self.model = NepaliSTT()
        else:
            raise ValueError("Invalid mode! Use 1 for English, 2 for Nepali")

    def transcribe(self, audio_path):
        return self.model.transcribe(audio_path)
