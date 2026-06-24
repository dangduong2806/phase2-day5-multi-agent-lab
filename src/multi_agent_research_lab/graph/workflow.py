"""LangGraph workflow skeleton."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState

# Import các Agents
from multi_agent_research_lab.agents import (
    SupervisorAgent,
    ResearcherAgent,
    AnalystAgent,
    WriterAgent,
    CriticAgent,
)
# Import các Clients
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient

from langgraph.graph import StateGraph, END

from typing import Any



class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(self) -> None:
        self.graph: Any = None


    def build(self) -> object:
        """Create a LangGraph graph.

        TODO(student): Implement nodes, edges, conditional routing, and stop condition.
        Suggested nodes: supervisor, researcher, analyst, writer, optional critic.
        """

        # Bước 2: Khởi tạo clients và các Agents
        llm_client = LLMClient()
        search_client = SearchClient()
        supervisor = SupervisorAgent()
        researcher = ResearcherAgent(search_client, llm_client)
        analyst = AnalystAgent(llm_client)
        writer = WriterAgent(llm_client)
        critic = CriticAgent(llm_client)

        # Khởi tạo đồ thị trạng thái ResearchState
        builder = StateGraph(ResearchState)

        # Bước 3: Đăng ký các Nodes
        builder.add_node("supervisor", supervisor.run)
        builder.add_node("researcher", researcher.run)
        builder.add_node("analyst", analyst.run)
        builder.add_node("writer", writer.run)
        builder.add_node("critic", critic.run)

        # Đặt điểm bắt đầu là Supervisor
        builder.set_entry_point("supervisor")

        # Bước 4: Thiết lập các Edges quay lại Supervisor
        builder.add_edge("researcher", "supervisor")
        builder.add_edge("analyst", "supervisor")
        builder.add_edge("writer", "supervisor")
        builder.add_edge("critic", "supervisor")

        # Định nghĩa hàm định tuyến từ Supervisor
        def route_next(state: ResearchState) -> str:
            if not state.route_history:
                return "supervisor"
            return state.route_history[-1]

        # Đăng ký cạnh điều kiện cho Supervisor
        builder.add_conditional_edges(
            "supervisor",
            route_next,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "critic": "critic",
                "done": END,
            }
        )

        # Biên dịch đồ thị
        self.graph = builder.compile()

        return self.graph
        

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state.

        TODO(student): Compile graph, invoke it, and convert result back to ResearchState.
        """

        if self.graph is None:
            self.build()

        # Bước 5: Chạy đồ thị
        # LangGraph invoke trả về kết quả trạng thái cuối cùng
        # Thêm dòng dưới đây để báo cho IDE biết self.graph chắc chắn đã khác None
        assert self.graph is not None
        # Bước 5: Chạy đồ thị
        # LangGraph invoke trả về kết quả trạng thái cuối cùng
        result = self.graph.invoke(state)
        # Đảm bảo đầu ra trả về đúng kiểu đối tượng ResearchState
        if isinstance(result, dict):
            return ResearchState(**result)
        return result