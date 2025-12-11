import nemo.collections.asr as nemo_asr
import torch

class EnglishSTT:
    def __init__(self):
        import torch
        torch.cuda.empty_cache()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_path = "models/eng_stt/parakeet-tdt-0.6b-v2.nemo"
        print("Loading English STT model (NeMo) locally...")
        self.model = nemo_asr.models.EncDecCTCModel.restore_from(model_path)
        self.model = self.model.to(self.device)

    
    def transcribe(self, audio_path):
        # This returns List[Hypothesis]
        hypotheses = self.model.transcribe([audio_path], batch_size=1)
        
        # Extract only the .text from the best hypothesis
        best_hypothesis = hypotheses[0]        # hypotheses is List[Hypothesis]
        if isinstance(best_hypothesis, list):
            best_hypothesis = best_hypothesis[0]  # sometimes nested
        
        clean_text = best_hypothesis.text if hasattr(best_hypothesis, 'text') else str(best_hypothesis)
        clean_text = clean_text.strip()
        
        print(f"English STT → '{clean_text}'")
        return clean_text, "en"


if __name__ == "__main__":
    stt = EnglishSTT()
    result = stt.transcribe("recorded.wav")
    print(f"result: {result}")