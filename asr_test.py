from translator.asr import ASR

asr = ASR()
text, lang = asr.transcribe("recorded.wav")
print(f"Transcribed Text: {text}")
print(f"Detected Language: {lang}")