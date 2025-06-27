import os
import requests

def get_summary(transcript: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a summarization assistant.

TASK:
- Summarize the following transcript in key bullet points only in any hindi or english language.
- Highlight only the most important insights discussed.
- The insight should be concise and informative and less than 200 words

Transcript:
{transcript}
    """

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Summary Error:", e)
        return "Error generating summary."
