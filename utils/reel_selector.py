import os
import requests
from rapidfuzz import fuzz

def get_top_reel_chunks_from_transcript(transcript: str, n_chunks: int = 10) -> list:
    """
    Use LLM to identify the best moments from transcript for reels.
    Returns a list of exact text chunks.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OpenRouter API key not set")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a content strategist working on educational YouTube videos.

TASK:
From the transcript below, identify the top {n_chunks} most impactful educational moments suitable for Instagram or YouTube Shorts.

Instructions:
- These should be moments that convey powerful insights, lessons, or summaries.
- DO NOT summarize or write new text.
- Return the exact text as spoken (copied from transcript).
- Each output must be under 100 words.
- always there should be atleast chunks never return nothing or blank or empty
- Output exactly {n_chunks} separate transcript chunks (if available).
- Do NOT include headers like "Moment 1" or "Here are..."
Only give raw text lines.

Transcript:
{transcript}
"""

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()["choices"][0]["message"]["content"]
        chunks = [line.strip("-• ").strip() for line in content.strip().split("\n") if len(line.strip().split()) >= 5]
        return chunks[:n_chunks]
    except Exception as e:
        print("❌ Error extracting reel moments:", e)
        return []



def match_chunks_to_segments(llm_chunks: list, segments: list, threshold: int = 80) -> list:
    """
    Match each LLM-selected chunk to timestamped transcript segments.
    Return as many valid matches as possible, up to 4.
    """
    matched = []

    for chunk in llm_chunks:
        if len(chunk.strip().split()) < 5:
            continue  # Skip junk lines

        best_match = None
        best_score = 0
        match_start, match_end = None, None

        for i in range(len(segments)):
            combined = ""
            start_time = segments[i]['start']

            for j in range(i, min(i + 10, len(segments))):  # up to ~30 seconds
                combined += segments[j]['text'] + " "
                end_time = segments[j]['end']
                duration = end_time - start_time

                if duration < 28:
                    continue
                if duration > 35:
                    break

                score = fuzz.partial_ratio(chunk.lower(), combined.lower())
                if score > best_score:
                    best_score = score
                    best_match = combined.strip()
                    match_start = start_time
                    match_end = end_time

        if best_score >= threshold and (match_end - match_start) >= 28:
            matched.append({
                "start": round(match_start, 2),
                "end": round(match_end, 2),
                "text": best_match
            })

        if len(matched) == 6:
            break  # Stop at max 6

    return matched
