"""Azure Cognitive Services TTS provider (REST API)."""

import os
import urllib.request

FEMALE_VOICES = [
    "hi-IN-AnanyaNeural",
    "hi-IN-AartiNeural",
    "hi-IN-KavyaNeural",
    "hi-IN-SwaraNeural",
]

MALE_VOICES = [
    "hi-IN-AaravNeural",
    "hi-IN-ArjunNeural",
    "hi-IN-KunalNeural",
    "hi-IN-MadhurNeural",
    "hi-IN-RehaanNeural",
]

ALL_VOICES = sorted(FEMALE_VOICES + MALE_VOICES)
DEFAULT_VOICE = "hi-IN-SwaraNeural"


def display_name(voice):
    """e.g. 'hi-IN-AaravNeural' -> 'Aarav'"""
    parts = voice.split("-")
    if len(parts) >= 3:
        return parts[2].replace("Neural", "")
    return voice


def _get_credentials():
    key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION", "eastus")
    if not key:
        raise ValueError(
            "Azure Speech key not found. "
            "Set AZURE_SPEECH_KEY in your environment."
        )
    return key, region


def _lang_from_voice(voice_name):
    parts = voice_name.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return "en-US"


def text_to_speech(text, output_file=None, voice_name=None, style=""):
    """Convert text to speech using Azure Cognitive Services REST API.

    Returns WAV audio bytes.
    """
    if voice_name is None:
        voice_name = DEFAULT_VOICE

    key, region = _get_credentials()
    lang = _lang_from_voice(voice_name)

    # Build SSML
    style_attr = f' style="{style}"' if style else ""
    ssml = (
        f'<speak version="1.0" xml:lang="{lang}">'
        f'<voice name="{voice_name}">'
        f"<mstts:express-as{style_attr}>" if style else ""
    )
    ssml = (
        f'<speak version="1.0" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="{lang}">'
        f'<voice name="{voice_name}">'
    )
    if style:
        ssml += f'<mstts:express-as style="{style}">{text}</mstts:express-as>'
    else:
        ssml += text
    ssml += "</voice></speak>"

    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"

    req = urllib.request.Request(
        url,
        data=ssml.encode("utf-8"),
        headers={
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
            "User-Agent": "Voicd-TTS",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            audio_data = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise ValueError(f"Azure TTS error ({e.code}): {body}") from e

    if output_file:
        with open(output_file, "wb") as f:
            f.write(audio_data)

    return audio_data
