"""Voicd - Text-to-Speech Web App (Streamlit)"""

import streamlit as st

from tts import DEFAULT_VOICE, FEMALE_VOICES, MALE_VOICES, display_name, text_to_speech

st.set_page_config(page_title="Voicd - Text to Speech", page_icon="🎙️", layout="centered")

st.title("Voicd")
st.caption("Text-to-Speech powered by Google Cloud TTS")

text = st.text_area("Text", placeholder="Enter text to convert to speech...", height=150)

col1, col2 = st.columns(2)
with col1:
    voice = st.selectbox(
        "Voice",
        options=FEMALE_VOICES + MALE_VOICES,
        format_func=lambda v: f"♀ {display_name(v)}" if v in FEMALE_VOICES else f"♂ {display_name(v)}",
        index=FEMALE_VOICES.index(DEFAULT_VOICE) if DEFAULT_VOICE in FEMALE_VOICES else 0,
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
                wav_bytes = text_to_speech(
                    text.strip(),
                    output_file=None,
                    voice_name=voice,
                    style=style.strip(),
                )

                st.audio(wav_bytes, format="audio/wav")
                st.download_button(
                    "Download WAV",
                    data=wav_bytes,
                    file_name="voicd_output.wav",
                    mime="audio/wav",
                )
            except Exception as e:
                st.error(str(e))
