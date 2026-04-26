"""Application configuration — loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

# ---------- Paths ----------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "kindle_flywheel.db"
SQLITE_URL = f"sqlite:///{DB_PATH}"

# ---------- API Keys (set via env or .env) ----------
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
RAINFOREST_API_KEY: str = os.environ.get("RAINFOREST_API_KEY", "")
APIFY_API_KEY: str = os.environ.get("APIFY_API_KEY", "")

# ---------- Defaults ----------
DEFAULT_ZIP = "10001"  # US zip for Amazon locale
BSR_MIN = 1_000
BSR_MAX = 100_000
TOP_N_PRODUCTS = 50

# ---------- Scoring Weights ----------
BSR_WEIGHT = 0.70
TREND_WEIGHT = 0.30

# ---------- Data Source Mode ----------
# "mock" | "rainforest" | "apify" | "oxylabs"
DATA_SOURCE: str = os.environ.get("DATA_SOURCE", "mock")

# ---------- LLM Mode ----------
# "gemini" | "mock"
LLM_MODE: str = "gemini" if GEMINI_API_KEY else "mock"
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
