
import ssl_patch 
import yt_dlp
import os
import uuid

def download_audio(youtube_url: str, output_dir: str = "outputs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    unique_id = uuid.uuid4().hex[:6]
    audio_path = f"{output_dir}/audio_{unique_id}.mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{output_dir}/audio_{unique_id}.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return audio_path
    except Exception as e:
        print(f"❌ Failed to download audio: {e}")
        return None


def download_video(youtube_url: str, output_dir: str = "outputs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    unique_id = uuid.uuid4().hex[:6]
    video_path = f"{output_dir}/video_{unique_id}.mp4"

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': video_path,
        'merge_output_format': 'mp4',
        'quiet': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return video_path if os.path.exists(video_path) else None
    except Exception as e:
        print(f"❌ Video download failed: {e}")
        return None
