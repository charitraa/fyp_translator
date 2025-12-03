import whisper
from translator.asr import ASR

asr = ASR()
text, lang = asr.transcribe("./output_ne.mp3")

# print the recognized text
print(text, lang)