"""Kindle Trend-Flywheel — Streamlit Dashboard."""

from __future__ import annotations

import ast

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.config import BSR_MAX, BSR_MIN, DATA_SOURCE, LLM_MODE
from src.data.mock_amazon import get_available_categories
from src.db.models import (
    get_gap_analysis_for_niche,
    get_niches_for_run,
    get_runs,
    get_trend_data_for_niche,
    init_db,
)
from src.workflow import run_pipeline

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Kindle Trend-Flywheel",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize DB ────────────────────────────────────────────
init_db()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.title("📚 Kindle Trend-Flywheel")
    st.caption("Automated KDP niche research tool")

    st.divider()

    st.subheader("🔍 New Research")
    categories = get_available_categories()
    selected_category = st.selectbox(
        "KDP Category",
        categories,
        help="Select a Kindle category to analyze",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("BSR Min", f"{BSR_MIN:,}")
    with col2:
        st.metric("BSR Max", f"{BSR_MAX:,}")

    run_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

    st.divider()

    st.subheader("⚙️ Configuration")
    st.info(f"**Data Source:** {DATA_SOURCE}\n\n**LLM Mode:** {LLM_MODE}")

    st.divider()

    st.subheader("📋 Past Runs")
    runs = get_runs()
    run_options = {
        f"#{r['id']} — {r['category']} ({r['status']})": r["id"]
        for r in runs
    }
    if run_options:
        selected_run_label = st.selectbox("Load previous run", list(run_options.keys()))
        selected_run_id = run_options[selected_run_label]
    else:
        st.caption("No previous runs yet.")
        selected_run_id = None

# ── Run Pipeline ─────────────────────────────────────────────
if run_btn:
    with st.spinner(f"Running analysis for **{selected_category}**..."):
        progress_bar = st.progress(0, text="Starting pipeline...")

        progress_bar.progress(10, text="🔍 Scout Agent: Fetching products...")
        result = run_pipeline(selected_category)

        progress_bar.progress(100, text="Pipeline complete!")

        if result.get("status") == "done":
            st.success(f"Analysis complete for **{selected_category}**!")
            selected_run_id = result["run_id"]
            # Refresh runs list
            st.rerun()
        else:
            st.error(f"Pipeline failed: {result.get('error', 'Unknown error')}")

# ── Main Content ─────────────────────────────────────────────
if selected_run_id:
    niches = get_niches_for_run(selected_run_id)

    if not niches:
        st.info("No niche data found for this run. Try running a new analysis.")
    else:
        # ── Tab Layout ───────────────────────────────────────
        tab1, tab2, tab3 = st.tabs([
            "📊 Opportunity Matrix",
            "📈 Deep Dive",
            "📝 Blueprint",
        ])

        # ── VIEW A: Opportunity Matrix ───────────────────────
        with tab1:
            st.header("Opportunity Matrix")
            st.caption("Niches sorted by Flywheel Score (70% BSR + 30% Trend Stability)")

            df = pd.DataFrame(niches)
            display_df = df[[
                "keyword",
                "median_bsr",
                "flywheel_score",
                "bsr_score",
                "trend_stability",
                "trend_status",
                "est_daily_revenue",
                "est_daily_royalty",
                "avg_price",
                "product_count",
            ]].copy()

            display_df.columns = [
                "Keyword",
                "Median BSR",
                "Flywheel Score",
                "BSR Score",
                "Trend Stability",
                "Trend Status",
                "Est. Daily Revenue ($)",
                "Est. Daily Royalty ($)",
                "Avg Price ($)",
                "Products",
            ]

            status_colors = {
                "stable": "🟢",
                "rising": "🔵",
                "cooling": "🟡",
                "declining": "🔴",
                "volatile": "🟠",
                "unknown": "⚪",
                "insufficient_data": "⚪",
            }
            display_df["Trend Status"] = display_df["Trend Status"].map(
                lambda x: f"{status_colors.get(x, '⚪')} {x.title()}"
            )

            st.dataframe(
                display_df.sort_values("Flywheel Score", ascending=False),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Flywheel Score": st.column_config.ProgressColumn(
                        "Flywheel Score", min_value=0, max_value=100, format="%.1f"
                    ),
                    "BSR Score": st.column_config.ProgressColumn(
                        "BSR Score", min_value=0, max_value=100, format="%.1f"
                    ),
                    "Trend Stability": st.column_config.ProgressColumn(
                        "Trend Stability", min_value=0, max_value=100, format="%.1f"
                    ),
                    "Median BSR": st.column_config.NumberColumn(format="%d"),
                    "Est. Daily Revenue ($)": st.column_config.NumberColumn(format="$%.2f"),
                    "Est. Daily Royalty ($)": st.column_config.NumberColumn(format="$%.2f"),
                    "Avg Price ($)": st.column_config.NumberColumn(format="$%.2f"),
                },
            )

            # Summary metrics
            st.divider()
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            top_niche = display_df.sort_values("Flywheel Score", ascending=False).iloc[0]
            with mcol1:
                st.metric("Top Niche", top_niche["Keyword"])
            with mcol2:
                st.metric("Best Flywheel Score", f"{top_niche['Flywheel Score']:.1f}")
            with mcol3:
                st.metric("Est. Daily Royalty", f"${top_niche['Est. Daily Royalty ($)']:.2f}")
            with mcol4:
                st.metric("Median BSR", f"{top_niche['Median BSR']:,.0f}")

        # ── VIEW B: Deep Dive ────────────────────────────────
        with tab2:
            st.header("Deep Dive: BSR vs. Google Trends")

            niche_keywords = [n["keyword"] for n in niches]
            selected_niche_kw = st.selectbox(
                "Select niche for deep dive",
                niche_keywords,
                key="deep_dive_select",
            )

            selected_niche = next(
                (n for n in niches if n["keyword"] == selected_niche_kw), None
            )

            if selected_niche:
                trend_data = get_trend_data_for_niche(selected_niche["id"])

                if trend_data:
                    trend_df = pd.DataFrame(trend_data)
                    trend_df["date"] = pd.to_datetime(trend_df["date"])

                    # Dual-axis chart
                    fig = make_subplots(specs=[[{"secondary_y": True}]])

                    fig.add_trace(
                        go.Scatter(
                            x=trend_df["date"],
                            y=trend_df["interest"],
                            name="Google Trends Interest",
                            line={"color": "#FF6B35", "width": 2},
                            fill="tozeroy",
                            fillcolor="rgba(255, 107, 53, 0.1)",
                        ),
                        secondary_y=False,
                    )

                    # Simulated BSR line (inverted — lower BSR = higher on chart)
                    bsr_base = selected_niche["median_bsr"]
                    import random

                    random.seed(42)
                    bsr_values = [
                        max(500, bsr_base + random.randint(-5000, 5000))
                        for _ in range(len(trend_df))
                    ]

                    fig.add_trace(
                        go.Scatter(
                            x=trend_df["date"],
                            y=bsr_values,
                            name="Amazon BSR (lower = better)",
                            line={"color": "#4ECDC4", "width": 2, "dash": "dot"},
                        ),
                        secondary_y=True,
                    )

                    fig.update_layout(
                        title=f"12-Month Trend: {selected_niche_kw}",
                        template="plotly_dark",
                        height=500,
                        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
                        hovermode="x unified",
                    )
                    fig.update_yaxes(
                        title_text="Google Trends Interest (0-100)",
                        secondary_y=False,
                        gridcolor="rgba(255,255,255,0.1)",
                    )
                    fig.update_yaxes(
                        title_text="Amazon BSR (inverted)",
                        secondary_y=True,
                        autorange="reversed",
                        gridcolor="rgba(255,255,255,0.05)",
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Metrics row
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Median BSR", f"{selected_niche['median_bsr']:,.0f}")
                    with col2:
                        st.metric("Flywheel Score", f"{selected_niche['flywheel_score']:.1f}")
                    with col3:
                        st.metric("Trend Status", selected_niche["trend_status"].title())
                    with col4:
                        st.metric("Avg Price", f"${selected_niche['avg_price']:.2f}")
                    with col5:
                        st.metric(
                            "Est. Daily Royalty",
                            f"${selected_niche['est_daily_royalty']:.2f}",
                        )
                else:
                    st.warning("No trend data available for this niche.")

        # ── VIEW C: Blueprint ────────────────────────────────
        with tab3:
            st.header("Strategy Blueprint")

            niche_keywords_bp = [n["keyword"] for n in niches]
            selected_bp_kw = st.selectbox(
                "Select niche for blueprint",
                niche_keywords_bp,
                key="blueprint_select",
            )

            selected_bp_niche = next(
                (n for n in niches if n["keyword"] == selected_bp_kw), None
            )

            if selected_bp_niche:
                gap = get_gap_analysis_for_niche(selected_bp_niche["id"])

                if gap:
                    # Strategy markdown
                    st.markdown(gap["strategy_markdown"])

                    st.divider()

                    # Structured data
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("🎯 Target Audience")
                        st.write(gap["target_audience"])

                        st.subheader("📊 Content Gaps")
                        try:
                            gaps_list = ast.literal_eval(gap["content_gaps"])
                        except (ValueError, SyntaxError):
                            gaps_list = [gap["content_gaps"]]
                        for i, g in enumerate(gaps_list, 1):
                            st.markdown(f"**{i}.** {g}")

                    with col2:
                        st.subheader("💡 Suggested Titles")
                        try:
                            titles_list = ast.literal_eval(gap["suggested_titles"])
                        except (ValueError, SyntaxError):
                            titles_list = [gap["suggested_titles"]]
                        for t in titles_list:
                            st.markdown(f"- *{t}*")

                        st.subheader("🤖 Model Used")
                        st.code(gap["model_used"])
                else:
                    st.info("No gap analysis available. Run the pipeline first.")

else:
    # Welcome screen
    st.title("📚 Kindle Trend-Flywheel")
    st.markdown("""
    ### Welcome to the Kindle Niche Research Tool

    This tool helps you identify **validated Kindle niches** by:

    1. **Scout Agent** — Discovers top products in a KDP category,
       filters by BSR (1,000-100,000)
    2. **📈 Validator Agent** — Cross-references keywords with Google Trends to ensure longevity
    3. **🤖 Gap Analyst** — Uses AI to analyze reviews and find content gaps

    Results are scored using the **Flywheel Score**:
    - **70%** Current Sales Performance (BSR)
    - **30%** Trend Stability (Google Trends)

    ---

    **Get started:** Select a category in the sidebar and click **Run Analysis**.
    """)

    # Show data source alternatives
    with st.expander("🔌 Supported Data Sources"):
        st.markdown("""
        | Source | Status | Description |
        |--------|--------|-------------|
        | **Mock Data** | ✅ Active | Built-in sample data for development |
        | **Rainforest API** | 🔧 Config needed | Real-time Amazon product data |
        | **Apify** | 🔧 Config needed | Web scraping platform with Amazon actors |
        | **Oxylabs** | 🔧 Config needed | E-commerce scraper API |
        | **Keepa** | 🔧 Config needed | Historical Amazon price/BSR data |
        | **Jungle Scout API** | 🔧 Config needed | KDP-focused product research |
        | **Google Trends** | 🔧 pytrends | Free via pytrends library |
        | **Gemini 1.5 Pro** | 🔧 API key needed | AI-powered review analysis |

        Set `DATA_SOURCE` and API keys in your environment to switch sources.
        """)
