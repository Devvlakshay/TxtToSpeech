"""Voicd - Text-to-Speech Web App (Streamlit)"""

import io
import wave

import streamlit as st

from tts import FEMALE_VOICES, MALE_VOICES, text_to_speech

st.set_page_config(page_title="Voicd - Text to Speech", page_icon="🎙️", layout="centered")

st.title("Voicd")
st.caption("Text-to-Speech powered by Gemini")

text = st.text_area("Text", placeholder="Enter text to convert to speech...", height=150)

col1, col2 = st.columns(2)
with col1:
    voice_options = (
        ["— Female —"] + FEMALE_VOICES + ["— Male —"] + MALE_VOICES
    )
    voice = st.selectbox(
        "Voice",
        options=FEMALE_VOICES + MALE_VOICES,
        format_func=lambda v: f"♀ {v}" if v in FEMALE_VOICES else f"♂ {v}",
        index=FEMALE_VOICES.index("Kore"),
    )
with col2:
    style = st.text_input(
        "Style Instructions (optional)",
        placeholder="e.g. Say cheerfully",
    )

if st.button("Generate Speech", type="primary", use_container_width=True):
    if not text.strip():
        st.error("Please enter some text.")
    else:
        with st.spinner("Generating audio..."):
            try:
                pcm_data = text_to_speech(
                    text.strip(),
                    output_file=None,
                    voice_name=voice,
                    style=style.strip(),
                )

                # Convert raw PCM to WAV in memory
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(pcm_data)
                wav_bytes = wav_buffer.getvalue()

                st.audio(wav_bytes, format="audio/wav")
                st.download_button(
                    "Download WAV",
                    data=wav_bytes,
                    file_name="voicd_output.wav",
                    mime="audio/wav",
                )
            except Exception as e:
                st.error(str(e))
