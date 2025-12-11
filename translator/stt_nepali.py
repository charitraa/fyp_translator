# translator/stt_nepali.py
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

class NepaliSTT:
    def __init__(self):
        import torch
        torch.cuda.empty_cache()
        self.device = "cpu"
        model_name = "addy88/wav2vec2-nepali-stt"

        print("Loading Nepali STT model → addy88/wav2vec2-nepali-stt")
        self.processor = Wav2Vec2Processor.from_pretrained(model_name, cache_dir="models/nep_stt")
        self.model = Wav2Vec2ForCTC.from_pretrained(model_name, cache_dir="models/nep_stt").to(self.device)
        self.model.eval()

    def transcribe(self, audio_path):
        waveform, sr = torchaudio.load(audio_path)

        # Resample to 16kHz
        if sr != 16000:
            waveform = torchaudio.functional.resample(waveform, sr, 16000)

        # Preprocess
        input_values = self.processor(waveform.squeeze(), sampling_rate=16000, return_tensors="pt").input_values
        input_values = input_values.to(self.device)

        # Inference
        with torch.no_grad():
            logits = self.model(input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)

        # === THE MAGIC FIX IS HERE ===
        # Use decode() with skip_special_tokens=True and clean_up_tokenization_spaces=True
        transcription = self.processor.decode(predicted_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        
        # Extra cleanup (sometimes still has weird spaces)
        clean_text = transcription.strip()
        clean_text = clean_text.replace("  ", " ")  # double space → single

        print(f"Nepali STT → '{clean_text}'")
        return clean_text, "ne"


# Test it
if __name__ == "__main__":
    stt = NepaliSTT()
    result = stt.transcribe("output.wav")  # or any Nepali audio
    print(f"Final result: {result}")