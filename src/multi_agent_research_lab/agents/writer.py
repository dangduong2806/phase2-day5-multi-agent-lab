"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState

from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.services.llm_client import LLMClient

class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self, llm_client: LLMClient):
        # Bước 1: Khởi tạo LLMClient
        self.llm_client = llm_client

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`.

        TODO(student): Synthesize a clear response with citations or source references.
        """

        # Bước 2: Kiểm tra dữ liệu đầu vào tối thiểu
        if not state.research_notes or not state.analysis_notes:
            state.errors.append("WriterAgent run failed: missing research_notes or analysis_notes.")
            return state

        # Tìm các phản hồi chỉnh sửa của Critic trong lịch sử chạy (nếu có)
        critic_feedbacks = [r.content for r in state.agent_results if r.agent == AgentName.CRITIC]
        last_critic_feedback = critic_feedbacks[-1] if critic_feedbacks else "None"

        # Định dạng danh sách nguồn để LLM in ra ở phần References
        sources_list = ""
        for idx, doc in enumerate(state.sources):
            sources_list += f"[{idx + 1}] {doc.title} - {doc.url or 'No link'}\n"

        # Bước 3: Thiết kế Prompt
        system_prompt = (
            "You are a professional technical writer. Your goal is to synthesize the provided "
            "Research Notes and Analysis Notes into a comprehensive, clear, and high-quality final report.\n\n"
            "Guidelines:\n"
            f"1. Target Audience: {state.request.audience}\n"
            "2. Keep the facts accurate according to the Research Notes.\n"
            "3. Structure the report beautifully using Markdown headings.\n"
            "4. Retain inline numerical citations (e.g. [1], [2]) corresponding to the facts.\n"
            "5. At the absolute end of the report, add a '## Sources' section listing all references provided.\n"
            "6. If Critic Feedback is provided, modify and improve your draft to address those specific issues."
        )
        user_prompt = (
            f"Research Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes}\n\n"
            f"Analysis Notes:\n{state.analysis_notes}\n\n"
            f"Sources:\n{sources_list}\n\n"
            f"Critic Feedback (if any):\n{last_critic_feedback}"
        )

        # Bước 4: Gọi LLM tổng hợp bài viết
        response = self.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Bước 5: Cập nhật state và ghi nhận kết quả
        state.final_answer = response.content
        result = AgentResult(
            agent=AgentName.WRITER,
            content=response.content,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd
            }
        )
        state.agent_results.append(result)

        state.add_trace_event(
            name="writer_completed",
            payload={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens
            }
        )
        return state

