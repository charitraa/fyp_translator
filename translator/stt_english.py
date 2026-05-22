import os
import torch
import nemo.collections.asr as nemo_asr

class EnglishSTT:
    def __init__(self):
        torch.cuda.empty_cache()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Model info
        self.model_dir = "models/eng_stt"
        self.model_name = "parakeet-tdt-0.6b-v2.nemo"
        self.model_path = os.path.join(self.model_dir, self.model_name)

        os.makedirs(self.model_dir, exist_ok=True)

        # Load or download model
        if os.path.exists(self.model_path):
            print("✅ Loading English STT model from local storage...")
            self.model = nemo_asr.models.EncDecCTCModel.restore_from(self.model_path)
        else:
            print("⬇️ Model not found locally. Downloading from NeMo...")
            self.model = nemo_asr.models.EncDecCTCModel.from_pretrained(
                model_name="stt_en_parakeet_tdt_0.6b_v2"
            )
            print("💾 Saving model locally...")
            self.model.save_to(self.model_path)

        self.model = self.model.to(self.device)

    def transcribe(self, audio_path):
        hypotheses = self.model.transcribe([audio_path], batch_size=1)

        best_hypothesis = hypotheses[0]
        if isinstance(best_hypothesis, list):
            best_hypothesis = best_hypothesis[0]

        clean_text = (
            best_hypothesis.text
            if hasattr(best_hypothesis, "text")
            else str(best_hypothesis)
        ).strip()

        print(f"🎙 English STT → '{clean_text}'")
        return clean_text, "en"


if __name__ == "__main__":
    stt = EnglishSTT()
    result = stt.transcribe("recorded.wav")
    print(f"Result: {result}")

