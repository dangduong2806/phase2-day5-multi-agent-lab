"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentName

class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route.

        TODO(student): Implement routing policy. Suggested steps:
        - Inspect request, current notes, and missing fields.
        - Choose one of: researcher, analyst, writer, done.
        - Enforce max iterations and failure fallback.
        """
        settings = get_settings()

        # Bước 2: Kiểm tra giới hạn vòng lặp tối đa
        if state.iteration >= settings.max_iterations:
            state.errors.append("Supervisor: Reached max iterations without completion.")
            state.record_route("done")
            return state

        # Bước 3: Logic định tuyến State Machine (Rule-based)
        next_route = "done"
        if not state.research_notes:
            # 1. Thu thập thông tin trước
            next_route = AgentName.RESEARCHER
        elif not state.analysis_notes:
            # 2. Phân tích thông tin đã thu thập
            next_route = AgentName.ANALYST
        elif not state.final_answer:
            # 3. Tổng hợp thành bài viết cuối cùng
            next_route = AgentName.WRITER
        else:
            # 4. Kiểm duyệt kết quả (Tùy chọn có sử dụng Critic)
            # Kiểm tra xem agent vừa chạy gần nhất có phải Critic hay không
            critic_results = [r for r in state.agent_results if r.agent == AgentName.CRITIC]
            
            if not critic_results:
                # Nếu chưa có phản biện nào, chuyển sang Critic để duyệt
                next_route = AgentName.CRITIC
            else:
                # Nếu đã có phản biện, xem xét đánh giá mới nhất của Critic
                last_critic_result = critic_results[-1]
                status = last_critic_result.metadata.get("status")
                
                if status == "needs_revision":
                    # Nếu Critic yêu cầu sửa đổi, quay lại Writer để chỉnh sửa bài viết
                    next_route = AgentName.WRITER
                else:
                    # Nếu được chấp thuận (approved) hoặc trạng thái khác, kết thúc quy trình
                    next_route = "done"
        # Bước 4: Cập nhật lịch sử định tuyến và ghi nhận trace
        state.record_route(next_route)
        
        state.add_trace_event(
            name="supervisor_routing",
            payload={
                "next_route": next_route,
                "iteration": state.iteration,
                "route_history": state.route_history
            }
        )
        return state
        



