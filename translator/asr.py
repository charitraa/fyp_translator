# translator/asr.py
import whisper
import os
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

class ASR:
    def __init__(self, model_size="medium"):
        use_gpu = bool(os.getenv("USE_GPU", "0"))  # Default CPU
        
        # Load model on GPU if available and requested
        if use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    self.device = "cuda"
                    print("✅ Using GPU for Whisper")
                else:
                    raise RuntimeError("CUDA not available")
            except Exception as e:
                print(f"⚠️ GPU failed ({e}), falling back to CPU")
                self.device = "cpu"
        else:
            self.device = "cpu"
            print("✅ Using CPU for Whisper (set USE_GPU=1 for GPU)")

        # Load Whisper model
        self.model = whisper.load_model(model_size, device=self.device)
        print(f"✅ Loaded Whisper ({model_size}) on {self.device.upper()}")

    def transcribe(self, audio_path: str, language: str = None) -> tuple:
        """
        Transcribes audio using OpenAI Whisper (non-faster version).
        """

        # Load audio
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        # Convert to Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        # Detect language
        if language is None:
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
        else:
            detected_lang = language

        # Decode
        options = whisper.DecodingOptions(language=language)
        result = whisper.decode(self.model, mel, options)

        text = result.text.strip()

        # Additional language detection using langdetect
        if text:
            try:
                text_lang = detect(text)
                if detected_lang == "en" and text_lang != "en":
                    print(f"⚠️ Override: {detected_lang} → {text_lang}")
                    detected_lang = text_lang
                elif detected_lang.startswith("ne") and text_lang == "en":
                    detected_lang = "en"
            except Exception as e:
                print(f"⚠️ Lang detect failed: {e}")

        return text, detected_lang
