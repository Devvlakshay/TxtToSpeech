"""Vercel serverless function for Voicd TTS API."""

import io
import json
import os
import sys
import wave

# Add parent dir so we can import tts.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, Response, jsonify, request, send_file

from tts import ALL_VOICES, FEMALE_VOICES, MALE_VOICES, text_to_speech

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    html_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "public",
        "index.html",
    )
    with open(html_path) as f:
        return Response(f.read(), mimetype="text/html")


@app.route("/api/voices", methods=["GET"])
def voices():
    return jsonify({"female": FEMALE_VOICES, "male": MALE_VOICES})


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    text = (data.get("text") or "").strip()
    voice = data.get("voice", "Kore")
    style = (data.get("style") or "").strip()

    if not text:
        return jsonify({"error": "Text is required"}), 400
    if voice not in ALL_VOICES:
        return jsonify({"error": f"Unknown voice: {voice}"}), 400

    try:
        pcm_data = text_to_speech(text, output_file=None, voice_name=voice, style=style)

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(pcm_data)
        wav_buffer.seek(0)

        return send_file(wav_buffer, mimetype="audio/wav", download_name="voicd_output.wav")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
