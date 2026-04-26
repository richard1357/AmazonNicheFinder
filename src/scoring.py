"""Flywheel Score calculation — the primary ranking metric."""

from __future__ import annotations

import math

from src.config import BSR_WEIGHT, TREND_WEIGHT


def normalize_bsr(median_bsr: float, bsr_min: float = 1_000, bsr_max: float = 100_000) -> float:
    """Convert BSR to a 0-100 score. Lower BSR = higher score."""
    if median_bsr <= bsr_min:
        return 100.0
    if median_bsr >= bsr_max:
        return 0.0
    log_min = math.log10(bsr_min)
    log_max = math.log10(bsr_max)
    log_bsr = math.log10(median_bsr)
    return round(((log_max - log_bsr) / (log_max - log_min)) * 100, 2)


def compute_flywheel_score(
    bsr_score: float,
    trend_stability: float,
    bsr_weight: float = BSR_WEIGHT,
    trend_weight: float = TREND_WEIGHT,
) -> float:
    """Weighted composite score: 70% BSR performance + 30% trend stability."""
    return round(bsr_weight * bsr_score + trend_weight * trend_stability, 2)


def estimate_daily_units(median_bsr: float) -> float:
    """Estimate daily unit sales from BSR using inverse-log model."""
    if median_bsr <= 0:
        return 0.0
    return max(0.5, round(100_000 / (median_bsr * math.log10(median_bsr + 1)), 2))


def estimate_daily_royalty(
    daily_units: float, avg_price: float, royalty_rate: float = 0.70
) -> float:
    """Estimated daily royalty = units × price × royalty_rate."""
    return round(daily_units * avg_price * royalty_rate, 2)
