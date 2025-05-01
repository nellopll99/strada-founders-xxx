
import streamlit as st
import whisper
import openai
import tempfile
import os

st.set_page_config(page_title="Southern Script – AI NoteTaker", layout="centered")
st.title("📝 Southern Script – Upload Your Call")

uploaded_file = st.file_uploader("Upload an audio file (.wav, .mp3, .m4a)", type=["wav", "mp3", "m4a"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        tmp.write(uploaded_file.read())
        audio_path = tmp.name

    st.audio(audio_path)

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcript = result["text"]
    st.success("Transcription complete.")
    st.text_area("Transcript", transcript, height=300)

    if "OPENAI_API_KEY" in st.secrets:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional meeting assistant. Write a structured and honest summary based on the transcript."},
                {"role": "user", "content": transcript}
            ]
        )
        summary = response.choices[0].message.content
        st.subheader("📄 Summary")
        st.write(summary)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w") as f:
            f.write(summary)
            st.download_button("📥 Download Summary", open(f.name, "rb"), "summary.txt", "text/plain")

    os.remove(audio_path)
