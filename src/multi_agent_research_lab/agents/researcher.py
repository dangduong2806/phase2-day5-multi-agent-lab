"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState

from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self, search_client: SearchClient, llm_client: LLMClient):
        # Bước 1: Khởi tạo các services cần thiết
        self.search_client = search_client
        self.llm_client = llm_client

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`.

        TODO(student): Implement search, source filtering, citation capture, and notes.
        """

        # Bước 2: Thực hiện tìm kiếm thông tin
        query = state.request.query
        max_sources = state.request.max_sources

        try:
            # Thực hiện tìm kiếm và lưu kết quả vào state.sources
            sources = self.search_client.search(query, max_results=max_sources)
            state.sources = sources
        except Exception as e:
            state.errors.append(f"ResearcherAgent search failed: {str(e)}")
            return state
        
        if not state.sources:
            state.research_notes = "No relevant search sources could be found."
            return state

        # Bước 3: Định dạng kết quả tìm kiếm cho Prompt
        formatted_sources = ""
        for idx, doc in enumerate(state.sources):
            formatted_sources += f"[{idx + 1}] Title: {doc.title}\nURL: {doc.url}\nSnippet: {doc.snippet}\n\n"
        system_prompt = (
            "You are an objective academic researcher. Your task is to review the provided search results "
            "and write concise, factual research notes addressing the user query.\n"
            "CRITICAL: You must cite the source index (e.g. [1], [2]) whenever you make a claim based "
            "on a document. Do not invent facts."
        )
        user_prompt = (
            f"Research Query: {query}\n\n"
            f"Search Results:\n{formatted_sources}"
        )

        # Bước 4: Gọi LLM tổng hợp ghi chú
        response = self.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Bước 5: Cập nhật state và tracking
        state.research_notes = response.content
        result = AgentResult(
            agent=AgentName.RESEARCHER,
            content=response.content,
            metadata={
                "num_sources": len(state.sources),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd
            }
        )
        state.agent_results.append(result)

        state.add_trace_event(
            name="researcher_completed",
            payload={
                "num_sources": len(state.sources),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens
            }
        )
        return state
