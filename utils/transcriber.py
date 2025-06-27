
# # import whisper
# # import re
# # import streamlit as st  # ✅ Add this
# # from youtube_transcript_api import (
# #     YouTubeTranscriptApi,
# #     TranscriptsDisabled,
# #     NoTranscriptFound,
# #     CouldNotRetrieveTranscript
# # )
# import whisper
# import re
# import json
# import requests
# import streamlit as st
# from xml.etree import ElementTree as ET

# from youtube_transcript_api import (
#     TranscriptsDisabled,
#     NoTranscriptFound,
#     CouldNotRetrieveTranscript
# )
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

# def extract_video_id(youtube_url: str) -> str:
#     pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
#     match = re.search(pattern, youtube_url)
#     return match.group(1) if match else None

# # def try_youtube_captions(youtube_url: str):
# #     try:
# #         video_id = extract_video_id(youtube_url)
# #         if not video_id:
# #             st.warning("❌ Invalid YouTube URL or video ID.")
# #             return None, None

# #         transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

# #         try:
# #             # Try manually created English transcript first
# #             transcript = transcript_list.find_transcript(['en', 'en-IN'])
# #         except:
# #             # If not found, fallback to any available auto-generated
# #             transcript = transcript_list.find_generated_transcript(transcript_list._generated_transcripts.keys())

# #         raw_segments = transcript.fetch()
# #         full_text = " ".join([seg.text for seg in raw_segments])

# #         segments = [
# #             {
# #                 "start": seg.start,
# #                 "end": seg.start + seg.duration,
# #                 "text": seg.text
# #             }
# #             for seg in raw_segments
# #         ]

# #         st.info(f"✅ Used YouTube captions for transcription. Language: {transcript.language_code}")
# #         return full_text, segments

# #     except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as e:
# #         st.warning(f"⚠️ YouTube captions not available: {e}")
# #         return None, None
# #     except Exception as e:
# #         st.error(f"❌ Error during YouTube caption extraction: {e}")
# #         return None, None


# def try_youtube_captions(youtube_url: str):
#     try:
#         video_id = extract_video_id(youtube_url)
#         if not video_id:
#             st.warning("❌ Invalid YouTube URL or video ID.")
#             return None, None

#         # Use proxy from secrets
#         proxy_url = st.secrets["PROXY_URL"]
#         proxies = {"http": proxy_url, "https": proxy_url}
#         transcript_url = f"https://video.google.com/timedtext?lang=en&v={video_id}"

#         response = requests.get(transcript_url, proxies=proxies, timeout=10)

#         if response.status_code != 200 or not response.text.strip():
#             # Short clear fallback
#             st.info("⚠️ Captions not available — falling back to Whisper.")
#             return None, None

#         # Parse XML captions
#         root = ET.fromstring(response.text)
#         segments = []
#         full_text = ""

#         for child in root.findall("text"):
#             start = float(child.attrib["start"])
#             dur = float(child.attrib.get("dur", "1.0"))
#             text = (child.text or "").replace("\n", " ")
#             full_text += text + " "
#             segments.append({
#                 "start": start,
#                 "end": start + dur,
#                 "text": text
#             })

#         st.success("✅ Captions fetched via proxy.")
#         return full_text.strip(), segments

#     except Exception:
#         # Always show same short fallback
#         st.info("⚠️ Captions not available — falling back to Whisper.")
#         return None, None


# # def transcribe_audio(audio_path: str, youtube_url: str = None):
# #     # First try YouTube captions
# #     if youtube_url:
# #         text, segments = try_youtube_captions(youtube_url)
# #         if text:
# #             return text, segments

# #     # If not found, fallback to Whisper
# #     st.info("🗣️ Using Whisper for transcription...")
# #     model = whisper.load_model("tiny")
# #     result = model.transcribe(audio_path, verbose=False)
# #     return result["text"], result["segments"]

# def transcribe_audio(audio_path: str, youtube_url: str = None, status_placeholder=None):
#     if youtube_url:
#         text, segments = try_youtube_captions(youtube_url, status_placeholder)
#         if text:
#             return text, segments

#     if status_placeholder:
#         status_placeholder.info("🗣️ Using Whisper for transcription...")

#     model = whisper.load_model("tiny")
#     result = model.transcribe(audio_path, verbose=False)
#     return result["text"], result["segments"]


import whisper
import re
import requests
import streamlit as st
from xml.etree import ElementTree as ET

def extract_video_id(youtube_url: str) -> str:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    return match.group(1) if match else None

def try_youtube_captions(youtube_url: str):
    try:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.warning("❌ Invalid YouTube URL.")
            return None, None

        proxy_url = st.secrets.get("PROXY_URL", "")
        if not proxy_url:
            st.info("⚠️ Proxy not set. Skipping captions.")
            return None, None

        proxies = {"http": proxy_url, "https": proxy_url}
        transcript_url = f"https://video.google.com/timedtext?lang=en&v={video_id}"

        response = requests.get(transcript_url, proxies=proxies, timeout=10)

        if response.status_code != 200 or not response.text.strip():
            st.info("⚡ Captions not available or blocked. Switching to Whisper.")
            return None, None

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

        st.success("✅ YouTube captions used (via proxy).")
        return full_text.strip(), segments

    except Exception:
        st.info("⚡ Captions failed. Switching to Whisper.")
        return None, None


def transcribe_audio(audio_path: str, youtube_url: str = None):
    # 1️⃣ Try captions via proxy
    if youtube_url:
        text, segments = try_youtube_captions(youtube_url)
        if text:
            return text, segments

    # 2️⃣ If failed, fallback to Whisper
    st.info("🗣️ Using Whisper for transcription...")
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path, verbose=False)
    return result["text"], result["segments"]
