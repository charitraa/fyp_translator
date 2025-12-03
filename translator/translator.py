# translator/translator.py

from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM,
    MBart50TokenizerFast, MBartForConditionalGeneration, pipeline
)
import torch

class LocalTranslator:
    def __init__(self, model_dir="models"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Translator using:", self.device)

        self.mbart_tokenizer = MBart50TokenizerFast.from_pretrained(f"{model_dir}/ne2en")
        self.mbart_model = MBartForConditionalGeneration.from_pretrained(
            f"{model_dir}/ne2en"
        ).to(self.device)

        self.nllb_tokenizer = AutoTokenizer.from_pretrained(f"{model_dir}/en2ne")
        self.nllb_model = AutoModelForSeq2SeqLM.from_pretrained(f"{model_dir}/en2ne")

    # Nepali → English
    def ne_to_en(self, text):
        self.mbart_tokenizer.src_lang = "ne_NP"
        inputs = self.mbart_tokenizer(text, return_tensors="pt").to(self.device)
        generated_ids = self.mbart_model.generate(
            **inputs,
            forced_bos_token_id=self.mbart_tokenizer.lang_code_to_id["en_XX"]
        )
        return self.mbart_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # English → Nepali
    def en_to_ne(self, text):
        translator = pipeline(
            "translation",
            model=self.nllb_model,
            tokenizer=self.nllb_tokenizer,
            src_lang="eng_Latn",
            tgt_lang="npi_Deva"
        )
        out = translator(text)
        return out[0]["translation_text"]
