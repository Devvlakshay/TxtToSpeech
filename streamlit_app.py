"""Voicd - Text-to-Speech Web App (Streamlit)"""

import streamlit as st

from tts import display_name, get_voices, text_to_speech

st.set_page_config(page_title="Voicd - Text to Speech", page_icon="🎙️", layout="centered")

st.title("Voicd")
st.caption("Text-to-Speech")

provider = st.radio("Provider", ["google", "azure"], horizontal=True, format_func=lambda p: "Google Cloud" if p == "google" else "Azure")

female, male, default = get_voices(provider)
all_names = female + male

text = st.text_area("Text", placeholder="Enter text to convert to speech...", height=150)

col1, col2 = st.columns(2)
with col1:
    voice = st.selectbox(
        "Voice",
        options=all_names,
        format_func=lambda v: f"♀ {display_name(v, provider)}" if v in female else f"♂ {display_name(v, provider)}",
        index=all_names.index(default) if default in all_names else 0,
    )
with col2:
    style = st.text_input("Style Instructions (optional)", placeholder="e.g. Say cheerfully")

if st.button("Generate Speech", type="primary", use_container_width=True):
    if not text.strip():
        st.error("Please enter some text.")
    else:
        with st.spinner("Generating audio..."):
            try:
                wav_bytes = text_to_speech(
                    text.strip(), output_file=None,
                    voice_name=voice, style=style.strip(), provider=provider,
                )
                st.audio(wav_bytes, format="audio/wav")
                st.download_button("Download WAV", data=wav_bytes, file_name="voicd_output.wav", mime="audio/wav")
            except Exception as e:
                st.error(str(e))
