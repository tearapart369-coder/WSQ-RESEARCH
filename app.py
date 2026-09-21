from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st
from logo_overlay import LOGO_PATH
from reel_engine import render_reel

st.set_page_config(page_title="Islamic Reel Studio", page_icon="🌙", layout="wide")
st.markdown("""<style>
.stApp {background: #071b17; color: #f4f0e4;}
[data-testid="stSidebar"] {background: #0d2821;}
.block-container {max-width: 1200px; padding-top: 2.5rem;}
h1,h2,h3 {color: #f5df9a !important;}
div.stButton > button[kind="primary"] {background:#d9b65d; color:#10251d; border:0;}
[data-testid="stFileUploader"] {border:1px solid #365347; border-radius:12px;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.image(str(LOGO_PATH), width=210)
    st.header("Your reel, your voice")
    st.caption("Local video studio • Bengali & Arabic narration")
    st.divider()
    st.subheader("Sound & branding")
    volume = st.slider("Background volume (%)", 0, 20, 8, 1)
    fade = st.slider("Fade in / out (seconds)", 0.0, 3.0, 1.5, 0.1)
    show_logo = st.toggle("Show my logo", value=True)
    resolution = st.selectbox("Export resolution", ["540 × 960 · Faster preview", "1080 × 1920 · Full HD"])
    st.caption("Vertical 9:16 • MP4 • 24 fps")

st.caption("ওয়াসিকের গবেষণা  /  REEL STUDIO")
st.title("Give your message a beautiful setting.")
st.write("Combine your narration, a soft Nasheed or ambient track, and your logo into a vertical reel.")
st.info("Ready to mix your own files locally. Automatic script writing, voice generation, and stock-media search are not connected in this version.")

left, right = st.columns([1.3, 1], gap="large")
with left:
    st.subheader("01 · Add your narration")
    narration = st.file_uploader("Main narration", type=["mp3", "wav", "m4a", "ogg"], key="main")
    additional = st.file_uploader("Arabic or second narration (optional)", type=["mp3", "wav", "m4a", "ogg"], key="second")
    st.caption("The second recording plays after the main narration. Upload recorded speech in any language.")
    st.subheader("02 · Set the atmosphere")
    footage = st.file_uploader("Background video (optional)", type=["mp4", "mov", "webm", "mkv"])
    music = st.file_uploader("Nasheed or ambient audio (optional)", type=["mp3", "wav", "m4a", "ogg"], key="ambient")
    st.caption("Without video, your reel uses a deep green background. Background audio loops or trims to fit your voice.")
    render = st.button("Create my reel", type="primary", disabled=narration is None, use_container_width=True)

with right:
    st.subheader("03 · Preview & download")
    if "reel_bytes" not in st.session_state:
        st.image(str(LOGO_PATH), width=280)
        st.caption("Your logo is ready. Add a narration to create your first reel.")

if render:
    try:
        with st.spinner("Mixing your audio and rendering your reel…"):
            with TemporaryDirectory(prefix="reel-studio-") as directory:
                folder = Path(directory)

                def save(upload, label):
                    if upload is None:
                        return None
                    path = folder / (label + Path(upload.name).suffix.lower())
                    path.write_bytes(upload.getvalue())
                    return path

                voices = [save(narration, "narration")]
                if additional is not None:
                    voices.append(save(additional, "second"))
                result = folder / "branded_reel.mp4"
                render_reel(
                    voices, result, save(footage, "footage"), save(music, "ambient"),
                    volume=volume / 100, fade=fade,
                    size=(1080, 1920) if resolution.startswith("1080") else (540, 960),
                    show_logo=show_logo,
                )
                st.session_state.reel_bytes = result.read_bytes()
        st.success("Your branded reel is ready.")
    except Exception as exc:
        st.error(f"Could not create the reel: {exc}")

with right:
    if "reel_bytes" in st.session_state:
        st.video(st.session_state.reel_bytes)
        st.download_button("Download MP4", st.session_state.reel_bytes,
                           "branded_reel.mp4", "video/mp4", use_container_width=True)
        st.caption("This is your last completed export. Create a new reel to apply changed files or settings.")
