"""Hindi Text-to-Speech using Gemini 2.5 Pro TTS model."""

import argparse
import os
import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash-preview-tts"

FEMALE_VOICES = [
    "Achernar", "Aoede", "Autonoe", "Callirrhoe", "Despina",
    "Erinome", "Gacrux", "Kore", "Laomedeia", "Leda",
    "Pulcherrima", "Sulafat", "Vindemiatrix", "Zephyr",
]

MALE_VOICES = [
    "Achird", "Algenib", "Algieba", "Alnilam", "Charon",
    "Enceladus", "Fenrir", "Iapetus", "Orus", "Puck",
    "Rasalgethi", "Sadachbia", "Sadaltager", "Schedar",
    "Umbriel", "Zubenelgenubi",
]

ALL_VOICES = sorted(FEMALE_VOICES + MALE_VOICES)


def save_wave_file(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    """Save raw PCM data as a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def text_to_speech(text, output_file="output.wav", voice_name="Kore", style=""):
    """Convert text to speech using Gemini TTS.

    Args:
        text: Text to convert (supports Hindi and 24+ languages).
        output_file: Output WAV file path.
        voice_name: One of the 30 available Gemini TTS voices.
        style: Optional style instructions (e.g. "Say cheerfully", "Speak in a whisper").

    Returns:
        The output file path.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Set GEMINI_API_KEY in your .env file")

    if voice_name not in ALL_VOICES:
        raise ValueError(f"Unknown voice '{voice_name}'. Use --list-voices to see options.")

    client = genai.Client(api_key=api_key)

    contents = f"{style}: {text}" if style else text

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name,
                    )
                )
            ),
        ),
    )

    data = response.candidates[0].content.parts[0].inline_data.data

    if output_file:
        save_wave_file(output_file, data)
        print(f"Audio saved to {output_file} (voice: {voice_name})")

    return data


def list_voices():
    """Print all available voices."""
    print("Female Voices (14):")
    for v in FEMALE_VOICES:
        print(f"  - {v}")
    print(f"\nMale Voices (16):")
    for v in MALE_VOICES:
        print(f"  - {v}")
    print(f"\nTotal: {len(ALL_VOICES)} voices")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hindi TTS using Gemini 2.5 Pro")
    parser.add_argument("text", nargs="?", help="Text to convert to speech")
    parser.add_argument("-v", "--voice", default="Kore", help="Voice name (default: Kore)")
    parser.add_argument("-o", "--output", default="output.wav", help="Output WAV file")
    parser.add_argument("-s", "--style", default="", help="Style instructions (e.g. 'Say cheerfully')")
    parser.add_argument("--list-voices", action="store_true", help="List all available voices")
    args = parser.parse_args()

    if args.list_voices:
        list_voices()
    elif args.text:
        text_to_speech(args.text, args.output, args.voice, args.style)
    else:
        parser.print_help()
