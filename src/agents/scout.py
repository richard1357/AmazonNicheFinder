"""Scout Agent — discovers top products in a KDP category and filters by BSR."""

from __future__ import annotations

import statistics
from typing import TypedDict

from src.config import BSR_MAX, BSR_MIN, TOP_N_PRODUCTS
from src.data.mock_amazon import fetch_mock_products, fetch_mock_reviews
from src.db.models import insert_products, insert_reviews


class ScoutResult(TypedDict):
    keyword: str
    products: list[dict]
    median_bsr: float
    avg_price: float
    product_count: int
    est_daily_revenue: float
    est_daily_royalty: float
    reviews: list[dict]


def _estimate_daily_units(median_bsr: float) -> float:
    """Rough estimate of daily unit sales from BSR using inverse-log model."""
    if median_bsr <= 0:
        return 0.0
    import math

    return max(0.5, 100_000 / (median_bsr * math.log10(median_bsr + 1)))


def run_scout(category: str, run_id: int) -> ScoutResult:
    """Fetch products, filter by BSR, persist to DB, and return aggregated niche data."""

    raw_products = fetch_mock_products(category, count=TOP_N_PRODUCTS)

    filtered = [p for p in raw_products if BSR_MIN <= p["bsr"] <= BSR_MAX]

    if not filtered:
        filtered = raw_products[:10]

    product_ids = insert_products(run_id, filtered)

    all_reviews: list[dict] = []
    for pid, product in zip(product_ids, filtered):
        reviews = fetch_mock_reviews(product["asin"], count=10)
        insert_reviews(pid, reviews)
        all_reviews.extend(reviews)

    bsr_values = [p["bsr"] for p in filtered]
    prices = [p["price"] for p in filtered]
    median_bsr = statistics.median(bsr_values)
    avg_price = statistics.mean(prices)
    daily_units = _estimate_daily_units(median_bsr)
    est_daily_revenue = daily_units * avg_price
    est_daily_royalty = est_daily_revenue * 0.70

    three_star = [r for r in all_reviews if r["rating"] == 3]
    review_sample = three_star[:100] if three_star else all_reviews[:100]

    return ScoutResult(
        keyword=category,
        products=filtered,
        median_bsr=median_bsr,
        avg_price=round(avg_price, 2),
        product_count=len(filtered),
        est_daily_revenue=round(est_daily_revenue, 2),
        est_daily_royalty=round(est_daily_royalty, 2),
        reviews=review_sample,
    )
