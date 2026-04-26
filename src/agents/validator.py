"""Validator Agent — checks Google Trends for keyword stability."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import TypedDict


class TrendResult(TypedDict):
    trend_score: float
    trend_status: str
    trend_stability: float
    trend_data: list[dict]


def _generate_mock_trend_data(keyword: str) -> list[dict]:
    """Generate 12 months of mock trend data."""
    data_points = []
    base_date = datetime.now() - timedelta(days=365)
    base_interest = random.randint(40, 80)

    for week in range(52):
        date = base_date + timedelta(weeks=week)
        noise = random.uniform(-10, 10)
        seasonal = 5 * (1 if week % 13 < 6 else -1)
        trend_drift = random.uniform(-0.5, 0.8) * (week / 52)
        interest = max(0, min(100, base_interest + noise + seasonal + trend_drift))
        data_points.append({
            "date": date.strftime("%Y-%m-%d"),
            "interest": round(interest, 1),
        })

    return data_points


def _calculate_stability(data_points: list[dict]) -> tuple[float, str]:
    """Calculate trend stability score and status.

    Returns (stability_score 0-100, status_label).
    - Compares recent 13 weeks vs prior 13 weeks
    - Checks for terminal decline (>40% drop)
    """
    values = [d["interest"] for d in data_points]
    if len(values) < 26:
        return 50.0, "insufficient_data"

    recent = values[-13:]
    prior = values[-26:-13]

    avg_recent = sum(recent) / len(recent)
    avg_prior = sum(prior) / len(prior)

    if avg_prior == 0:
        change_pct = 0.0
    else:
        change_pct = ((avg_recent - avg_prior) / avg_prior) * 100

    import statistics as stats

    cv = stats.stdev(values) / max(stats.mean(values), 1) * 100

    stability = max(0, min(100, 70 - abs(change_pct) + (30 - cv)))

    if change_pct < -40:
        status = "declining"
    elif change_pct < -15:
        status = "cooling"
    elif change_pct > 15:
        status = "rising"
    elif cv > 40:
        status = "volatile"
    else:
        status = "stable"

    return round(stability, 1), status


def run_validator(keyword: str, use_live: bool = False) -> TrendResult:
    """Query Google Trends (or mock) and return stability analysis.

    When use_live=True and pytrends is available, attempts real Google Trends query.
    Falls back to mock data on failure.
    """
    trend_data: list[dict] = []

    if use_live:
        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl="en-US", tz=360)
            pytrends.build_payload([keyword], timeframe="today 12-m", geo="US")
            df = pytrends.interest_over_time()

            if not df.empty and keyword in df.columns:
                for idx, row in df.iterrows():
                    trend_data.append({
                        "date": idx.strftime("%Y-%m-%d"),
                        "interest": float(row[keyword]),
                    })
        except Exception:
            trend_data = []

    if not trend_data:
        trend_data = _generate_mock_trend_data(keyword)

    stability, status = _calculate_stability(trend_data)

    trend_score = stability

    return TrendResult(
        trend_score=trend_score,
        trend_status=status,
        trend_stability=stability,
        trend_data=trend_data,
    )
