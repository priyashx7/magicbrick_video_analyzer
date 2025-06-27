
import whisper
import re
import streamlit as st  # ✅ Add this
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript
)

def extract_video_id(youtube_url: str) -> str:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None

# def try_youtube_captions(youtube_url: str):
#     try:
#         video_id = extract_video_id(youtube_url)
#         if not video_id:
#             st.warning("❌ Invalid YouTube URL or video ID.")
#             return None, None

#         transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

#         try:
#             # Try manually created English transcript first
#             transcript = transcript_list.find_transcript(['en', 'en-IN'])
#         except:
#             # If not found, fallback to any available auto-generated
#             transcript = transcript_list.find_generated_transcript(transcript_list._generated_transcripts.keys())

#         raw_segments = transcript.fetch()
#         full_text = " ".join([seg.text for seg in raw_segments])

#         segments = [
#             {
#                 "start": seg.start,
#                 "end": seg.start + seg.duration,
#                 "text": seg.text
#             }
#             for seg in raw_segments
#         ]

#         st.info(f"✅ Used YouTube captions for transcription. Language: {transcript.language_code}")
#         return full_text, segments

#     except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as e:
#         st.warning(f"⚠️ YouTube captions not available: {e}")
#         return None, None
#     except Exception as e:
#         st.error(f"❌ Error during YouTube caption extraction: {e}")
#         return None, None


import whisper
import re
import json
import requests
import streamlit as st
from xml.etree import ElementTree as ET  # for parsing YouTube caption XML

from youtube_transcript_api import (
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript
)

def try_youtube_captions(youtube_url: str):
    try:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.warning("❌ Invalid YouTube URL or video ID.")
            return None, None

        # 🛡️ Get proxy URL from Streamlit secrets
        proxy_url = st.secrets["PROXY_URL"]
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

        # Direct YouTube caption API URL
        transcript_url = f"https://video.google.com/timedtext?lang=en&v={video_id}"

        # Make request via proxy
        response = requests.get(transcript_url, proxies=proxies, timeout=10)

        if response.status_code != 200 or not response.text:
            st.warning("⚠️ Captions not available or blocked. Using Whisper instead.")
            return None, None

        # Parse XML captions
        root = ET.fromstring(response.text)
        segments = []
        full_text = ""

        for child in root.findall("text"):
            start = float(child.attrib["start"])
            dur = float(child.attrib.get("dur", "1.0"))
            text = (child.text or "").replace("\n", " ")
            full_text += text + " "
            segments.append({
                "start": start,
                "end": start + dur,
                "text": text
            })

        st.info("✅ Used YouTube captions via proxy.")
        return full_text.strip(), segments

    except Exception as e:
        st.warning("⚠️ Proxy caption fetch failed. Falling back to Whisper.")
        print(f"[Proxy error] {e}")
        return None, None



def transcribe_audio(audio_path: str, youtube_url: str = None):
    # First try YouTube captions
    if youtube_url:
        text, segments = try_youtube_captions(youtube_url)
        if text:
            return text, segments

    # If not found, fallback to Whisper
    st.info("🗣️ Using Whisper for transcription...")
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path, verbose=False)
    return result["text"], result["segments"]
