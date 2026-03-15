"""Unified Text-to-Speech interface supporting Google Cloud and Azure providers."""

import argparse
import os

from dotenv import load_dotenv

load_dotenv()

# Provider modules (lazy imports to avoid requiring both SDKs)
PROVIDERS = {
    "google": "tts_google",
    "azure": "tts_azure",
}


def _get_provider(name):
    import importlib
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider '{name}'. Choose from: {list(PROVIDERS.keys())}")
    return importlib.import_module(PROVIDERS[name])


def get_voices(provider="google"):
    """Return (female_voices, male_voices, default_voice) for a provider."""
    mod = _get_provider(provider)
    return mod.FEMALE_VOICES, mod.MALE_VOICES, mod.DEFAULT_VOICE


def get_all_voices(provider="google"):
    mod = _get_provider(provider)
    return mod.ALL_VOICES


def display_name(voice, provider="google"):
    mod = _get_provider(provider)
    return mod.display_name(voice)


def text_to_speech(text, output_file=None, voice_name=None, style="", provider="google"):
    """Convert text to speech.

    Args:
        text: Text to convert.
        output_file: Output WAV file path (None to skip saving).
        voice_name: Voice name (provider-specific).
        style: Optional style instructions.
        provider: 'google' or 'azure'.

    Returns:
        WAV audio bytes.
    """
    mod = _get_provider(provider)
    return mod.text_to_speech(text, output_file=output_file, voice_name=voice_name, style=style)


# --- Backwards compatibility exports (default to google) ---
import tts_google

FEMALE_VOICES = tts_google.FEMALE_VOICES
MALE_VOICES = tts_google.MALE_VOICES
ALL_VOICES = tts_google.ALL_VOICES
DEFAULT_VOICE = tts_google.DEFAULT_VOICE


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text-to-Speech (Google Cloud / Azure)")
    parser.add_argument("text", nargs="?", help="Text to convert to speech")
    parser.add_argument("-p", "--provider", default="google", choices=["google", "azure"])
    parser.add_argument("-v", "--voice", default=None, help="Voice name")
    parser.add_argument("-o", "--output", default="output.wav", help="Output WAV file")
    parser.add_argument("-s", "--style", default="", help="Style instructions")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    args = parser.parse_args()

    if args.list_voices:
        female, male, default = get_voices(args.provider)
        print(f"Provider: {args.provider}\n")
        print("Female voices:")
        for v in female:
            tag = " (default)" if v == default else ""
            print(f"  {v:45s} {display_name(v, args.provider)}{tag}")
        print("\nMale voices:")
        for v in male:
            tag = " (default)" if v == default else ""
            print(f"  {v:45s} {display_name(v, args.provider)}{tag}")
    elif args.text:
        data = text_to_speech(args.text, args.output, args.voice, args.style, args.provider)
        print(f"Audio saved to {args.output} ({args.provider}, {len(data)} bytes)")
    else:
        parser.print_help()
