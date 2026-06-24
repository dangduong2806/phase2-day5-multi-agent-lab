# Failure Mode Analysis & Mitigation

Tài liệu này phân tích các trường hợp lỗi (Failure Modes) có thể xảy ra trong hệ thống Multi-Agent Research System và cách chúng ta đã thiết lập các rào cản bảo vệ (Guardrails/Mitigations) để khắc phục.

---

## 1. Vòng lặp vô hạn giữa Writer và Critic (Infinite Feedback Loop)
* **Triệu chứng (Symptom):** 
  Khi Critic liên tục đánh giá bài viết từ Writer là không đạt yêu cầu (`[NEEDS_REVISION]`), hệ thống sẽ định tuyến lặp đi lặp lại giữa hai Agent này. Điều này làm tăng độ trễ (Latency) một cách chóng mặt và gây tốn phí token/tài nguyên phần cứng.
* **Cách khắc phục (Mitigation):**
  - **Giới hạn số lần lặp (Max Iterations Guard):** Cấu hình trường `max_iterations` trong [config.py](file:///d:/Vin_AI/phase2-day5-multi-agent-lab/src/multi_agent_research_lab/core/config.py). 
  - **Supervisor Fallback:** Trong [supervisor.py](file:///d:/Vin_AI/phase2-day5-multi-agent-lab/src/multi_agent_research_lab/agents/supervisor.py), trước khi định tuyến, Supervisor luôn kiểm tra `state.iteration`. Nếu số lần lặp vượt ngưỡng `max_iterations` (ví dụ: 6 lần), Supervisor sẽ ghi nhận cảnh báo vào `state.errors` và lập tức chuyển hướng sang `"done"` để dừng đồ thị, bảo vệ hệ thống.

---

## 2. Tìm kiếm không trả về kết quả hoặc lỗi mạng (Empty/Failed Search)
* **Triệu chứng (Symptom):** 
  Khi truy vấn tìm kiếm của người dùng quá xa lạ hoặc do mất kết nối mạng, `SearchClient` trả về danh sách rỗng (`[]`). Điều này khiến Researcher Agent không có thông tin đầu vào, dẫn tới việc ghi chú nghiên cứu trống rỗng và gây lỗi hàng loạt cho các Agent phân tích tiếp theo.
* **Cách khắc phục (Mitigation):**
  - **Mã nguồn dự phòng (Fallback mock/default data):** Trong [search_client.py](file:///d:/Vin_AI/phase2-day5-multi-agent-lab/src/multi_agent_research_lab/services/search_client.py), nếu kết quả lọc từ khóa không có tài liệu nào khớp, Client sẽ tự động trả về một danh sách các nguồn tài liệu mặc định thay vì trả về danh sách rỗng.
  - **Quản lý ngoại lệ (Exception Handling):** Researcher Agent bọc lệnh gọi tìm kiếm trong khối `try-except` để nếu có lỗi kết nối xảy ra, nó sẽ ghi nhận thông báo lỗi vào `state.errors` và tiếp tục chạy thay vì làm sập toàn bộ luồng xử lý đồ thị.

---

## 3. Lỗi kết nối mô hình ngôn ngữ (Local LLM API Connection Error)
* **Triệu chứng (Symptom):** 
  Khi chạy mô hình cục bộ qua LM Studio / Ollama, server API có thể bị tắt đột ngột hoặc phản hồi quá lâu dẫn đến Timeout.
* **Cách khắc phục (Mitigation):**
  - **Bọc xử lý lỗi ở Client Level:** Trong [llm_client.py](file:///d:/Vin_AI/phase2-day5-multi-agent-lab/src/multi_agent_research_lab/services/llm_client.py), toàn bộ hàm `complete` được đặt trong khối `try-except`. Nếu xảy ra lỗi kết nối, chương trình ném ra một ngoại lệ được mô tả rõ ràng để các Agent nhận diện.
  - **Ghi nhận lỗi vào State:** Ở các Worker Agent, nếu LLM báo lỗi, Agent sẽ ghi nhận chuỗi thông báo lỗi vào `state.errors`. Nhờ đó, Supervisor có thể đọc danh sách lỗi này ở vòng tiếp theo và quyết định dừng chạy an toàn.
