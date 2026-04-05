import json
import os
from typing import Any, Dict, List

from openai import OpenAI
from pydantic import BaseModel, ValidationError


class CreatorBrief(BaseModel):
    summary: str
    recommendations: List[str]


def _fallback_creator_brief(analysis: Dict[str, Any]) -> Dict[str, Any]:
    summary = analysis.get("summary", {})
    sponsorship = analysis.get("sponsorship", {})
    duration = analysis.get("duration_patterns", [])
    keywords = analysis.get("keyword_patterns", [])

    best_duration = max(duration, key=lambda x: x.get("avg_engagement_rate", 0.0), default={})
    best_keyword = max(keywords, key=lambda x: x.get("avg_engagement_rate", 0.0), default={})

    recommendations = [
        (
            f"Use a comparison format with clear ranking verdicts around the "
            f"{best_duration.get('duration_bucket', '3-10m')} range."
        ),
        (
            f"Include high-signal language like '{best_keyword.get('keyword', 'best')}' "
            f"in the title and early hook."
        ),
    ]

    if sponsorship.get("sponsored_avg_views", 0) > sponsorship.get("organic_avg_views", 0):
        recommendations.append(
            "If using a sponsor, place the ad read after early value delivery (roughly mid-video)."
        )
    else:
        recommendations.append(
            "Prioritize an organic-feeling story arc and keep sponsor language minimal in the title."
        )

    return {
        "summary": (
            f"Sampled {summary.get('num_videos', 0)} videos. The strongest performance pattern "
            f"is concentrated in {best_duration.get('duration_bucket', 'mid-length')} videos with "
            f"keyword framing around '{best_keyword.get('keyword', 'best')}'."
        ),
        "recommendations": recommendations[:4],
    }


def generate_creator_brief(analysis: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_creator_brief(analysis)

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 4,
            },
        },
        "required": ["summary", "recommendations"],
        "additionalProperties": False,
    }

    try:
        response = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a YouTube food content analyst. You will receive structured data "
                        "about a food topic. Write a creator brief with: (1) a 2-3 sentence summary "
                        "of what patterns you found, (2) 3-4 specific actionable recommendations for "
                        "a creator making a video on this topic. Be concrete and mention formats, "
                        "title ideas, ideal length, and where to place a sponsor if relevant. "
                        "Ground everything in the numbers provided. "
                        "Return JSON matching this schema exactly: "
                        + json.dumps(schema)
                    ),
                },
                {"role": "user", "content": json.dumps(analysis)},
            ],
            temperature=0.4,
        )

        content = response.choices[0].message.content or "{}"
        parsed = CreatorBrief.model_validate(json.loads(content))
        return parsed.model_dump()
    except (ValidationError, json.JSONDecodeError, Exception):
        return _fallback_creator_brief(analysis)


def chat_with_analysis_context(
    topic: str,
    analysis: Dict[str, Any],
    history: List[Dict[str, str]],
    message: str,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "Chat is running in fallback mode because OPENAI_API_KEY is not set. "
            "I can still summarize: ask about top videos, duration patterns, sponsorship, "
            "or creator recommendations."
        )

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    messages = [
        {
            "role": "system",
            "content": (
                "You are ViralBite, a creator strategy assistant. Answer only using the provided "
                "analysis context for the topic. If information is missing, say so clearly and "
                "suggest what metric would help. Keep answers concise and practical.\n\n"
                f"TOPIC: {topic}\n"
                f"ANALYSIS_JSON: {json.dumps(analysis)}"
            ),
        }
    ]

    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content or ""
