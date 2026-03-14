"""Text-to-Speech using Google Cloud TTS API."""

import argparse
import base64
import json
import os
import tempfile

from dotenv import load_dotenv
from google.cloud import texttospeech
from google.oauth2 import service_account

load_dotenv()

# Default credentials path (for local development)
DEFAULT_CREDENTIALS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ornate-apricot-490206-j9-c5cb523a0a28.json",
)

# Curated Chirp3-HD voices (high quality, multilingual)
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
    """Extract short display name (e.g. 'en-US-Chirp3-HD-Kore' -> 'Kore')."""
    return voice.rsplit("-", 1)[-1]


def _get_client():
    """Create a TTS client using service account credentials.

    Supports two modes:
    - Local: reads JSON file from GOOGLE_APPLICATION_CREDENTIALS or default path
    - Vercel/Cloud: reads base64-encoded JSON from GCP_CREDENTIALS_B64 env var
    """
    # Mode 1: Base64-encoded credentials (for Vercel / serverless)
    creds_b64 = os.getenv("GCP_CREDENTIALS_B64")
    if creds_b64:
        creds_json = json.loads(base64.b64decode(creds_b64))
        credentials = service_account.Credentials.from_service_account_info(creds_json)
        return texttospeech.TextToSpeechClient(credentials=credentials)

    # Mode 2: JSON file path (for local development)
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", DEFAULT_CREDENTIALS)
    if not os.path.exists(creds_path):
        raise ValueError(
            f"GCP credentials file not found: {creds_path}\n"
            "Set GOOGLE_APPLICATION_CREDENTIALS or GCP_CREDENTIALS_B64 in your environment."
        )
    return texttospeech.TextToSpeechClient.from_service_account_json(creds_path)


def _language_from_voice(voice_name):
    """Extract language code from voice name (e.g. 'en-US-Chirp3-HD-Kore' -> 'en-US')."""
    parts = voice_name.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return "en-US"


def text_to_speech(text, output_file="output.wav", voice_name=None, style=""):
    """Convert text to speech using Google Cloud TTS.

    Args:
        text: Text to convert.
        output_file: Output WAV file path (None to skip saving).
        voice_name: A Google Cloud TTS voice name (e.g. 'en-US-Chirp3-HD-Kore').
        style: Optional style instructions (prepended to text).

    Returns:
        WAV audio bytes.
    """
    if voice_name is None:
        voice_name = DEFAULT_VOICE

    language_code = _language_from_voice(voice_name)
    client = _get_client()

    input_text = f"{style}: {text}" if style else text

    synthesis_input = texttospeech.SynthesisInput(text=input_text)

    voice_params = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=24000,
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    audio_data = response.audio_content

    if output_file:
        with open(output_file, "wb") as f:
            f.write(audio_data)
        print(f"Audio saved to {output_file} (voice: {voice_name})")

    return audio_data


def list_voices(language_code=None):
    """List available voices from Google Cloud TTS."""
    client = _get_client()
    response = client.list_voices(language_code=language_code)

    for voice in response.voices:
        langs = ", ".join(voice.language_codes)
        gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
        print(f"  {voice.name:40s} {langs:10s} {gender}")

    print(f"\nTotal: {len(response.voices)} voices")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text-to-Speech using Google Cloud TTS")
    parser.add_argument("text", nargs="?", help="Text to convert to speech")
    parser.add_argument("-v", "--voice", default=DEFAULT_VOICE, help=f"Voice name (default: {DEFAULT_VOICE})")
    parser.add_argument("-o", "--output", default="output.wav", help="Output WAV file")
    parser.add_argument("-s", "--style", default="", help="Style instructions")
    parser.add_argument("--list-voices", action="store_true", help="List all available voices")
    parser.add_argument("--language", default=None, help="Filter voices by language code (e.g. en-US, hi-IN)")
    args = parser.parse_args()

    if args.list_voices:
        list_voices(args.language)
    elif args.text:
        text_to_speech(args.text, args.output, args.voice, args.style)
    else:
        parser.print_help()
