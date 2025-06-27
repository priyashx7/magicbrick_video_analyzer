

# import os
# import streamlit as st
# import shutil
# from dotenv import load_dotenv
# load_dotenv()

# from utils.downloader import download_audio, download_video
# from utils.transcriber import transcribe_audio
# from utils.summarizer import get_summary
# from utils.speaker_identifier import extract_speakers_from_metadata_using_llm
# from utils.speaker_insights import extract_speaker_insights
# from utils.metadata_parser import fetch_metadata
# from utils.reel_selector import get_top_reel_chunks_from_transcript, match_chunks_to_segments
# from utils.ffmpeg_utils import trim_and_crop_with_ffmpeg
# import glob


# st.title("🎙️ MBTV Video Analyzer")

# youtube_url = st.text_input("Paste a YouTube video link from MBTV:")

# if st.button("Generate Analysis"):
#     with st.spinner("Processing... Please wait. Estimated time 2-5 minutes."):

#         status_placeholder = st.empty()


#         # # Clean previous files
#         # status_placeholder.info("🧹 Cleaning previous files...")
#         # output_dir = "outputs"
#         # for f in os.listdir(output_dir):
#         #     file_path = os.path.join(output_dir, f)
#         #     try:
#         #         if os.path.isfile(file_path):
#         #             os.remove(file_path)
#         #     except Exception as e:
#         #         print(f"Error deleting {file_path}: {e}")

#         # Clean previous files
#         status_placeholder.info("🧹 Cleaning previous files...")
        
#         output_dir = "outputs"
#         os.makedirs(output_dir, exist_ok=True)  # ✅ Ensures the folder exists
        
#         for f in os.listdir(output_dir):
#             file_path = os.path.join(output_dir, f)
#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#             except Exception as e:
#                 print(f"Error deleting {file_path}: {e}")

#         # Step 1: Download
#         status_placeholder.info("⬇️ Downloading audio and video... Time depends on the video length and quality.")
#         audio_path = download_audio(youtube_url)
#         video_path = download_video(youtube_url)

#         if not video_path or not os.path.exists(video_path):
#             status_placeholder.error("⚠️ Video download failed or file not found.")
#             st.stop()

#         # Step 2: Transcribe
#         # status_placeholder.info("📝 Transcribing... (trying YouTube captions first)")
#         # transcript, segments = transcribe_audio(audio_path, youtube_url)
#         transcript, segments = transcribe_audio(audio_path, youtube_url, status_placeholder)


#         if transcript:
#             status_placeholder.success("✅ Transcription Complete.")
#         else:
#             status_placeholder.error("❌ Failed to generate transcript.")
#             st.stop()

#         # Step 3: Reel Chunks
#         status_placeholder.info("🎞️ Extracting top reel-worthy chunks...")
#         reel_chunks = get_top_reel_chunks_from_transcript(transcript)
#         reel_timestamps = match_chunks_to_segments(reel_chunks, segments)

#         # Step 4: Speaker Metadata
#         status_placeholder.info("🧑 Identifying speakers...")
#         metadata = fetch_metadata(youtube_url)
#         speaker_metadata = extract_speakers_from_metadata_using_llm(metadata['title'], metadata['description'])

#         status_placeholder.empty()  # Clear progress after final step

#         # --- Tabs ---
#         if speaker_metadata == "NO_SPEAKER_FOUND":
#             tab1, tab2, tab3, tab5, tab6 = st.tabs([
#                 "📄 Full Transcript",
#                 "🧠 Summary",
#                 "🧑 Speakers",
#                 "🎬 Timestamped Chunks",
#                 "🎞️ Downloaded Reels"
#             ])
#         else:
#             tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
#                 "📄 Full Transcript",
#                 "🧠 Summary",
#                 "🧑 Speakers",
#                 "🔍 Speaker Insights",
#                 "🎬 Timestamped Chunks",
#                 "🎞️ Downloaded Reels"
#             ])

#         with tab1:
#             st.subheader("Full Transcript")
#             st.write(transcript)

#         with tab2:
#             st.subheader("Video Summary")
#             st.write(get_summary(transcript))

#         with tab3:
#             st.subheader("Identified Speakers")
#             st.write("🚫 No speakers found." if speaker_metadata == "NO_SPEAKER_FOUND" else speaker_metadata)

#         if speaker_metadata != "NO_SPEAKER_FOUND":
#             with tab4:
#                 st.subheader("Speaker-wise Insights")
#                 full_output = extract_speaker_insights(transcript, speaker_metadata)

#                 if "Repeated Attributes:" in full_output:
#                     insights_part, attributes_part = full_output.split("Repeated Attributes:")
#                     st.markdown("#### 🧑 Speaker Insights")
#                     st.markdown(insights_part.strip())
#                     st.markdown("#### 🔁 Repeated Keywords")
#                     st.markdown(attributes_part.strip())
#                 else:
#                     st.markdown(full_output)

#         with tab5:
#             st.subheader("🎞️ Top Reel Moments")
#             if not reel_timestamps:
#                 st.warning("❌ No high-quality reel moments were found.")
#             else:
#                 for idx, item in enumerate(reel_timestamps):
#                     st.markdown(f"**Reel {idx+1}** — `{item['start']}s to `{item['end']}s`")
#                     st.write(item['text'])

#                 st.info("🤔 Not satisfied with the reels shown? You can try re-generating the analysis for better results.")


#         with tab6:
#             st.subheader("📽️ Auto-Cut Reels (FFmpeg)")

#             if reel_timestamps and isinstance(reel_timestamps, list) and video_path and os.path.exists(video_path):
#                 for idx, item in enumerate(reel_timestamps):
#                     start = round(item.get('start', 0), 2)
#                     end = round(item.get('end', 0), 2)

#                     if end <= start:
#                         st.warning(f"⚠️ Skipping clip {idx+1}: end time <= start time")
#                         continue
#                     if (end - start) < 5:
#                         st.warning(f"⚠️ Skipping clip {idx+1}: too short (< 5s)")
#                         continue

#                     clip_path = trim_and_crop_with_ffmpeg(
#                         video_path, start, end, idx=idx
#                     )

#                     if clip_path and os.path.exists(clip_path):
#                         st.video(clip_path)
#                         st.markdown(f"🕒 Clip {idx+1}: `{start}s` to `{end}s`")
#                     else:
#                         st.error(f"❌ Failed to generate clip {idx+1}")
#             else:
#                 st.warning("⚠️ Valid timestamps or video not available.")

#             st.info("🤔 Not satisfied with the reels shown? You can try re-generating the analysis for better results.")


import os
import streamlit as st
import shutil
from dotenv import load_dotenv
load_dotenv()

from utils.downloader import download_audio, download_video
from utils.transcriber import transcribe_audio
from utils.summarizer import get_summary
from utils.speaker_identifier import extract_speakers_from_metadata_using_llm
from utils.speaker_insights import extract_speaker_insights
from utils.metadata_parser import fetch_metadata
from utils.reel_selector import get_top_reel_chunks_from_transcript, match_chunks_to_segments
from utils.ffmpeg_utils import trim_and_crop_with_ffmpeg
import glob


st.title("🎙️ MBTV Video Analyzer")

youtube_url = st.text_input("Paste a YouTube video link from MBTV:")

if st.button("Generate Analysis"):
    with st.spinner("Processing... Please wait. Estimated time 1-4 minutes."):

        status_placeholder = st.empty()


        # Clean previous files
        status_placeholder.info("🧹 Cleaning previous files...")
        output_dir = "outputs"
        for f in os.listdir(output_dir):
            file_path = os.path.join(output_dir, f)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

        # Step 1: Download
        status_placeholder.info("⬇️ Downloading audio and video... Time depends on the video length and quality.")
        audio_path = download_audio(youtube_url)
        video_path = download_video(youtube_url)

        if not video_path or not os.path.exists(video_path):
            status_placeholder.error("⚠️ Video download failed or file not found.")
            st.stop()

        # Step 2: Transcribe
        status_placeholder.info("📝 Trying YouTube captions via proxy...")
        
        # Call the new transcribe function but split it
        from utils.transcriber import try_youtube_captions, transcribe_with_whisper
        
        # First try captions directly:
        transcript, segments = try_youtube_captions(youtube_url)
        
        if transcript:
            status_placeholder.success("✅ Transcription Complete using YouTube captions.")
        else:
            status_placeholder.info("⚠️ Captions failed. Using Whisper instead...")
            transcript, segments = transcribe_with_whisper(audio_path)
        
            if transcript:
                status_placeholder.success("✅ Transcription Complete using Whisper.")
            else:
                status_placeholder.error("❌ Failed to generate transcript.")
                st.stop()


        # Step 3: Reel Chunks
        status_placeholder.info("🎞️ Extracting top reel-worthy chunks...")
        reel_chunks = get_top_reel_chunks_from_transcript(transcript)
        reel_timestamps = match_chunks_to_segments(reel_chunks, segments)

        # Step 4: Speaker Metadata
        status_placeholder.info("🧑 Identifying speakers...")
        metadata = fetch_metadata(youtube_url)
        speaker_metadata = extract_speakers_from_metadata_using_llm(metadata['title'], metadata['description'])

        status_placeholder.empty()  # Clear progress after final step

        # --- Tabs ---
        if speaker_metadata == "NO_SPEAKER_FOUND":
            tab1, tab2, tab3, tab5, tab6 = st.tabs([
                "📄 Full Transcript",
                "🧠 Summary",
                "🧑 Speakers",
                "🎬 Timestamped Chunks",
                "🎞️ Downloaded Reels"
            ])
        else:
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📄 Full Transcript",
                "🧠 Summary",
                "🧑 Speakers",
                "🔍 Speaker Insights",
                "🎬 Timestamped Chunks",
                "🎞️ Downloaded Reels"
            ])

        with tab1:
            st.subheader("Full Transcript")
            st.write(transcript)

        with tab2:
            st.subheader("Video Summary")
            st.write(get_summary(transcript))

        with tab3:
            st.subheader("Identified Speakers")
            st.write("🚫 No speakers found." if speaker_metadata == "NO_SPEAKER_FOUND" else speaker_metadata)

        if speaker_metadata != "NO_SPEAKER_FOUND":
            with tab4:
                st.subheader("Speaker-wise Insights")
                full_output = extract_speaker_insights(transcript, speaker_metadata)

                if "Repeated Attributes:" in full_output:
                    insights_part, attributes_part = full_output.split("Repeated Attributes:")
                    st.markdown("#### 🧑 Speaker Insights")
                    st.markdown(insights_part.strip())
                    st.markdown("#### 🔁 Repeated Keywords")
                    st.markdown(attributes_part.strip())
                else:
                    st.markdown(full_output)

        with tab5:
            st.subheader("🎞️ Top Reel Moments")
            if not reel_timestamps:
                st.warning("❌ No high-quality reel moments were found.")
            else:
                for idx, item in enumerate(reel_timestamps):
                    st.markdown(f"**Reel {idx+1}** — `{item['start']}s to `{item['end']}s`")
                    st.write(item['text'])

                st.info("🤔 Not satisfied with the reels shown? You can try re-generating the analysis for better results.")


        with tab6:
            st.subheader("📽️ Auto-Cut Reels (FFmpeg)")

            if reel_timestamps and isinstance(reel_timestamps, list) and video_path and os.path.exists(video_path):
                for idx, item in enumerate(reel_timestamps):
                    start = round(item.get('start', 0), 2)
                    end = round(item.get('end', 0), 2)

                    if end <= start:
                        st.warning(f"⚠️ Skipping clip {idx+1}: end time <= start time")
                        continue
                    if (end - start) < 5:
                        st.warning(f"⚠️ Skipping clip {idx+1}: too short (< 5s)")
                        continue

                    clip_path = trim_and_crop_with_ffmpeg(
                        video_path, start, end, idx=idx
                    )

                    if clip_path and os.path.exists(clip_path):
                        st.video(clip_path)
                        st.markdown(f"🕒 Clip {idx+1}: `{start}s` to `{end}s`")
                    else:
                        st.error(f"❌ Failed to generate clip {idx+1}")
            else:
                st.warning("⚠️ Valid timestamps or video not available.")

            st.info("🤔 Not satisfied with the reels shown? You can try re-generating the analysis for better results.")

