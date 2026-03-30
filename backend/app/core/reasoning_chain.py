"""Reasoning chain — to be implemented in Phase 3."""

import json
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

SYSTEM_PROMPT = """You are a finanical analysis AI. Given recent price data and news articels for a stock,
analyze the information and return a structure JSON belief state.

Your response must be valid JSON with exactly this shape:
{
  "conviction": <float 0.0-1.0, where 0=max bearish, 0.5=neutral, 1.0=max bullish>,
  "thesis": "<2-3 sentence summary of your current view on this asset>",
  "key_factors": [
    {"factor": "<factor name>", "signal": "<bullish|bearish|neutral>", "weight": <0.0-1.0>}
  ],
  "evidence_refs": ["<article_id>", ...]
}

Return only the JSON object - no markdown, no explanation.
"""


def build_prompt(context: dict) -> str:
    asset_id = context["asset_id"]
    prices = context["prices"]
    articles = context["articles"]
    current_belief = context["current_belief"]

    price_summary = "\n".join(
        f"{p['time']}: open={p['open']} high={p['high']} low={p['low']} close={p['close']} vol={p['volume']}"
        for p in prices[:7]
    ) or "No recent price data."

    article_summary = "\n".join(
        f"[{a['id']}] ({a['published_at']}) {a['source']}: {a['title']} — {a['summary'] or 'No summary.'}"
        for a in articles
    ) or "No recent articles."

    prior = (
        f"Current conviction: {current_belief['conviction']}\nCurrent thesis: {current_belief['thesis']}"
        if current_belief
        else "No prior belief — this is the first analysis."
    )

    return f"""{SYSTEM_PROMPT}

    Asset: {asset_id}

    --- Prior Belief ---
    {prior}

    --- Recent Prices (last 7 days) ---
    {price_summary}

    --- Relevant News Articles ---
    {article_summary}

    Analyze the above and return an updated belief state as JSON."""

def run_reasoning_chain(context: dict) -> dict:
    """Call Gemini Flash and parse the belief state from the response."""
    prompt = build_prompt(context)
    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown code fences if Gemini wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())

