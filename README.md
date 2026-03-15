# Voicd - Text-to-Speech Web App

A text-to-speech web application supporting **Google Cloud TTS** and **Azure Cognitive Services TTS**. Switch between providers with a single click. Supports 24+ languages with high-quality neural voices.

Deploy anywhere: **Streamlit Cloud**, **Vercel**, **Django**, or run as a **standalone API server**.

## Features

- Two TTS providers: Google Cloud (Chirp3-HD) and Azure (Neural voices)
- Provider switcher in the UI
- Hindi and English voices out of the box
- Style instructions to control tone
- Standalone REST API with auto-save to `ttsGoogle/` and `ttsAzure/` folders
- CLI tool for terminal usage
- Four deployment options: Streamlit, Vercel, Django, API server

## Quick Start (Local)

```bash
git clone https://github.com/Devvlakshay/TxtToSpeech.git
cd TxtToSpeech
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Google Cloud TTS (service account JSON or base64)
GCP_CREDENTIALS_B64=your_base64_encoded_service_account_json
# Or point to the JSON file directly:
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Azure TTS
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=eastus

DEBUG=True
```

Then pick how you want to run it:

```bash
# Option 1: Django (web UI with provider tabs)
python3 manage.py runserver

# Option 2: Standalone API server (saves files to ttsGoogle/ & ttsAzure/)
python3 api/server.py

# Option 3: Streamlit
streamlit run streamlit_app.py

# Option 4: Flask (same as Vercel, locally)
flask --app api/index.py run
```

## REST API

Start the API server:

```bash
python3 api/server.py
# Runs on http://localhost:5000
```

### Endpoints

#### Generate Audio

```bash
# Google Cloud TTS (saves to ttsGoogle/)
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "en-US-Chirp3-HD-Kore", "provider": "google"}'

# Azure TTS (saves to ttsAzure/)
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "नमस्ते दुनिया", "voice": "hi-IN-AaravNeural", "provider": "azure"}'
```

Response:
```json
{
  "file": "ttsAzure/tts_6d8b237e.wav",
  "size": 147044,
  "voice": "hi-IN-AaravNeural",
  "provider": "azure"
}
```

#### List Voices

```bash
curl http://localhost:5000/api/voices?provider=google
curl http://localhost:5000/api/voices?provider=azure
```

#### List Generated Files

```bash
curl http://localhost:5000/api/files
curl http://localhost:5000/api/files?provider=azure
```

#### Download a File

```bash
curl http://localhost:5000/api/download/ttsAzure/tts_6d8b237e.wav -o output.wav
```

## CLI Usage

```bash
# Google Cloud TTS (default)
python3 tts.py "Hello, how are you?" -p google

# Azure TTS
python3 tts.py "नमस्ते, कैसे हैं आप?" -p azure -v hi-IN-AaravNeural

# With style instructions
python3 tts.py "Have a wonderful day!" -p google -s "Say cheerfully"

# Custom output file
python3 tts.py "Some text" -v en-US-Chirp3-HD-Aoede -o my_audio.wav

# List voices for a provider
python3 tts.py --list-voices -p google
python3 tts.py --list-voices -p azure
```

## Deploy to Vercel

1. Push repo to GitHub
2. Go to [vercel.com](https://vercel.com) and import the repo
3. Set **Framework Preset** to **Other**
4. Add environment variables:
   - `GCP_CREDENTIALS_B64` — base64-encoded service account JSON
   - `AZURE_SPEECH_KEY` — Azure Speech key
   - `AZURE_SPEECH_REGION` — e.g. `eastus`
5. Deploy

> **Note:** Vercel free plan has a 10s function timeout. Short text works fine; upgrade to Pro for 60s timeout.

## Deploy to Streamlit Cloud

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select your repo, set main file to `streamlit_app.py`
4. Add secrets: `GCP_CREDENTIALS_B64`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`
5. Deploy

## Self-Hosted (Django + Gunicorn)

```bash
export DJANGO_SECRET_KEY=your-random-secret
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com
export CSRF_TRUSTED_ORIGINS=https://yourdomain.com

python3 manage.py collectstatic --noinput
gunicorn voicd.wsgi:application --bind 0.0.0.0:8000
```

## Project Structure

```text
TxtToSpeech/
├── .env.example              # Template for env vars
├── requirements.txt          # Python dependencies
├── tts.py                    # Unified TTS interface (provider routing)
├── tts_google.py             # Google Cloud TTS provider
├── tts_azure.py              # Azure Cognitive Services TTS provider
│
├── api/
│   ├── index.py              # Vercel serverless (Flask + embedded UI)
│   └── server.py             # Standalone REST API server
├── vercel.json               # Vercel config
│
├── streamlit_app.py          # Streamlit frontend
│
├── manage.py                 # Django management
├── voicd/                    # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── ttsapp/                   # Django app
│   ├── views.py
│   ├── urls.py
│   └── templates/ttsapp/
│       └── index.html
│
├── ttsGoogle/                # Generated audio (Google Cloud)
└── ttsAzure/                 # Generated audio (Azure)
```

## Available Voices

### Google Cloud TTS (Chirp3-HD)

**Female (14):** Achernar, Aoede, Autonoe, Callirrhoe, Despina, Erinome, Gacrux, **Kore** (default), Laomedeia, Leda, Pulcherrima, Sulafat, Vindemiatrix, Zephyr

**Male (16):** Achird, Algenib, Algieba, Alnilam, Charon, Enceladus, Fenrir, Iapetus, Orus, Puck, Rasalgethi, Sadachbia, Sadaltager, Schedar, Umbriel, Zubenelgenubi

### Azure Neural Voices

**Female:** Ava (en-US), Emma (en-US), Jenny (en-US), Aria (en-US), Ananya (hi-IN), **Swara** (hi-IN, default)

**Male:** Andrew (en-US), Brian (en-US), Guy (en-US), Davis (en-US), Aarav (hi-IN), Madhur (hi-IN)

## Requirements

- Python 3.10+
- Google Cloud service account with Text-to-Speech API enabled
- Azure Speech Services key (for Azure provider)
