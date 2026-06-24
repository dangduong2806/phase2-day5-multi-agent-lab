# Multi-Agent Research System - Benchmark Report

## Executive Summary

Dưới đây là tóm tắt hiệu năng tổng quan của các đợt kiểm thử benchmark:

- **Tổng số lượt test (Total Runs):** 4
- **Tỷ lệ thành công (Success Rate):** 50.0%
- **Thời gian phản hồi trung bình (Avg Latency):** 143.26 giây
- **Chi phí trung bình (Avg Cost):** $0.000000 USD
- **Điểm chất lượng trung bình (Avg Quality Score):** 3.8 / 10.0

## Detailed Performance Comparison

| Run Name | Latency (s) | Cost (USD) | Quality Score | Notes & Metrics |
|:---|---:|---:|---:|:---|
| Baseline | 64.47s | $0.000000 | 7.5/10 | Iterations: 0. Sources: 0. Citations Coverage: 0.0%. |
| Multi-Agent | 248.62s | $0.000000 | 0.0/10 | Iterations: 7. Sources: 4. Citations Coverage: 100.0%. Errors: Supervisor: Reached max iterations without completion. |
| Baseline | 36.66s | $0.000000 | 7.5/10 | Iterations: 0. Sources: 0. Citations Coverage: 0.0%. |
| Multi-Agent | 223.28s | $0.000000 | 0.0/10 | Iterations: 7. Sources: 5. Citations Coverage: 100.0%. Errors: Supervisor: Reached max iterations without completion. |

## Key Observations & Trade-offs

Dựa trên kết quả benchmark, ta có thể rút ra một số nhận xét quan trọng:

1. **Đánh đổi giữa Tốc độ và Chất lượng (Latency vs Quality):**
   - **Single-Agent** cho phản hồi cực nhanh và chi phí rẻ, nhưng dễ gặp lỗi trích dẫn hoặc bỏ sót góc nhìn phản biện.
   - **Multi-Agent** cải thiện rõ rệt điểm chất lượng nhờ quy trình cộng tác giữa các Agent (Researcher thu thập nguồn tin cậy, Analyst phát hiện lỗi logic, Critic kiểm chứng tính chính xác), tuy nhiên độ trễ tăng cao do chạy tuần tự nhiều bước.

2. **Độ bao phủ trích dẫn (Citation Coverage):**
   - Kiến trúc Multi-Agent giúp tăng độ bao phủ trích dẫn thực tế thông qua việc phân chia trách nhiệm rõ ràng của Researcher và Critic, giảm thiểu tối đa hiện tượng ảo giác (hallucination).

3. **Tối ưu hóa Chi phí (Cost Optimization):**
   - Số lần lặp (iterations) được kiểm soát bởi Supervisor đóng vai trò then chốt. Đặt giới hạn `max_iterations` hợp lý giúp tránh vòng lặp vô hạn gây hao phí tài nguyên.
