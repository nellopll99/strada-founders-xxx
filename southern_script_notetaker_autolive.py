
import streamlit as st
import sounddevice as sd
import soundfile as sf
import tempfile
import os
import whisper
import openai
from datetime import datetime

st.set_page_config(page_title="Southern Script – Live NoteTaker", layout="centered")
st.title("📝 Southern Script – Live NoteTaker (Full Version)")

# Legal notice
st.markdown("### ⚠️ Legal Notice")
st.warning("This call **will be recorded**. It is your **legal responsibility** to inform all participants before proceeding. By clicking 'Start Recording', you confirm that you accept this responsibility.")

# Session state
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "summary" not in st.session_state:
    st.session_state.summary = None

# Start recording
if not st.session_state.recording:
    if st.button("🔴 Start Recording"):
        st.session_state.recording = True
        st.success("Recording started. Speak freely, and click 'Stop Recording' when done.")

# Stop recording and save
if st.session_state.recording:
    if st.button("🛑 Stop Recording"):
        st.session_state.recording = False
        st.success("Recording stopped. Saving file and processing...")

        fs = 44100
        duration = 0
        st.write("Recording...")
        recording = []

        # Record until manually stopped
        def audio_callback(indata, frames, time, status):
            if status:
                st.error(f"Error: {status}")
            recording.append(indata.copy())

        with sd.InputStream(samplerate=fs, channels=1, callback=audio_callback):
            while st.session_state.recording:
                sd.sleep(100)

        # Save audio to file
        audio_data = b"".join([x.tobytes() for x in recording])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"call_{timestamp}.wav"
        tmp_path = os.path.join(tempfile.gettempdir(), filename)
        with sf.SoundFile(tmp_path, mode='x', samplerate=fs, channels=1, subtype='PCM_16') as f:
            for chunk in recording:
                f.write(chunk)

        st.session_state.audio_file = tmp_path

# Process after file saved
if st.session_state.audio_file and not st.session_state.transcript:
    st.info("Transcribing...")
    model = whisper.load_model("base")
    result = model.transcribe(st.session_state.audio_file)
    st.session_state.transcript = result["text"]

    st.success("✅ Transcription complete.")
    st.subheader("📄 Transcript")
    st.text_area("Transcript", value=st.session_state.transcript, height=300)

    if "OPENAI_API_KEY" in st.secrets:
        st.subheader("🧠 AI Summary")
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert meeting assistant. Write a clear and structured summary based on the transcript. Include key points, questions, decisions, and follow-ups. Neutral, honest tone."},
                {"role": "user", "content": st.session_state.transcript}
            ]
        )
        st.session_state.summary = response.choices[0].message.content
        st.write(st.session_state.summary)
    else:
        st.warning("No OpenAI API key found.")

    # Download links
    with open(st.session_state.audio_file, "rb") as f:
        st.download_button("📥 Download audio (.wav)", data=f, file_name=os.path.basename(st.session_state.audio_file), mime="audio/wav")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w") as f:
        f.write(st.session_state.summary or "")
        st.download_button("📄 Download summary (.txt)", data=open(f.name, "rb"), file_name="call_summary.txt", mime="text/plain")

    # Cleanup
    os.remove(st.session_state.audio_file)
    st.session_state.audio_file = None
    st.session_state.transcript = None
    st.session_state.summary = None
    st.success("Session cleaned. All files deleted after download.")
