# Islamic Reel Studio

A Streamlit app for combining uploaded narration, optional background footage,
quiet Nasheed or ambient audio, and the supplied transparent logo into a
vertical MP4. Audio loops or trims to narration length with adjustable fades.

## Run locally

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

Publish this directory as a GitHub repository, including `brand_logo.png`.
In Community Cloud, select that repository, branch `main`, and main file
`app.py`. Choose Python 3.13 in Advanced settings. No API keys are required
for the current upload-based workflow.

Official deployment instructions:
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

The dependencies retain MoviePy 1.x to match this app's API. ImageIO-FFmpeg
supplies the FFmpeg executable on supported platforms. The local app and a
sample MP4 export were tested; cloud deployment has not yet been verified.

## Usage

1. Upload the main narration and, optionally, a second narration.
2. Add optional footage and a background audio track you are authorized to use.
3. Adjust background volume, fades, logo visibility, and output resolution.
4. Create the reel, preview it, and download the MP4.

The app uses a green background when footage is omitted. Uploaded files are
processed in a temporary directory, cleaned up after rendering. The completed
video stays in the browser session's server-side memory for downloading.
On cloud hosting, uploads are processed by the cloud server, not locally.

Automatic script writing, synthesized narration, subtitles, and stock-media
search are not implemented in this version. Long or Full HD renders can exceed
Community Cloud memory or compute limits; begin with short 540 × 960 exports.
