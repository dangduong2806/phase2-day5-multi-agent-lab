"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.services.llm_client import LLMClient

class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self, llm_client: LLMClient):
        # Bước 1: Lưu trữ LLMClient cho agent
        self.llm_client = llm_client

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`.

        TODO(student): Extract key claims, compare viewpoints, and flag weak evidence.
        """
        # Bước 2: Kiểm tra dữ liệu đầu vào
        if not state.research_notes:
            state.analysis_notes = "No research notes available to analyze."
            state.errors.append("AnalystAgent run failed: research_notes is empty.")
            return state
        
        # Bước 3: Thiết kế Prompt
        system_prompt = (
            "You are a critical research analyst. Your task is to analyze raw research notes, "
            "extract key claims, compare different viewpoints, and flag any weak evidence or "
            "missing information. Format your output clearly using Markdown."
        )

        user_prompt = (
            f"Research Query: {state.request.query}\n\n"
            f"Raw Research Notes:\n{state.research_notes}"
        )

        # Bước 4: Gọi LLMClient
        response = self.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Bước 5: Cập nhật state, lịch sử chạy (AgentResult) và trace event
        state.analysis_notes = response.content
        result = AgentResult(
            agent=AgentName.ANALYST,
            content=response.content,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd
            }
        )

        state.agent_results.append(result)
        state.add_trace_event(
            name="analyst_completed",
            payload={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd
            }
        )
        return state






        
