from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, MBart50TokenizerFast, MBartForConditionalGeneration, pipeline
import torch

class LocalTranslator:
    def __init__(self, model_dir="models"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        mbart_path = f"{model_dir}/ne2en"
        self.mbart_tokenizer = MBart50TokenizerFast.from_pretrained(mbart_path)
        self.mbart_model = MBartForConditionalGeneration.from_pretrained(mbart_path).to(self.device)

        nllb_path = f"{model_dir}/en2ne"
        self.nllb_tokenizer = AutoTokenizer.from_pretrained(nllb_path )
        self.nllb_model = AutoModelForSeq2SeqLM.from_pretrained(nllb_path)

    def ne_to_en(self, text: str) -> str:
        self.mbart_tokenizer.src_lang = "ne_NP"
        inputs = self.mbart_tokenizer(text, return_tensors="pt").to(self.device)
        generated_ids = self.mbart_model.generate(**inputs, forced_bos_token_id=self.mbart_tokenizer.lang_code_to_id["en_XX"])
        return self.mbart_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    def en_to_ne(self, text: str) -> str:
        translator = pipeline(
        "translation",
        model=self.nllb_model,
        tokenizer=self.nllb_tokenizer,
        src_lang="eng_Latn",
        tgt_lang="npi_Deva",
        max_length=200
    )   
        result = translator(text)
        return result[0]["translation_text"]

