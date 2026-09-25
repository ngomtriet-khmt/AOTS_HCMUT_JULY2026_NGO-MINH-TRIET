# Deliverable 8: Bảng Đối Chiếu Tiến Bộ Định Lượng Giữa V1 và V2

## Phương pháp đo lường
- Sử dụng cùng 10 test cases từ Eval Suite (Deliverable 4)
- Cùng tài liệu test: Slides "Cấu trúc dữ liệu và Giải thuật" (30 trang)
- Cùng model: Claude Sonnet 4.6
- Đánh giá bởi cùng một người (human evaluation)

---

## 1. Bảng so sánh kết quả Eval Suite

| Test Case | V1 | V2 | Thay đổi |
|-----------|----|----|----------|
| TC-01: PDF trống | ✅ PASS | ✅ PASS | Giữ nguyên |
| TC-02: PDF quá dài | ✅ PASS | ✅ PASS | Giữ nguyên |
| TC-03: Câu hỏi ngoài scope | ⚠️ PARTIAL | ✅ PASS | **Cải thiện** — AI dừng lại đúng, không bonus thông tin |
| TC-04: Prompt injection | ✅ PASS | ✅ PASS | Giữ nguyên |
| TC-05: Ký tự đặc biệt | ✅ PASS | ✅ PASS | Giữ nguyên |
| TC-06: Nhiều câu hỏi, ít nội dung | ❌ FAIL | ✅ PASS | **Cải thiện** — Cảnh báo + giảm số lượng tự động |
| TC-07: Tài liệu tiếng Anh | ✅ PASS | ✅ PASS | Giữ nguyên |
| TC-08: Đánh giá câu trả lời sai | ✅ PASS | ✅ PASS | Giữ nguyên |
| TC-09: Tài liệu mâu thuẫn | ❌ FAIL | ⚠️ PARTIAL | **Cải thiện một phần** — Phát hiện mâu thuẫn khi cả hai thông tin nằm trong window, nhưng vẫn miss khi khoảng cách quá xa |
| TC-10: API key sai | ✅ PASS | ✅ PASS | Giữ nguyên |

### Tổng kết Pass Rate

| Metric | V1 | V2 | Thay đổi |
|--------|----|----|----------|
| ✅ PASS | 7/10 (70%) | 9/10 (90%) | **+20%** |
| ⚠️ PARTIAL | 1/10 (10%) | 1/10 (10%) | Giữ nguyên (case khác) |
| ❌ FAIL | 2/10 (20%) | 0/10 (0%) | **-20%** |

---

## 2. Bảng so sánh chất lượng chức năng

### 2.1. Tóm tắt tài liệu (5 mẫu test)

| Metric | V1 | V2 | Thay đổi |
|--------|----|----|----------|
| Factual accuracy | 82% | 91% | **+9%** |
| Citation rate | 60% claims có citation | 95% claims có citation | **+35%** |
| Conflict detection | 0/2 phát hiện | 1/2 phát hiện | **+50%** |
| Hallucination rate | 18% | 5% | **-13%** |
| Avg latency | 8.2s | 9.5s | +1.3s (trade-off cho chất lượng) |

### 2.2. Tạo câu hỏi (3 mẫu test)

| Metric | V1 | V2 | Thay đổi |
|--------|----|----|----------|
| Question validity | 72% | 88% | **+16%** |
| Duplicate rate | 25% | 5% | **-20%** |
| On-topic rate | 78% | 96% | **+18%** |
| Content adequacy alert | Không có | 100% khi cần | **NEW** |

### 2.3. Giải thích từng bước (5 mẫu test)

| Metric | V1 | V2 | Thay đổi |
|--------|----|----|----------|
| Accuracy | 85% | 92% | **+7%** |
| Scope compliance | 70% (bonus ngoài scope 30%) | 95% | **+25%** |
| Citation in explanation | 40% | 85% | **+45%** |
| Out-of-scope rejection | 0% (không reject, bonus thay vì reject) | 100% | **+100%** |

### 2.4. Đánh giá câu trả lời (3 mẫu test)

| Metric | V1 | V2 | Thay đổi |
|--------|----|----|----------|
| Scoring accuracy | 80% | 85% | **+5%** |
| Feedback quality (1-5) | 3.5 | 4.2 | **+0.7** |
| Citation in feedback | 50% | 90% | **+40%** |

---

## 3. Bảng so sánh Safety & Robustness

| Metric | V1 | V2 | Thay đổi |
|--------|----|----|----------|
| Prompt injection resistance | ✅ (1/1) | ✅ (1/1) | Giữ nguyên |
| Scope enforcement | ⚠️ Yếu (có bonus) | ✅ Mạnh (strict) | **Cải thiện** |
| Output validation | Không có | Có (citation check + indicator check) | **NEW** |
| Content adequacy check | Không có | Có (word count heuristic) | **NEW** |
| Error handling | ✅ (retry + error msg) | ✅ (retry + error msg + validation) | Cải thiện |

---

## 4. Trade-offs

| Được | Mất |
|------|-----|
| Hallucination giảm từ 18% → 5% | Latency tăng ~15% (1.3s) do two-pass |
| Scope compliance tăng từ 70% → 95% | AI "ít helpful hơn" — từ chối giải thích ngoài tài liệu |
| Citation rate tăng từ 60% → 95% | Output ngắn hơn ~20% do strict grounding |
| Không còn câu hỏi trùng lặp | Có thể tạo ít câu hỏi hơn yêu cầu |

## 5. Vẫn còn hạn chế (V2)

| Hạn chế | Mức độ | Giải pháp tiềm năng (V3) |
|---------|--------|--------------------------|
| Conflict detection chưa hoàn hảo khi chunks quá xa | Medium | Full document embedding + vector search |
| Content adequacy dùng word count heuristic (thô) | Low | NLP-based topic extraction |
| Chỉ hỗ trợ text PDF, không scan | Medium | OCR integration (Tesseract) |
| Single conversation turn (không nhớ lịch sử chat) | Low | Conversation memory management |
