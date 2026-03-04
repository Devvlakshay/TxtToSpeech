import os
import uuid

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import render

from tts import FEMALE_VOICES, MALE_VOICES, text_to_speech


def index(request):
    context = {
        "female_voices": FEMALE_VOICES,
        "male_voices": MALE_VOICES,
    }

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        voice = request.POST.get("voice", "Kore")
        style = request.POST.get("style", "").strip()
        context["text"] = text
        context["voice"] = voice
        context["style"] = style

        if not text:
            context["error"] = "Please enter some text."
            return render(request, "ttsapp/index.html", context)

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)

        try:
            text_to_speech(text, output_file=filepath, voice_name=voice, style=style)
            context["audio_url"] = settings.MEDIA_URL + filename
            context["filename"] = filename
        except Exception as e:
            context["error"] = str(e)

    return render(request, "ttsapp/index.html", context)


def download(request, filename):
    if not filename.endswith(".wav") or "/" in filename or "\\" in filename:
        raise Http404
    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(filepath):
        raise Http404
    return FileResponse(open(filepath, "rb"), as_attachment=True, filename=filename)
