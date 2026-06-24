"""Benchmark skeleton for single-agent vs multi-agent."""

import re

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

from multi_agent_research_lab.services.llm_client import LLMClient

Runner = Callable[[str], ResearchState]

def evaluate_quality_with_llm(query: str, answer: str) -> float:
    """Optional: Use an LLM as a judge to grade the output quality (0-10)."""
    if not answer:
        return 0.0
        
    llm_client = LLMClient()
    system_prompt = (
        "You are an objective AI evaluator. Rate the quality of the provided research answer "
        "relative to the user query on a scale from 0.0 to 10.0.\n"
        "Consider factors like: clarity, structure, completeness, and formatting.\n"
        "Output ONLY the numeric score (e.g., 8.5) and nothing else."
    )
    user_prompt = f"Query: {query}\n\nAnswer:\n{answer}"
    
    try:
        response = llm_client.complete(system_prompt, user_prompt)
        score_match = re.search(r"(\d+(\.\d+)?)", response.content)
        if score_match:
            score = float(score_match.group(1))
            return min(max(score, 0.0), 10.0)
    except Exception:
        pass
    return 5.0 # Mặc định điểm trung bình nếu LLM lỗi

def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object.

    TODO(student): Add quality scoring, estimated token cost, citation coverage, and error rate.
    """

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started

    # Bước 1: Tính toán chi phí ước tính
    total_cost = 0.0
    for res in state.agent_results:
        total_cost += res.metadata.get("cost_usd") or 0.0

    # Bước 2: Tính toán độ bao phủ trích dẫn
    cited_indices = set()
    if state.final_answer:
        matches = re.findall(r"\[(\d+)\]", state.final_answer)
        cited_indices = {int(m) for m in matches}
    total_sources = len(state.sources)
    valid_citations = {idx for idx in cited_indices if 1 <= idx <= total_sources}
    citation_coverage = len(valid_citations) / total_sources if total_sources > 0 else 0.0

    # Bước 3: Đánh giá điểm chất lượng (Dùng LLM Judge hoặc Heuristic)
    quality_score = 0.0
    if state.final_answer and not state.errors:
        quality_score = evaluate_quality_with_llm(query, state.final_answer)

    
    # Bước 4: Tạo Ghi chú (Notes)
    notes = f"Iterations: {state.iteration}. Sources: {total_sources}. Citations Coverage: {citation_coverage:.1%}."
    if state.errors:
        notes += f" Errors: {', '.join(state.errors)}"
    
    # Bước 5: Trả về Kết quả
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=quality_score,
        notes=notes
    )
    
    return state, metrics
