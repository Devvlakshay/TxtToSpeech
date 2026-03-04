"""Vercel serverless function for Voicd TTS API."""

import io
import os
import sys
import traceback
import wave

# Add parent dir so we can import tts.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, Response, jsonify, request, send_file

try:
    from tts import ALL_VOICES, FEMALE_VOICES, MALE_VOICES, text_to_speech
except Exception as e:
    print(f"Import error: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voicd - Text to Speech</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 40px 20px;
        }
        .container { width: 100%; max-width: 600px; }
        h1 { font-size: 2rem; margin-bottom: 8px; color: #fff; }
        .subtitle { color: #888; margin-bottom: 32px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; color: #ccc; }
        .hint { font-weight: 400; color: #666; }
        textarea, input[type="text"], select {
            width: 100%; padding: 12px; border: 1px solid #333;
            border-radius: 8px; background: #1a1a1a; color: #e0e0e0;
            font-size: 1rem; margin-bottom: 20px;
        }
        textarea { height: 140px; resize: vertical; }
        textarea:focus, input:focus, select:focus { outline: none; border-color: #5b8def; }
        button {
            width: 100%; padding: 12px; border: none; border-radius: 8px;
            background: #5b8def; color: #fff; font-size: 1rem;
            font-weight: 600; cursor: pointer; transition: background 0.2s;
        }
        button:hover { background: #4a7de0; }
        button:disabled { background: #333; cursor: not-allowed; }
        .error { background: #3a1a1a; border: 1px solid #662222; color: #ff6b6b; padding: 12px; border-radius: 8px; margin-bottom: 20px; }
        .result { margin-top: 28px; padding: 20px; background: #1a1a1a; border: 1px solid #333; border-radius: 8px; }
        .result h3 { margin-bottom: 16px; color: #fff; }
        audio { width: 100%; margin-bottom: 16px; }
        .download-btn {
            display: inline-block; padding: 10px 20px; background: #2a8a5a;
            color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600;
        }
        .download-btn:hover { background: #237a4e; }
        .spinner { display: none; margin-top: 16px; text-align: center; color: #888; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Voicd</h1>
        <p class="subtitle">Text-to-Speech powered by Gemini</p>

        <div id="error" class="error hidden"></div>

        <label for="text">Text</label>
        <textarea id="text" placeholder="Enter text to convert to speech..."></textarea>

        <label for="voice">Voice</label>
        <select id="voice"></select>

        <label for="style">Style Instructions <span class="hint">(optional)</span></label>
        <input type="text" id="style" placeholder="e.g. Say cheerfully, Speak in a whisper, Read slowly">

        <button id="gen-btn" onclick="generate()">Generate Speech</button>
        <div class="spinner" id="spinner">Generating audio, please wait...</div>

        <div id="result" class="result hidden">
            <h3>Generated Audio</h3>
            <audio id="audio" controls></audio>
            <a id="download-btn" class="download-btn" href="#" download="voicd_output.wav">Download WAV</a>
        </div>
    </div>

    <script>
        fetch('/api/voices')
            .then(r => r.json())
            .then(data => {
                const select = document.getElementById('voice');
                const femaleGroup = document.createElement('optgroup');
                femaleGroup.label = 'Female';
                data.female.forEach(v => {
                    const opt = document.createElement('option');
                    opt.value = v; opt.textContent = v;
                    if (v === 'Kore') opt.selected = true;
                    femaleGroup.appendChild(opt);
                });
                const maleGroup = document.createElement('optgroup');
                maleGroup.label = 'Male';
                data.male.forEach(v => {
                    const opt = document.createElement('option');
                    opt.value = v; opt.textContent = v;
                    maleGroup.appendChild(opt);
                });
                select.appendChild(femaleGroup);
                select.appendChild(maleGroup);
            });

        async function generate() {
            const text = document.getElementById('text').value.trim();
            const voice = document.getElementById('voice').value;
            const style = document.getElementById('style').value.trim();
            const btn = document.getElementById('gen-btn');
            const spinner = document.getElementById('spinner');
            const errorDiv = document.getElementById('error');
            const resultDiv = document.getElementById('result');

            errorDiv.classList.add('hidden');
            resultDiv.classList.add('hidden');

            if (!text) { errorDiv.textContent = 'Please enter some text.'; errorDiv.classList.remove('hidden'); return; }

            btn.disabled = true; btn.textContent = 'Generating...';
            spinner.style.display = 'block';

            try {
                const resp = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, voice, style }),
                });

                if (!resp.ok) {
                    const err = await resp.json();
                    throw new Error(err.error || 'Generation failed');
                }

                const blob = await resp.blob();
                const url = URL.createObjectURL(blob);

                document.getElementById('audio').src = url;
                document.getElementById('download-btn').href = url;
                resultDiv.classList.remove('hidden');
            } catch (e) {
                errorDiv.textContent = e.message;
                errorDiv.classList.remove('hidden');
            } finally {
                btn.disabled = false; btn.textContent = 'Generate Speech';
                spinner.style.display = 'none';
            }
        }
    </script>
</body>
</html>"""


@app.route("/", methods=["GET"])
def home():
    return Response(HTML_PAGE, mimetype="text/html")


@app.route("/api/health", methods=["GET"])
def health():
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    return jsonify({
        "status": "ok",
        "gemini_key_set": has_key,
        "voices_loaded": len(ALL_VOICES),
    })


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
        print(f"Generate error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return jsonify({"error": str(e)}), 500
