import os
import sys

# Add src to python path so we can import multi_agent_research_lab
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report


def baseline_runner(query: str) -> ResearchState:
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    llm_client = LLMClient()
    system_prompt = (
        "You are a helpful research assistant. Answer the user's research query comprehensively, "
        "providing clear explanation and details where possible."
    )
    response = llm_client.complete(system_prompt, query)
    state.final_answer = response.content
    
    # Create a mock agent result to record token costs
    from multi_agent_research_lab.core.schemas import AgentName, AgentResult
    state.agent_results.append(
        AgentResult(
            agent=AgentName.WRITER,
            content=response.content,
            metadata={
                "cost_usd": response.cost_usd or 0.0,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens
            }
        )
    )
    return state


def multi_agent_runner(query: str) -> ResearchState:
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)


def main() -> None:
    queries = [
        "Research GraphRAG state-of-the-art and write a 500-word summary",
        "Explain multi-agent systems and their trade-offs compared to single-agent"
    ]
    
    metrics = []
    
    print("Running benchmarks...")
    for q in queries:
        print(f"\nQuery: {q}")
        
        # Run Baseline
        print("-> Running Single-Agent Baseline...")
        try:
            state_base, metric_base = run_benchmark("Baseline", q, baseline_runner)
            metrics.append(metric_base)
            print(f"   Done. Latency: {metric_base.latency_seconds:.2f}s")
        except Exception as e:
            print(f"   Baseline failed: {e}")
            
        # Run Multi-Agent
        print("-> Running Multi-Agent Workflow...")
        try:
            state_multi, metric_multi = run_benchmark("Multi-Agent", q, multi_agent_runner)
            metrics.append(metric_multi)
            print(f"   Done. Latency: {metric_multi.latency_seconds:.2f}s, Iterations: {state_multi.iteration}")
        except Exception as e:
            print(f"   Multi-Agent failed: {e}")
            
    # Render report
    report_md = render_markdown_report(metrics)
    
    # Save to reports/benchmark_report.md
    os.makedirs("reports", exist_ok=True)
    report_path = "reports/benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"\nBenchmark completed successfully! Report saved to {report_path}")


if __name__ == "__main__":
    main()
