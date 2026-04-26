"""Gap Analyst Agent — uses Gemini (or mock) to find content gaps in reviews."""

from __future__ import annotations

import json
import logging
import os
from typing import TypedDict

from src.config import GEMINI_API_KEY, GEMINI_MODEL, LLM_MODE

logger = logging.getLogger(__name__)


class GapAnalysis(TypedDict):
    target_audience: str
    content_gaps: list[str]
    suggested_titles: list[str]
    strategy_markdown: str
    model_used: str


_SYSTEM_PROMPT = """You are an expert Kindle publishing strategist. Analyze the following customer reviews (mostly 3-star) for books in the "{category}" category.

Your task:
1. Identify the TARGET AUDIENCE — who is buying these books?
2. Find CONTENT GAPS — what are readers consistently asking for that isn't being delivered?
3. Suggest 3-5 BOOK TITLES that would fill these gaps.
4. Write a STRATEGY brief in markdown format.

Focus on actionable, specific insights. Look for patterns in complaints and requests."""

_REVIEW_TEMPLATE = """## Reviews for "{category}" Category

{reviews_text}

---
Based on these reviews, provide your analysis in the following JSON format:
{{
    "target_audience": "Description of the primary reader persona",
    "content_gaps": ["Gap 1", "Gap 2", "Gap 3", ...],
    "suggested_titles": ["Title 1", "Title 2", "Title 3", ...],
    "strategy_markdown": "## Strategy for {category}\\n\\n### Target Audience\\n...\\n\\n### Content Gaps to Fill\\n...\\n\\n### Suggested Titles\\n...\\n\\n### Recommended Approach\\n..."
}}"""


def _format_reviews(reviews: list[dict]) -> str:
    lines = []
    for i, r in enumerate(reviews, 1):
        lines.append(
            f"**Review {i}** ({r.get('rating', '?')}★): "
            f"*\"{r.get('title', '')}\"*\n"
            f"{r.get('body', 'No content')}\n"
            f"(Helpful votes: {r.get('helpful_count', 0)})\n"
        )
    return "\n".join(lines)


def _call_gemini(category: str, reviews: list[dict]) -> GapAnalysis:
    """Call Gemini API for real analysis."""
    import google.generativeai as genai

    api_key = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)

    reviews_text = _format_reviews(reviews)
    prompt = _REVIEW_TEMPLATE.format(category=category, reviews_text=reviews_text)

    response = model.generate_content(
        [
            {"role": "user", "parts": [_SYSTEM_PROMPT.format(category=category)]},
            {"role": "model", "parts": ["I understand. I'll analyze the reviews and provide structured insights about content gaps and opportunities. Please share the reviews."]},
            {"role": "user", "parts": [prompt]},
        ],
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=4096,
        ),
    )

    # --- Usage tracking ---
    usage = getattr(response, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
    output_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
    total_tokens = getattr(usage, "total_token_count", 0) if usage else 0
    logger.info(
        "Gemini usage: model=%s input_tokens=%d output_tokens=%d total_tokens=%d",
        GEMINI_MODEL, input_tokens, output_tokens, total_tokens,
    )
    _record_usage(category, input_tokens, output_tokens, total_tokens)

    text = response.text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {
            "target_audience": "Analysis available (raw text)",
            "content_gaps": [text[:200]],
            "suggested_titles": [],
            "strategy_markdown": text,
        }

    return GapAnalysis(
        target_audience=data.get("target_audience", ""),
        content_gaps=data.get("content_gaps", []),
        suggested_titles=data.get("suggested_titles", []),
        strategy_markdown=data.get("strategy_markdown", ""),
        model_used=GEMINI_MODEL,
    )


def _mock_analysis(category: str, reviews: list[dict]) -> GapAnalysis:
    """Generate a realistic mock analysis without calling any API."""
    gap_templates = {
        "Self-Help": {
            "target_audience": "Professionals aged 25-45 seeking practical personal development frameworks they can implement immediately in their daily routines.",
            "content_gaps": [
                "Lack of actionable workbook/exercise sections — readers want to practice, not just read",
                "Missing modern digital tool integrations (apps, software, AI assistants)",
                "No step-by-step implementation guides — too high-level and theoretical",
                "Outdated case studies from pre-2020 era — needs current examples",
                "No beginner on-ramp — assumes prior knowledge of personal development concepts",
            ],
            "suggested_titles": [
                "The Self-Help Workbook: 90 Days of Guided Exercises for Real Change",
                "Digital Habits: Using AI & Apps to Build Your Best Life in 2025",
                "Self-Help for Skeptics: A No-BS Step-by-Step Implementation Guide",
                "From Zero to Growth: The Complete Beginner's Personal Development System",
            ],
        },
        "Romance": {
            "target_audience": "Women aged 25-55 who read 3+ books per month and value emotional depth, diverse representation, and unique settings.",
            "content_gaps": [
                "Lack of cultural diversity in romance leads and settings",
                "Predictable plot structures — readers want subverted tropes",
                "Missing emotional depth in character development mid-book",
                "Not enough dual-POV narratives — readers want both perspectives",
                "Weak endings that feel rushed after strong openings",
            ],
            "suggested_titles": [
                "Love Across Borders: A Dual-POV Cultural Romance",
                "The Anti-Trope Love Story: When Everything Goes Sideways",
                "Slow Burn, Deep Roots: A Character-Driven Romance",
                "Second Act Romance: Love After the Plot Twist",
            ],
        },
        "Science Fiction": {
            "target_audience": "Tech-savvy readers aged 20-50 who want scientifically plausible worlds with complex characters and social commentary.",
            "content_gaps": [
                "World-building overshadows character development — readers want both",
                "Hard sci-fi that's inaccessible to casual readers",
                "Missing near-future settings — most focus on far future",
                "Lack of diverse perspectives in speculative futures",
                "Technology hand-waving without explaining societal impact",
            ],
            "suggested_titles": [
                "Tomorrow's People: A Near-Future Human Story",
                "The Accessible Universe: Sci-Fi for Everyone",
                "Coded Futures: Technology, Society, and the Human Heart",
                "2035: Five Perspectives on the World Next Door",
            ],
        },
    }

    defaults = {
        "target_audience": f"Avid readers in the {category} space looking for practical, updated, and engaging content that goes beyond surface-level treatment.",
        "content_gaps": [
            "Lack of practical exercises and downloadable resources",
            "Content feels outdated — needs 2024/2025 updates",
            "Missing step-by-step implementation guidance",
            "No companion digital resources (templates, checklists, tools)",
            "Repetitive middle sections — needs tighter editing",
        ],
        "suggested_titles": [
            f"The {category} Workbook: Hands-On Exercises for Real Results",
            f"{category} in 2025: A Modern Practical Guide",
            f"The Complete {category} Blueprint: From Beginner to Expert",
            f"{category} Toolkit: Templates, Frameworks & Action Plans",
        ],
    }

    template = gap_templates.get(category, defaults)

    strategy = f"""## 📚 Content Strategy for {category}

### 🎯 Target Audience
{template['target_audience']}

### 🔍 Content Gaps Identified
Based on analysis of reader reviews (prioritizing 3-star feedback):

"""
    for i, gap in enumerate(template["content_gaps"], 1):
        strategy += f"{i}. **{gap}**\n"

    strategy += "\n### 💡 Suggested Titles\n"
    for title in template["suggested_titles"]:
        strategy += f"- *{title}*\n"

    strategy += f"""
### 🚀 Recommended Approach
1. **Fill the Workbook Gap**: Include actionable exercises in every chapter
2. **Add Digital Companion**: Create downloadable templates and checklists
3. **Update for 2025**: Reference current tools, platforms, and trends
4. **Beginner-Friendly**: Add a foundations chapter for newcomers
5. **Tight Editing**: Aim for 200-250 pages of dense, non-repetitive content

### 📊 Market Opportunity
The {category} category shows strong demand but consistent reader frustration with existing offerings.
Books that combine practical exercises with modern, updated content have the highest potential for 4.5+ star ratings and strong BSR performance.
"""

    return GapAnalysis(
        target_audience=template["target_audience"],
        content_gaps=template["content_gaps"],
        suggested_titles=template["suggested_titles"],
        strategy_markdown=strategy,
        model_used="mock-analysis-v1",
    )


def _record_usage(
    category: str, input_tokens: int, output_tokens: int, total_tokens: int
) -> None:
    """Persist Gemini token usage to the llm_usage table."""
    try:
        from src.db.models import get_connection

        conn = get_connection()
        conn.execute(
            "INSERT INTO llm_usage (model, category, input_tokens, output_tokens, total_tokens, created_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'))",
            (GEMINI_MODEL, category, input_tokens, output_tokens, total_tokens),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("Failed to record LLM usage: %s", exc)


def get_usage_summary() -> dict:
    """Return cumulative Gemini token usage across all runs."""
    try:
        from src.db.models import get_connection

        conn = get_connection()
        row = conn.execute(
            "SELECT COUNT(*) as calls, "
            "COALESCE(SUM(input_tokens), 0) as input_tokens, "
            "COALESCE(SUM(output_tokens), 0) as output_tokens, "
            "COALESCE(SUM(total_tokens), 0) as total_tokens "
            "FROM llm_usage"
        ).fetchone()
        conn.close()
        return dict(row) if row else {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    except Exception:
        return {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0}


def run_gap_analyst(category: str, reviews: list[dict]) -> GapAnalysis:
    """Analyze reviews to find content gaps. Uses Gemini if available, mock otherwise."""
    if LLM_MODE == "gemini":
        try:
            return _call_gemini(category, reviews)
        except Exception as e:
            logger.warning("Gemini API failed (%s), falling back to mock analysis", e)
            return _mock_analysis(category, reviews)
    else:
        return _mock_analysis(category, reviews)
