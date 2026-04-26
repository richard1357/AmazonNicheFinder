"""Tests for scoring module."""

from src.scoring import (
    compute_flywheel_score,
    estimate_daily_royalty,
    estimate_daily_units,
    normalize_bsr,
)


def test_normalize_bsr_low():
    score = normalize_bsr(1_000)
    assert score == 100.0


def test_normalize_bsr_high():
    score = normalize_bsr(100_000)
    assert score == 0.0


def test_normalize_bsr_mid():
    score = normalize_bsr(10_000)
    assert 0 < score < 100


def test_normalize_bsr_below_min():
    score = normalize_bsr(500)
    assert score == 100.0


def test_normalize_bsr_above_max():
    score = normalize_bsr(200_000)
    assert score == 0.0


def test_flywheel_score_all_bsr():
    score = compute_flywheel_score(bsr_score=100, trend_stability=0)
    assert score == 70.0


def test_flywheel_score_all_trend():
    score = compute_flywheel_score(bsr_score=0, trend_stability=100)
    assert score == 30.0


def test_flywheel_score_balanced():
    score = compute_flywheel_score(bsr_score=50, trend_stability=50)
    assert score == 50.0


def test_estimate_daily_units():
    units = estimate_daily_units(10_000)
    assert units > 0


def test_estimate_daily_units_zero_bsr():
    units = estimate_daily_units(0)
    assert units == 0.0


def test_estimate_daily_royalty():
    royalty = estimate_daily_royalty(10, 9.99)
    assert abs(royalty - 10 * 9.99 * 0.70) < 0.01
