"""Google Cloud TTS provider."""

import base64
import json
import os

from google.cloud import texttospeech
from google.oauth2 import service_account

DEFAULT_CREDENTIALS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ornate-apricot-490206-j9-c5cb523a0a28.json",
)

FEMALE_VOICES = [
    "en-US-Chirp3-HD-Achernar",
    "en-US-Chirp3-HD-Aoede",
    "en-US-Chirp3-HD-Autonoe",
    "en-US-Chirp3-HD-Callirrhoe",
    "en-US-Chirp3-HD-Despina",
    "en-US-Chirp3-HD-Erinome",
    "en-US-Chirp3-HD-Gacrux",
    "en-US-Chirp3-HD-Kore",
    "en-US-Chirp3-HD-Laomedeia",
    "en-US-Chirp3-HD-Leda",
    "en-US-Chirp3-HD-Pulcherrima",
    "en-US-Chirp3-HD-Sulafat",
    "en-US-Chirp3-HD-Vindemiatrix",
    "en-US-Chirp3-HD-Zephyr",
]

MALE_VOICES = [
    "en-US-Chirp3-HD-Achird",
    "en-US-Chirp3-HD-Algenib",
    "en-US-Chirp3-HD-Algieba",
    "en-US-Chirp3-HD-Alnilam",
    "en-US-Chirp3-HD-Charon",
    "en-US-Chirp3-HD-Enceladus",
    "en-US-Chirp3-HD-Fenrir",
    "en-US-Chirp3-HD-Iapetus",
    "en-US-Chirp3-HD-Orus",
    "en-US-Chirp3-HD-Puck",
    "en-US-Chirp3-HD-Rasalgethi",
    "en-US-Chirp3-HD-Sadachbia",
    "en-US-Chirp3-HD-Sadaltager",
    "en-US-Chirp3-HD-Schedar",
    "en-US-Chirp3-HD-Umbriel",
    "en-US-Chirp3-HD-Zubenelgenubi",
]

ALL_VOICES = sorted(FEMALE_VOICES + MALE_VOICES)
DEFAULT_VOICE = "en-US-Chirp3-HD-Kore"


def display_name(voice):
    return voice.rsplit("-", 1)[-1]


def _get_client():
    creds_b64 = os.getenv("GCP_CREDENTIALS_B64")
    if creds_b64:
        creds_json = json.loads(base64.b64decode(creds_b64))
        credentials = service_account.Credentials.from_service_account_info(creds_json)
        return texttospeech.TextToSpeechClient(credentials=credentials)

    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", DEFAULT_CREDENTIALS)
    if not os.path.exists(creds_path):
        raise ValueError(
            "GCP credentials not found. "
            "Set GOOGLE_APPLICATION_CREDENTIALS or GCP_CREDENTIALS_B64."
        )
    return texttospeech.TextToSpeechClient.from_service_account_json(creds_path)


def _language_from_voice(voice_name):
    parts = voice_name.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return "en-US"


def text_to_speech(text, output_file=None, voice_name=None, style=""):
    if voice_name is None:
        voice_name = DEFAULT_VOICE

    language_code = _language_from_voice(voice_name)
    client = _get_client()

    input_text = f"{style}: {text}" if style else text

    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=input_text),
        voice=texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        ),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=24000,
        ),
    )

    audio_data = response.audio_content

    if output_file:
        with open(output_file, "wb") as f:
            f.write(audio_data)

    return audio_data
