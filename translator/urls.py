# translator/urls.py
from django.conf import settings
from django.urls import path
from .views import TextTranslateView, SpeechTranslateView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("translate/text/", TextTranslateView.as_view(), name="text-translate"),
    path("translate/speech/", SpeechTranslateView.as_view(), name="speech-translate"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
