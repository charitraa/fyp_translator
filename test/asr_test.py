from ..translator.stt_english import EnglishSTT


english = EnglishSTT()

result = english.transcribe("recorded.wav")
print(result)