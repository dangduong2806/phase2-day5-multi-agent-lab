"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


# Bước 1: Mock Database chứa dữ liệu nghiên cứu mẫu
MOCK_DATABASE = [
    {
        "title": "Introduction to Multi-Agent Systems",
        "url": "https://example.com/multi-agent-intro",
        "snippet": "A multi-agent system (MAS) is a computerized system composed of multiple interacting intelligent agents. MAS can solve problems that are difficult or impossible for an individual agent or a monolithic system to solve."
    },
    {
        "title": "LangGraph: Orchestrating Multi-Agent Workflows",
        "url": "https://example.com/langgraph-orchestration",
        "snippet": "LangGraph is a library designed for building stateful, multi-actor applications with LLMs. It allows developers to define agents as nodes and transitions as edges, enabling complex agent loops and conditional routing."
    },
    {
        "title": "Single-Agent vs Multi-Agent Systems Trade-offs",
        "url": "https://example.com/agent-tradeoffs",
        "snippet": "While single-agent systems are simple and fast to implement, multi-agent systems excel in complex task decomposition, parallel processing, and collaborative error correction. However, they introduce higher latency and token cost."
    },
    {
        "title": "Prompt Engineering Best Practices for LLM Agents",
        "url": "https://example.com/prompt-engineering",
        "snippet": "Designing robust prompts for LLM agents requires specifying clear roles, output structures, and constraint descriptions. System prompts define agent identity (e.g., researcher, critic) while user prompts feed input context."
    },
    {
        "title": "Agentic RAG and Semantic Search",
        "url": "https://example.com/agentic-rag",
        "snippet": "Agentic Retrieval-Augmented Generation (RAG) uses agents to dynamically formulate search queries, evaluate retrieved documents, and decide whether more searches are needed before generating the final answer."
    }
]

class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.

        TODO(student): Implement with Tavily, Bing, SerpAPI, internal docs, or a local mock.
        """

        """Search for mock documents relevant to a query using simple keyword scoring."""
        # Chuẩn hóa từ khóa tìm kiếm
        query_words = query.lower().split()
        results = []
        # Bước 2: Duyệt tìm kiếm và tính điểm
        for doc in MOCK_DATABASE:
            score = 0
            title_lower = doc["title"].lower()
            snippet_lower = doc["snippet"].lower()
            for word in query_words:
                if len(word) > 2:  # Bỏ qua từ quá ngắn như 'is', 'to', 'in'
                    if word in title_lower:
                        score += 3  # Ưu tiên khớp tiêu đề
                    if word in snippet_lower:
                        score += 1
            if score > 0:
                results.append((score, doc))
        # Sắp xếp kết quả theo điểm số giảm dần
        results.sort(key=lambda x: x[0], reverse=True)
        # Bước 3: Đóng gói thành danh sách SourceDocument
        selected_docs = [
            SourceDocument(
                title=item["title"],
                url=item["url"],
                snippet=item["snippet"]
            )
            for _, item in results[:max_results]
        ]
        # Dự phòng: Nếu không tìm thấy kết quả nào, trả về các nguồn mặc định đầu tiên
        if not selected_docs:
            selected_docs = [
                SourceDocument(
                    title=item["title"],
                    url=item["url"],
                    snippet=item["snippet"]
                )
                for item in MOCK_DATABASE[:max_results]
            ]
        return selected_docs