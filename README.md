# Voicd - Text-to-Speech Web App

A Django web application for text-to-speech conversion using Google's **Gemini TTS** model. Supports 24+ languages with 30 natural-sounding voices and style instructions to control how the voice sounds.

## Features

- Web UI with text input, voice selection, and style instructions
- 30 voices (14 female, 16 male) grouped in a dropdown
- Style prompts to control tone (e.g. "Say cheerfully", "Speak in a whisper")
- In-browser audio playback with download option
- CLI tool for quick terminal usage
- Production-ready with gunicorn

## Quick Start

### 1. Clone & setup environment

```bash
git clone <your-repo-url>
cd Voicd-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key
DEBUG=True
```

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 3. Run the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

### 4. Use the app

1. Enter text in the textarea
2. Pick a voice from the dropdown (grouped by Female/Male)
3. Optionally add style instructions (e.g. "Say with excitement", "Read slowly")
4. Click **Generate Speech**
5. Listen to the audio in the browser
6. Click **Download WAV** to save the file

## CLI Usage

The `tts.py` script can also be used directly from the terminal:

```bash
# Basic usage (default voice: Kore)
python tts.py "Hello, how are you today?"

# Choose a voice
python tts.py "Good morning!" --voice Charon

# With style instructions
python tts.py "Have a wonderful day!" --voice Kore --style "Say cheerfully"

# Custom output file
python tts.py "Some text" --voice Aoede --output my_audio.wav

# List all available voices
python tts.py --list-voices
```

## Production Deployment

### 1. Set production environment variables

```
GEMINI_API_KEY=your_api_key
DJANGO_SECRET_KEY=your-random-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### 2. Collect static files

```bash
python manage.py collectstatic
```

### 3. Run with gunicorn

```bash
gunicorn voicd.wsgi:application --bind 0.0.0.0:8000
```

For production, put gunicorn behind a reverse proxy (nginx/caddy) that handles HTTPS and serves static/media files.

## Project Structure

```
Voicd-agent/
├── .env                        # Environment variables (not in git)
├── .env.example                # Template for .env
├── .gitignore
├── manage.py                   # Django management script
├── requirements.txt
├── tts.py                      # Core TTS logic (used by CLI and web)
├── voicd/                      # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── ttsapp/                     # Django app
│   ├── views.py                # index (form + generate) & download views
│   ├── urls.py
│   └── templates/ttsapp/
│       └── index.html          # Single-page UI
└── media/                      # Generated audio files (not in git)
```

## Available Voices

### Female (14)

Achernar, Aoede, Autonoe, Callirrhoe, Despina, Erinome, Gacrux, **Kore** (default), Laomedeia, Leda, Pulcherrima, Sulafat, Vindemiatrix, Zephyr

### Male (16)

Achird, Algenib, Algieba, Alnilam, Charon, Enceladus, Fenrir, Iapetus, Orus, Puck, Rasalgethi, Sadachbia, Sadaltager, Schedar, Umbriel, Zubenelgenubi

## Style Instruction Examples

| Style | Effect |
|-------|--------|
| `Say cheerfully` | Happy, upbeat tone |
| `Speak in a whisper` | Soft, quiet delivery |
| `Read slowly and dramatically` | Slower pace with emphasis |
| `Say with excitement and energy` | Enthusiastic, fast-paced |
| `Speak in a calm, soothing tone` | Relaxed, gentle |
| `Read like a news anchor` | Professional, clear |

## Output Format

WAV audio - PCM 24kHz, 16-bit, mono

## Requirements

- Python 3.10+
- Gemini API key
