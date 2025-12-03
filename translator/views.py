# translator/views.py

import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from translator import settings
from .translator import LocalTranslator
from .pipeline import SpeechTranslator
import threading

translator = LocalTranslator()
speech_instance = None
speech_lock = threading.Lock()

def get_speech_translator():
    global speech_instance
    if speech_instance is None:
        with speech_lock:
            if speech_instance is None:
                speech_instance = SpeechTranslator()
    return speech_instance

class TextTranslateView(APIView):
    def post(self, request):
        text = request.data.get("text", "")
        direction = request.data.get("direction", "en2ne")

        if direction == "en2ne":
            output = translator.en_to_ne(text)
        else:
            output = translator.ne_to_en(text)

        return Response({
            "input": text,
            "translation": output,
            "direction": direction
        })

class SpeechTranslateView(APIView):
    def post(self, request):
        audio = request.FILES.get("audio")
        if not audio:
            return Response({"error": "audio file missing"})

        try:
            worker = get_speech_translator()
            result = worker.speech_to_speech(audio)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)})

class SaveAudioView(APIView):
    def post(self, request):
        raw_data = request.body
        
        if not raw_data:
            return Response({"error": "No audio received"}, status=400)

        save_dir = os.path.join(settings.MEDIA_ROOT, "esp_audio")
        os.makedirs(save_dir, exist_ok=True)
    
        filename = f"{uuid.uuid4().hex}.wav"
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "wb") as f:
            f.write(raw_data)

        return Response({
            "status": "success",
            "saved_as": filename,
            "url": f"/media/esp_audio/{filename}"
        })
