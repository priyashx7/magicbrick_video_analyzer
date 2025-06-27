import re
from yt_dlp import YoutubeDL

def fetch_metadata(youtube_url):
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return {
            'title': info.get('title', ''),
            'description': info.get('description', '')
        }

