# translator/stt_nepali.py

import os
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC


class NepaliSTT:
    def __init__(self):
        torch.cuda.empty_cache()
        self.device = "cpu"  # wav2vec2-nepali is CPU-friendly

        self.model_name = "addy88/wav2vec2-nepali-stt"
        self.cache_dir = "models/nep_stt"

        os.makedirs(self.cache_dir, exist_ok=True)

        print("🔍 Loading Nepali STT model (auto-download if missing)...")

        # HuggingFace handles:
        # - download if missing
        # - reuse if exists
        self.processor = Wav2Vec2Processor.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir
        )

        self.model = Wav2Vec2ForCTC.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir
        ).to(self.device)

        self.model.eval()

        print("✅ Nepali STT model ready")

    def transcribe(self, audio_path):
        waveform, sr = torchaudio.load(audio_path)

        # Resample to 16kHz (required by wav2vec2)
        if sr != 16000:
            waveform = torchaudio.functional.resample(waveform, sr, 16000)

        input_values = self.processor(
            waveform.squeeze(),
            sampling_rate=16000,
            return_tensors="pt"
        ).input_values.to(self.device)

        with torch.no_grad():
            logits = self.model(input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)

        transcription = self.processor.decode(
            predicted_ids[0],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )

        clean_text = transcription.strip().replace("  ", " ")

        print(f"🎙 Nepali STT → '{clean_text}'")
        return clean_text, "ne"


# Test
if __name__ == "__main__":
    stt = NepaliSTT()
    result = stt.transcribe("output.wav")
    print(f"Final result: {result}")
