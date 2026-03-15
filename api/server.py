"""Standalone REST API server for Voicd TTS.

Run:
    python3 api/server.py

Endpoints:
    POST /api/generate
        Body: { "text": "...", "voice": "...", "style": "...", "provider": "google|azure" }
        Returns: { "file": "ttsGoogle/xxx.wav" or "ttsAzure/xxx.wav", "size": 12345 }

    GET /api/voices?provider=google|azure
        Returns: { "female": [...], "male": [...], "default_voice": "..." }

Audio files are saved to ttsGoogle/ and ttsAzure/ folders automatically.
"""

import os
import sys
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, send_file

from tts import display_name, get_voices, text_to_speech

app = Flask(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIRS = {
    "google": os.path.join(PROJECT_ROOT, "ttsGoogle"),
    "azure": os.path.join(PROJECT_ROOT, "ttsAzure"),
}

# Create output directories
for d in OUTPUT_DIRS.values():
    os.makedirs(d, exist_ok=True)


@app.route("/api/voices", methods=["GET"])
def voices():
    provider = request.args.get("provider", "google")
    female, male, default = get_voices(provider)
    return jsonify({
        "female": [{"name": v, "display": display_name(v, provider)} for v in female],
        "male": [{"name": v, "display": display_name(v, provider)} for v in male],
        "default_voice": default,
        "provider": provider,
    })


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    text = (data.get("text") or "").strip()
    voice = data.get("voice")
    style = (data.get("style") or "").strip()
    provider = data.get("provider", "google")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    if provider not in OUTPUT_DIRS:
        return jsonify({"error": f"Unknown provider: {provider}. Use 'google' or 'azure'"}), 400

    output_dir = OUTPUT_DIRS[provider]
    filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
    filepath = os.path.join(output_dir, filename)

    try:
        wav_data = text_to_speech(text, output_file=filepath, voice_name=voice, style=style, provider=provider)
        relative_path = os.path.join(os.path.basename(output_dir), filename)
        return jsonify({
            "file": relative_path,
            "size": len(wav_data),
            "voice": voice,
            "provider": provider,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/<provider>/<filename>", methods=["GET"])
def download(provider, filename):
    if provider not in OUTPUT_DIRS:
        return jsonify({"error": "Unknown provider"}), 404
    if not filename.endswith(".wav") or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400
    filepath = os.path.join(OUTPUT_DIRS[provider], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath, mimetype="audio/wav", as_attachment=True, download_name=filename)


@app.route("/api/files", methods=["GET"])
def list_files():
    """List all generated audio files."""
    provider = request.args.get("provider")
    result = {}
    dirs = {provider: OUTPUT_DIRS[provider]} if provider and provider in OUTPUT_DIRS else OUTPUT_DIRS
    for p, d in dirs.items():
        files = sorted(
            [f for f in os.listdir(d) if f.endswith(".wav")],
            key=lambda f: os.path.getmtime(os.path.join(d, f)),
            reverse=True,
        )
        result[p] = [{"file": f"{os.path.basename(d)}/{f}", "size": os.path.getsize(os.path.join(d, f))} for f in files]
    return jsonify(result)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "5000"))
    print(f"\nVoicd TTS API running on http://0.0.0.0:{port}")
    print(f"  POST /api/generate    - Generate audio")
    print(f"  GET  /api/voices      - List voices")
    print(f"  GET  /api/files       - List generated files")
    print(f"  GET  /api/download    - Download a file\n")
    print(f"Audio saved to: ttsGoogle/ and ttsAzure/\n")
    app.run(host="0.0.0.0", port=port, debug=True)
