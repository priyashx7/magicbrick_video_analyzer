# magicbrick_video_analyzer

## What It Does
MBTV-Analyzer takes a YouTube video link from the MBTV channel and fully analyzes it to extract structured insights from the content.

## What It Extracts
- Transcript of the full video
- Summary of the video content
- Speakers identified in the video
- Speaker insights and key attributes
- Key talking points shared by the speaker
- LinkedIn social profile of the speaker

## Logic Used
- Fetched transcript directly from YouTube captions to speed up processing and avoid redundant transcription
- If captions unavailable, used OpenAI Whisper (tiny model) to transcribe audio locally as fallback
- Used meta-llama/llama-3-8b-instruct via OpenRouter to generate video summary and extract speaker insights from transcript and metadata
- Fetched YouTube video title and description to identify potential speaker names
- Searched speaker names on LinkedIn via Google search to give multiple profile options and avoid incorrect matches
- Identified high-quality reel-worthy chunks from transcript using LLM
- Used fuzzy matching via rapidfuzz to map text chunks back to original timestamps
- Used FFmpeg to trim original video based on matched timestamps
- Displayed all final clips under a dedicated tab for viewing or downloading short reels

## Tools & Libraries
- Streamlit — interactive web app UI
- yt-dlp — downloads YouTube video and audio
- YouTube Transcript API — fetches native YouTube captions
- Whisper (OpenAI Whisper) — fallback transcription if captions unavailable
- OpenRouter API — video summarization, speaker extraction, speaker insights
- FFmpeg — trims top moments and creates downloadable video reels
- tiktoken / openai / requests — LLM communication and token estimation
- os / glob / shutil — file cleanup and folder operations
- requests + xml.etree.ElementTree — parses captions via proxy in XML format
- .streamlit/secrets.toml — stores OpenRouter API key securely
- requirements.txt — dependency locking and deployment
