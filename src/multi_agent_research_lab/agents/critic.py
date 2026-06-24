"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState

from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.services.llm_client import LLMClient

class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self, llm_client: LLMClient):
        # Bước 1: Khởi tạo LLMClient
        self.llm_client = llm_client

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings.

        TODO(student): Add fact-check, citation coverage, or hallucination checks.
        """

        # Bước 2: Kiểm tra sự tồn tại của câu trả lời nháp
        if not state.final_answer:
            state.errors.append("CriticAgent run failed: final_answer is missing.")
            return state
        
        # Bước 3: Thiết kế Prompt kiểm duyệt
        system_prompt = (
            "You are a rigorous Fact-Checking and Quality Assurance Agent.\n"
            "Your task is to review the draft 'Final Answer' against the provided 'Research Notes' "
            "and check for:\n"
            "1. Hallucinations (claims made in the answer that are not supported by the notes).\n"
            "2. Missing or incorrect citations.\n"
            "3. Logic flaws or errors.\n\n"
            "At the beginning of your response, you MUST output one of the following decisions:\n"
            "- [APPROVED]: If the answer is accurate, fully supported, and requires no changes.\n"
            "- [NEEDS_REVISION]: If you find inaccuracies, unsupported claims, or major formatting issues.\n\n"
            "Follow the decision with a detailed list of findings or feedback."
        )
        user_prompt = (
            f"Research Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes}\n\n"
            f"Draft Final Answer:\n{state.final_answer}"
        )

        # Bước 4: Gọi LLM
        response = self.llm_client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Bước 5: Cập nhật State và kiểm tra trạng thái phê duyệt
        critic_content = response.content
        # Kiểm tra xem có chứa từ khóa APPROVED hay không để gán nhãn
        is_approved = "[APPROVED]" in critic_content
        status = "approved" if is_approved else "needs_revision"

        # Ghi nhận kết quả
        result = AgentResult(
            agent=AgentName.CRITIC,
            content=critic_content,
            metadata={
                "status": status,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd
            }
        )
        state.agent_results.append(result)

        # Ghi vết Trace
        state.add_trace_event(
            name="critic_completed",
            payload={
                "decision": status,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens
            }
        )
        return state


