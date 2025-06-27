
import os
import requests

def extract_speaker_insights(transcript: str, speaker_metadata: str = "") -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "🔒 OPENROUTER_API_KEY not set"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Extract speaker names from metadata if present
    speaker_list = ""
    if "—" in speaker_metadata:
        speaker_lines = [line.strip() for line in speaker_metadata.split("\n") if "—" in line]
        if speaker_lines:
            speaker_list = "\n".join(speaker_lines)

    prompt = f"""
You are an assistant analyzing a conversation transcript.

TASKS:
1. For each speaker, extract 2–3 key insights or points they made.
2. If real names are mentioned (like "Rina Kaurab" or "Mr. Winitanda"), use them.
3. Use this speaker list for reference if needed:
{speaker_list}

4. Then identify **important attributes or keywords** (e.g., "Sector 150", "infrastructure", "affordability") that are:
   - Repeated multiple times by the same or different speaker
   - Business, location, or strategy specific
   - Write how many times each was mentioned and by whom (use real names instead of "Speaker 1" if possible)

📄 Format the output as:

Speaker Insights:
Rina Kaurab:
- Insight 1
- Insight 2
...

Repeated Attributes:
• Sector 150 — mentioned 7 times by Rina Kaurab
• Golf Course Road — mentioned 4 times by Mr. Winitanda
• Affordability — mentioned 3 times by Shweta Kapoor

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
        print("❌ Speaker Insight Error:", e)
        return "Error extracting speaker insights."
