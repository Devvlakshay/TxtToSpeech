# Voicd - Text-to-Speech Web App

A text-to-speech web application using Google's **Gemini TTS** model. Supports 24+ languages with 30 natural-sounding voices and style instructions to control tone and delivery.

Deploy anywhere: **Streamlit Cloud**, **Vercel**, or **self-hosted with Django**.

## Features

- 30 voices (14 female, 16 male)
- Style prompts to control tone (e.g. "Say cheerfully", "Speak in a whisper")
- In-browser audio playback with download
- Three deployment options: Streamlit Cloud, Vercel, Django
- CLI tool for terminal usage

## Quick Start (Local)

```bash
git clone <your-repo-url>
cd Voicd-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey):

```env
GEMINI_API_KEY=your_actual_api_key
DEBUG=True
```

Then pick how you want to run it:

```bash
# Option 1: Streamlit (simplest)
streamlit run streamlit_app.py

# Option 2: Django
python manage.py runserver

# Option 3: Flask (same as Vercel, locally)
flask --app api/index.py run
```

## Deploy to Streamlit Cloud

1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select your repo, branch, and set main file to `streamlit_app.py`
4. Add secret in Streamlit dashboard: `GEMINI_API_KEY = "your_key"`
5. Deploy

## Deploy to Vercel

1. Push your repo to GitHub
2. Go to [vercel.com](https://vercel.com) and import the repo
3. Add environment variable: `GEMINI_API_KEY`
4. Deploy — Vercel auto-detects `vercel.json` config

> **Note:** Vercel serverless functions have a 10s timeout on the free plan. Short text works fine; long text may timeout. Upgrade to Pro for 60s timeout.

## Self-Hosted (Django + Gunicorn)

```bash
# Set production env vars
export DJANGO_SECRET_KEY=your-random-secret
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com
export CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Collect static files and run
python manage.py collectstatic --noinput
gunicorn voicd.wsgi:application --bind 0.0.0.0:8000
```

Put gunicorn behind nginx/caddy for HTTPS and static file serving.

## CLI Usage

```bash
# Basic usage (default voice: Kore)
python tts.py "Hello, how are you today?"

# Choose a voice
python tts.py "Good morning!" --voice Charon

# With style instructions
python tts.py "Have a wonderful day!" --style "Say cheerfully"

# Custom output file
python tts.py "Some text" --voice Aoede --output my_audio.wav

# List all available voices
python tts.py --list-voices
```

## Project Structure

```text
Voicd-agent/
├── .env.example              # Template for env vars
├── .gitignore
├── requirements.txt
├── tts.py                    # Core TTS logic (shared by all frontends)
│
├── streamlit_app.py          # Streamlit Cloud frontend
│
├── api/                      # Vercel serverless backend
│   └── index.py              #   Flask API (generate + voices endpoints)
├── public/
│   └── index.html            #   Vercel static frontend
├── vercel.json               #   Vercel config
│
├── manage.py                 # Django management
├── voicd/                    # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── ttsapp/                   # Django app
    ├── views.py
    ├── urls.py
    └── templates/ttsapp/
        └── index.html
```

## Available Voices

**Female (14):** Achernar, Aoede, Autonoe, Callirrhoe, Despina, Erinome, Gacrux, **Kore** (default), Laomedeia, Leda, Pulcherrima, Sulafat, Vindemiatrix, Zephyr

**Male (16):** Achird, Algenib, Algieba, Alnilam, Charon, Enceladus, Fenrir, Iapetus, Orus, Puck, Rasalgethi, Sadachbia, Sadaltager, Schedar, Umbriel, Zubenelgenubi

## Style Examples

| Style                           | Effect                        |
| ------------------------------- | ----------------------------- |
| `Say cheerfully`                | Happy, upbeat tone            |
| `Speak in a whisper`            | Soft, quiet delivery          |
| `Read slowly and dramatically`  | Slower pace with emphasis     |
| `Say with excitement and energy` | Enthusiastic, fast-paced     |
| `Speak in a calm, soothing tone` | Relaxed, gentle             |
| `Read like a news anchor`       | Professional, clear           |

## Requirements

- Python 3.10+
- Gemini API key
