"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

import time
from multi_agent_research_lab.services.llm_client import LLMClient

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    # state.final_answer = (
    #     "Baseline skeleton response. TODO(student): replace this with a real single-agent "
    #     "implementation and record latency/cost/quality metrics."
    # )
    # Bước 2: Khởi tạo LLMClient và thiết lập Prompt
    llm_client = LLMClient()
    
    system_prompt = (
        "You are a helpful research assistant. Answer the user's research query comprehensively, "
        "providing clear explanation and details where possible."
    )
    user_prompt = request.query
    console.print(f"[bold blue]Starting Single-Agent Baseline for query:[/bold blue] {query}\n")
    
    # Bước 3: Gọi LLM và đo thời gian
    start_time = time.perf_counter()
    try:
        response = llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        end_time = time.perf_counter()
        
        # Cập nhật kết quả vào state
        state.final_answer = response.content
        latency = end_time - start_time
        
        # Bước 4: Hiển thị kết quả & thông số đo lường ra màn hình
        console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Output", border_style="green"))
        
        metrics_info = (
            f"[bold green]Metrics Summary:[/bold green]\n"
            f"- Latency: {latency:.2f} seconds\n"
            f"- Input Tokens: {response.input_tokens or 'N/A'}\n"
            f"- Output Tokens: {response.output_tokens or 'N/A'}\n"
            f"- Estimated Cost: ${response.cost_usd or 0.0:.6f}"
        )
        console.print(Panel(metrics_info, title="Performance Benchmark"))
        
    except StudentTodoError:
        console.print(
            "[bold yellow]Note:[/bold yellow] LLMClient.complete raises StudentTodoError. "
            "Please implement LLMClient before running this baseline.",
            style="yellow"
        )
    # console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
