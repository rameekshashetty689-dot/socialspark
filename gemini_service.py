import json
import os
import re

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Add GEMINI_API_KEY=your_key to your .env file."
        )
    return genai.Client(api_key=api_key)


def generate_post_ideas(objective, num_ideas=7, platforms=None, tone="Friendly", **kwargs):
    """Ask Gemini for social media post ideas based on a campaign objective.

    Returns a list of dicts: [{"title": ..., "caption": ...}, ...]
    """
    if isinstance(platforms, (list, tuple)):
        platforms = ", ".join(platforms)
    platforms = platforms or "Instagram, Facebook, LinkedIn"

    prompt = f"""You are a social media marketing expert.
Campaign objective: {objective}
Platforms: {platforms}
Tone: {tone}

Create {num_ideas} different social media post ideas.
Return ONLY a JSON array, no extra text, no markdown fences.
Each item must have exactly these keys:
"title": a short idea title,
"caption": a ready-to-post caption with relevant hashtags.
"""

    client = _get_client()
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    text = (response.text or "").strip()

    # Remove ```json fences if the model adds them
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()

    try:
        ideas = json.loads(text)
        if isinstance(ideas, dict):
            ideas = [ideas]
        return ideas
    except json.JSONDecodeError:
        # Fallback: treat each non-empty line as an idea
        lines = [ln.strip("-* \t") for ln in text.splitlines() if ln.strip()]
        return [{"title": f"Idea {i + 1}", "caption": ln} for i, ln in enumerate(lines)]