"""SQLite database models for Kindle Trend-Flywheel."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.config import DB_PATH


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            category        TEXT    NOT NULL,
            status          TEXT    NOT NULL DEFAULT 'pending',
            created_at      TEXT    NOT NULL,
            finished_at     TEXT
        );

        CREATE TABLE IF NOT EXISTS products (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
            asin            TEXT    NOT NULL,
            title           TEXT    NOT NULL,
            author          TEXT    DEFAULT '',
            price           REAL    DEFAULT 0.0,
            bsr             INTEGER NOT NULL,
            rating          REAL    DEFAULT 0.0,
            review_count    INTEGER DEFAULT 0,
            category        TEXT    DEFAULT '',
            kindle_unlimited BOOLEAN DEFAULT 0,
            image_url       TEXT    DEFAULT '',
            fetched_at      TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS niches (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
            keyword         TEXT    NOT NULL,
            median_bsr      REAL    NOT NULL,
            avg_price       REAL    DEFAULT 0.0,
            product_count   INTEGER DEFAULT 0,
            est_daily_revenue REAL  DEFAULT 0.0,
            est_daily_royalty REAL  DEFAULT 0.0,
            trend_score     REAL    DEFAULT 0.0,
            trend_status    TEXT    DEFAULT 'unknown',
            flywheel_score  REAL    DEFAULT 0.0,
            bsr_score       REAL    DEFAULT 0.0,
            trend_stability REAL    DEFAULT 0.0,
            created_at      TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS trend_data (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            niche_id        INTEGER NOT NULL REFERENCES niches(id) ON DELETE CASCADE,
            date            TEXT    NOT NULL,
            interest        REAL    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS bsr_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            date            TEXT    NOT NULL,
            bsr             INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            reviewer        TEXT    DEFAULT '',
            rating          INTEGER NOT NULL,
            title           TEXT    DEFAULT '',
            body            TEXT    DEFAULT '',
            date            TEXT    DEFAULT '',
            helpful_count   INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS gap_analyses (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            niche_id        INTEGER NOT NULL REFERENCES niches(id) ON DELETE CASCADE,
            target_audience TEXT    DEFAULT '',
            content_gaps    TEXT    DEFAULT '[]',
            suggested_titles TEXT   DEFAULT '[]',
            strategy_markdown TEXT  DEFAULT '',
            model_used      TEXT    DEFAULT '',
            created_at      TEXT    NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_products_run ON products(run_id);
        CREATE INDEX IF NOT EXISTS idx_niches_run ON niches(run_id);
        CREATE INDEX IF NOT EXISTS idx_niches_score ON niches(flywheel_score DESC);
        CREATE INDEX IF NOT EXISTS idx_trend_data_niche ON trend_data(niche_id);
        CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
        """
    )
    conn.commit()
    conn.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_run(category: str, db_path: Path = DB_PATH) -> int:
    conn = get_connection(db_path)
    cur = conn.execute(
        "INSERT INTO runs (category, status, created_at) VALUES (?, 'running', ?)",
        (category, _now()),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id  # type: ignore[return-value]


def finish_run(run_id: int, status: str = "done", db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    conn.execute(
        "UPDATE runs SET status = ?, finished_at = ? WHERE id = ?",
        (status, _now(), run_id),
    )
    conn.commit()
    conn.close()


def insert_products(run_id: int, products: list[dict], db_path: Path = DB_PATH) -> list[int]:
    conn = get_connection(db_path)
    ids = []
    for p in products:
        cur = conn.execute(
            """INSERT INTO products
               (run_id, asin, title, author, price, bsr, rating, review_count,
                category, kindle_unlimited, image_url, fetched_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                p["asin"],
                p["title"],
                p.get("author", ""),
                p.get("price", 0.0),
                p["bsr"],
                p.get("rating", 0.0),
                p.get("review_count", 0),
                p.get("category", ""),
                p.get("kindle_unlimited", False),
                p.get("image_url", ""),
                _now(),
            ),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    conn.close()
    return ids  # type: ignore[return-value]


def insert_niche(run_id: int, niche: dict, db_path: Path = DB_PATH) -> int:
    conn = get_connection(db_path)
    cur = conn.execute(
        """INSERT INTO niches
           (run_id, keyword, median_bsr, avg_price, product_count,
            est_daily_revenue, est_daily_royalty, trend_score, trend_status,
            flywheel_score, bsr_score, trend_stability, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            run_id,
            niche["keyword"],
            niche["median_bsr"],
            niche.get("avg_price", 0.0),
            niche.get("product_count", 0),
            niche.get("est_daily_revenue", 0.0),
            niche.get("est_daily_royalty", 0.0),
            niche.get("trend_score", 0.0),
            niche.get("trend_status", "unknown"),
            niche.get("flywheel_score", 0.0),
            niche.get("bsr_score", 0.0),
            niche.get("trend_stability", 0.0),
            _now(),
        ),
    )
    niche_id = cur.lastrowid
    conn.commit()
    conn.close()
    return niche_id  # type: ignore[return-value]


def insert_trend_data(niche_id: int, data_points: list[dict], db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    conn.executemany(
        "INSERT INTO trend_data (niche_id, date, interest) VALUES (?, ?, ?)",
        [(niche_id, d["date"], d["interest"]) for d in data_points],
    )
    conn.commit()
    conn.close()


def insert_reviews(product_id: int, reviews: list[dict], db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    conn.executemany(
        """INSERT INTO reviews (product_id, reviewer, rating, title, body, date, helpful_count)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                product_id,
                r.get("reviewer", ""),
                r["rating"],
                r.get("title", ""),
                r.get("body", ""),
                r.get("date", ""),
                r.get("helpful_count", 0),
            )
            for r in reviews
        ],
    )
    conn.commit()
    conn.close()


def insert_gap_analysis(niche_id: int, analysis: dict, db_path: Path = DB_PATH) -> int:
    conn = get_connection(db_path)
    cur = conn.execute(
        """INSERT INTO gap_analyses
           (niche_id, target_audience, content_gaps, suggested_titles,
            strategy_markdown, model_used, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            niche_id,
            analysis.get("target_audience", ""),
            str(analysis.get("content_gaps", [])),
            str(analysis.get("suggested_titles", [])),
            analysis.get("strategy_markdown", ""),
            analysis.get("model_used", ""),
            _now(),
        ),
    )
    analysis_id = cur.lastrowid
    conn.commit()
    conn.close()
    return analysis_id  # type: ignore[return-value]


def get_niches_for_run(run_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM niches WHERE run_id = ? ORDER BY flywheel_score DESC", (run_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_trend_data_for_niche(niche_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM trend_data WHERE niche_id = ? ORDER BY date", (niche_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_gap_analysis_for_niche(niche_id: int, db_path: Path = DB_PATH) -> dict | None:
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT * FROM gap_analyses WHERE niche_id = ? ORDER BY created_at DESC LIMIT 1",
        (niche_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_products_for_run(run_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM products WHERE run_id = ? ORDER BY bsr ASC", (run_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_runs(db_path: Path = DB_PATH) -> list[dict]:
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM runs ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_reviews_for_product(product_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM reviews WHERE product_id = ? ORDER BY rating ASC", (product_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
