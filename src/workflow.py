"""LangGraph state machine — orchestrates Scout → Validator → Gap Analyst pipeline."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph

from src.agents.gap_analyst import run_gap_analyst
from src.agents.scout import run_scout
from src.agents.validator import run_validator
from src.db.models import (
    create_run,
    finish_run,
    insert_gap_analysis,
    insert_niche,
    insert_trend_data,
)
from src.scoring import compute_flywheel_score, normalize_bsr


def _merge_lists(left: list, right: list) -> list:
    return left + right


class PipelineState(TypedDict):
    category: str
    run_id: int
    scout_results: list[dict]
    validated_niches: list[dict]
    gap_analyses: list[dict]
    status: str
    error: str
    progress_messages: Annotated[list[str], _merge_lists]


def scout_node(state: PipelineState) -> dict:
    """Run the Scout Agent to discover products."""
    category = state["category"]
    run_id = state["run_id"]

    try:
        result = run_scout(category, run_id)
        return {
            "scout_results": [dict(result)],
            "progress_messages": [
                f"Scout: Found {result['product_count']} products in '{category}'"
            ],
        }
    except Exception as e:
        return {
            "scout_results": [],
            "status": "failed",
            "error": f"Scout failed: {e}",
            "progress_messages": [f"Scout error: {e}"],
        }


def validator_node(state: PipelineState) -> dict:
    """Run the Validator Agent on each scouted niche."""
    validated = []

    for scout in state["scout_results"]:
        keyword = scout["keyword"]
        trend_result = run_validator(keyword, use_live=False)

        bsr_score = normalize_bsr(scout["median_bsr"])
        flywheel = compute_flywheel_score(bsr_score, trend_result["trend_stability"])

        niche_data = {
            **scout,
            "trend_score": trend_result["trend_score"],
            "trend_status": trend_result["trend_status"],
            "trend_stability": trend_result["trend_stability"],
            "trend_data": trend_result["trend_data"],
            "bsr_score": bsr_score,
            "flywheel_score": flywheel,
        }
        validated.append(niche_data)

    return {
        "validated_niches": validated,
        "progress_messages": [
            f"Validator: Analyzed trends for {len(validated)} niche(s)"
        ],
    }


def gap_analyst_node(state: PipelineState) -> dict:
    """Run the Gap Analyst on validated niches."""
    analyses = []
    run_id = state["run_id"]

    for niche in state["validated_niches"]:
        niche_id = insert_niche(run_id, niche)

        if niche.get("trend_data"):
            insert_trend_data(niche_id, niche["trend_data"])

        reviews = niche.get("reviews", [])
        gap = run_gap_analyst(niche["keyword"], reviews)

        insert_gap_analysis(niche_id, dict(gap))

        analyses.append({
            "niche_id": niche_id,
            "keyword": niche["keyword"],
            **dict(gap),
        })

    return {
        "gap_analyses": analyses,
        "status": "done",
        "progress_messages": [
            f"Gap Analyst: Generated strategies for {len(analyses)} niche(s)"
        ],
    }


def should_continue(state: PipelineState) -> str:
    """Route based on current status."""
    if state.get("status") == "failed":
        return END
    return "validator"


def should_analyze(state: PipelineState) -> str:
    """Route after validation."""
    if not state.get("validated_niches"):
        return END
    return "gap_analyst"


def build_workflow() -> StateGraph:
    """Construct the LangGraph pipeline."""
    graph = StateGraph(PipelineState)

    graph.add_node("scout", scout_node)
    graph.add_node("validator", validator_node)
    graph.add_node("gap_analyst", gap_analyst_node)

    graph.set_entry_point("scout")
    graph.add_conditional_edges("scout", should_continue, {"validator": "validator", END: END})
    graph.add_conditional_edges(
        "validator", should_analyze, {"gap_analyst": "gap_analyst", END: END}
    )
    graph.add_edge("gap_analyst", END)

    return graph


def run_pipeline(category: str) -> dict:
    """Execute the full pipeline for a category and return final state."""
    run_id = create_run(category)

    graph = build_workflow()
    app = graph.compile()

    initial_state: PipelineState = {
        "category": category,
        "run_id": run_id,
        "scout_results": [],
        "validated_niches": [],
        "gap_analyses": [],
        "status": "running",
        "error": "",
        "progress_messages": [],
    }

    try:
        final_state = app.invoke(initial_state)
        finish_run(run_id, status=final_state.get("status", "done"))
        return final_state
    except Exception as e:
        finish_run(run_id, status="failed")
        raise RuntimeError(f"Pipeline failed: {e}") from e
