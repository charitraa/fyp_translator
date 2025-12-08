# translator/asr.py

import whisper
import os
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

class ASR:
    def __init__(self, model_size="medium"):
        use_gpu = os.getenv("USE_GPU", "0") == "1"

        if use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    self.device = "cuda"
                    print("✅ Using GPU for Whisper")
                else:
                    raise RuntimeError("CUDA not available")
            except Exception as e:
                print(f"⚠️ GPU failed ({e}), using CPU")
                self.device = "cpu"
        else:
            print("✅ Using CPU for Whisper")
            self.device = "cpu"

        self.model = whisper.load_model(model_size, device=self.device)
        print(f"Loaded Whisper model ({model_size})")

    def transcribe(self, audio_path, language=None):
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        if language is None:
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
        else:
            detected_lang = language

        options = whisper.DecodingOptions(language=detected_lang)
        result = whisper.decode(self.model, mel, options)

        text = result.text.strip()

        # Additional fallback detection
        if text:
            try:
                lang2 = detect(text)
                detected_lang = lang2
            except:
                pass

        return text, detected_lang
