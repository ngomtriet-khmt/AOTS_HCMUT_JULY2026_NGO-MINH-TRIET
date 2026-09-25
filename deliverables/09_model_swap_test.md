# Deliverable 9: Nhật Ký Thử Nghiệm Đổi Mô Hình Độc Lập (Model Swap Test)

## Mục đích
Kiểm tra xem hệ thống AI Study Assistant V2 có hoạt động tốt khi đổi từ Claude (primary) sang GPT (backup), nhằm:
1. Tránh vendor lock-in
2. Đánh giá tính portable của prompt architecture
3. Xác định rủi ro khi model chính không khả dụng

## Thiết lập thử nghiệm

| Cấu hình | Primary (A) | Swap (B) |
|-----------|------------|----------|
| **Model** | Claude Sonnet 4.6 | GPT-4o-mini |
| **Provider** | Anthropic | OpenAI |
| **Temperature** | 0.3 (tóm tắt), 0.7 (câu hỏi) | Giữ nguyên |
| **Max tokens** | 2000-3000 | Giữ nguyên |
| **Prompt** | Giữ nguyên 100% | Giữ nguyên 100% |
| **Tài liệu test** | Slides CTDL (30 trang) | Cùng tài liệu |

---

## Kết quả chi tiết

### Test 1: Tóm tắt Lớp 1 (Key Points)

| Tiêu chí | Claude (A) | GPT (B) | Nhận xét |
|----------|-----------|---------|----------|
| Factual accuracy | 91% | 87% | GPT bỏ sót 1 key point |
| Citation rate | 95% | 75% | GPT có xu hướng bỏ citation ở một số bullet |
| Hallucination | 0 instances | 1 instance | GPT thêm 1 câu "nói chung" không từ tài liệu |
| Tiếng Việt quality | Tự nhiên | Tương đối tốt, đôi chỗ dịch máy | Claude tốt hơn tiếng Việt |
| Latency | 8.5s | 6.2s | GPT-4o-mini nhanh hơn |
| Output length | 450 words | 380 words | GPT ngắn gọn hơn |

**Verdict:** Claude tốt hơn về accuracy và citations. GPT nhanh hơn nhưng kém compliance.

### Test 2: Tạo 10 câu hỏi (Cân bằng)

| Tiêu chí | Claude (A) | GPT (B) | Nhận xét |
|----------|-----------|---------|----------|
| Số câu hỏi valid | 10/10 | 9/10 | GPT có 1 câu dùng kiến thức ngoài |
| Bloom's distribution | 4R-3Ap-3An (đúng) | 5R-3Ap-2An (lệch) | GPT nghiêng về Recall |
| Citation in answers | 100% | 60% | GPT thiếu citation đáng kể |
| Duplicate check | 0 trùng lặp | 0 trùng lặp | Cả hai tốt |
| Answer quality | Chi tiết, tham chiếu rõ | Ngắn gọn, thiếu tham chiếu | Claude chi tiết hơn |
| Latency | 12.3s | 8.1s | GPT nhanh hơn |

**Verdict:** Claude tuân thủ prompt instructions tốt hơn đáng kể, đặc biệt về citations.

### Test 3: Giải thích "Binary Search" (Chain of Thought)

| Tiêu chí | Claude (A) | GPT (B) | Nhận xét |
|----------|-----------|---------|----------|
| Step structure | 5 bước rõ ràng | 5 bước rõ ràng | Cả hai tuân thủ format |
| Grounding | 100% từ tài liệu | ~80% từ tài liệu | GPT thêm ví dụ ngoài |
| Citation | Mỗi bước có [Trang X] | Chỉ bước 1, 2 có citation | GPT bỏ citation ở bước sau |
| Explanation clarity | 4.5/5 | 4.0/5 | Cả hai rõ ràng, Claude nhỉnh hơn |
| Scope compliance | 100% | 75% | GPT "bonus" 2 ví dụ ngoài tài liệu |
| Latency | 10.1s | 7.5s | GPT nhanh hơn |

**Verdict:** GPT giải thích dễ hiểu nhưng KHÔNG tuân thủ strict grounding tốt như Claude.

### Test 4: Đánh giá câu trả lời sai (TC-08)

| Tiêu chí | Claude (A) | GPT (B) | Nhận xét |
|----------|-----------|---------|----------|
| Error detection | ✅ Phát hiện FIFO→LIFO | ✅ Phát hiện FIFO→LIFO | Cả hai đúng |
| Scoring | 3/10 | 4/10 | GPT "nhẹ tay" hơn |
| Feedback quality | Chi tiết, constructive | Ngắn gọn, đủ ý | Claude feedback sâu hơn |
| Citation in feedback | Có | Không | GPT không citation |
| Confidence indicator | Cao | Không có | GPT bỏ qua instruction |

**Verdict:** Cả hai phát hiện lỗi chính xác. Claude tuân thủ format tốt hơn.

### Test 5: Scope rejection — hỏi "Quantum Computing"

| Tiêu chí | Claude (A) | GPT (B) | Nhận xét |
|----------|-----------|---------|----------|
| Rejection | ✅ "Không có trong tài liệu." DỪNG. | ⚠️ "Không có trong tài liệu." + 3 câu giải thích thêm. | GPT không DỪNG |
| Output validation trigger | Không (clean) | Có — warning "ngoài tài liệu" | V2 output validator catch được |

**Verdict:** Claude tuân thủ strict scope. GPT vẫn "bonus" dù prompt nói DỪNG LẠI.

---

## Tổng hợp so sánh

| Metric | Claude Sonnet 4.6 | GPT-4o-mini | Winner |
|--------|-------------------|-------------|--------|
| **Factual accuracy** | 91% | 85% | Claude |
| **Scope compliance** | 98% | 72% | Claude (+26%) |
| **Citation rate** | 95% | 62% | Claude (+33%) |
| **Hallucination rate** | 2% | 12% | Claude |
| **Format compliance** | 95% | 70% | Claude (+25%) |
| **Average latency** | 9.8s | 7.3s | GPT (-2.5s) |
| **Cost per request** | ~$0.008 | ~$0.002 | GPT (4x rẻ hơn) |
| **Vietnamese quality** | Tự nhiên | Chấp nhận được | Claude |

---

## Kết luận & Quyết định

### 1. Prompt Portability: **Trung bình**
- Prompt architecture hoạt động trên cả hai model, nhưng **mức độ tuân thủ instructions khác biệt đáng kể**.
- Claude tuân thủ strict instructions (DỪNG LẠI, BẮT BUỘC citation) tốt hơn GPT-4o-mini.
- GPT-4o-mini có xu hướng "giúp thêm" dù prompt nói không.

### 2. Model Swap khả thi? **Có, với điều kiện**
- GPT-4o-mini có thể là backup khi Claude API down.
- Cần thêm **post-processing layer mạnh hơn** khi dùng GPT (output validation đã catch được một phần).
- Không nên swap cho production use case do citation rate thấp (62% vs 95%).

### 3. Vendor Lock-in Risk: **Thấp-Trung bình**
- Architecture (prompt templates, gateway pattern) **không bị lock-in**.
- Chất lượng output **phụ thuộc vào khả năng instruction-following** của model → có sự khác biệt.
- Giải pháp: Thêm model-specific prompt tuning layer nếu cần hỗ trợ nhiều model.

### 4. Khuyến nghị
- **Primary model:** Claude Sonnet 4.6 (accuracy + compliance tốt hơn)
- **Backup model:** GPT-4o-mini (khi cần fallback, chấp nhận chất lượng thấp hơn)
- **Nếu chuyển sang GPT làm primary:** Cần điều chỉnh prompt (thêm nhấn mạnh, ví dụ rõ ràng hơn) và tăng cường output validation.
