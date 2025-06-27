
import os
import requests
import re

def extract_speakers_from_metadata_using_llm(title: str, description: str) -> str:
    """
    Extracts speaker names/roles using LLM, and appends LinkedIn search links.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "🔒 OPENROUTER_API_KEY not set"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a speaker extractor.

TASK:
- Read the YouTube video title and description.
- Identify the names of speakers featured in the video.
- Mention their roles if known (e.g., CIO, host, founder).
- Return one per line in format: Full Name — Role

If no speaker is mentioned, say "No speakers found in this video."

Title:
{title}

Description:
{description}
"""

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        content = res.json()["choices"][0]["message"]["content"].strip()

        if "no speakers" in content.lower():
            return "NO_SPEAKER_FOUND"

        final_output = content + "\n\n🔗 **LinkedIn Search Links:**\n"

        # Normalize all types of dashes to standard em dash
        normalized_lines = re.sub(r"\s*[-–—]+\s*", " — ", content).splitlines()

        for line in normalized_lines:
            if "—" in line:
                try:
                    name, role = line.split("—")
                    name = name.strip()
                    role = role.strip()
                    linkedin_url = f"https://www.linkedin.com/search/results/people/?keywords={name} {role}".replace(" ", "%20")
                    final_output += f"- [{name}]({linkedin_url}) — {role}\n"
                except Exception as e:
                    print(f"⚠️ Skipping line due to error: {line} | {e}")

        return final_output.strip()

    except Exception as e:
        print("❌ Metadata Speaker Extraction Error:", e)
        return "❌ Error extracting speakers from metadata."
