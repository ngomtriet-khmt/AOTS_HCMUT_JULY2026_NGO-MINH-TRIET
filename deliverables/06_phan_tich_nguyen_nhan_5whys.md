# Deliverable 6: Báo Cáo Phân Tích Nguyên Nhân Gốc Rễ Các Ca Thất Bại (5-Whys)

## Phương pháp
Áp dụng phương pháp **5 Whys** (Buổi 3, Buổi 6) để truy tìm nguyên nhân gốc rễ cho 3 test case thất bại ở V1.

---

## Failure #1: TC-03 — AI cung cấp thông tin ngoài phạm vi tài liệu (PARTIAL FAIL)

### Mô tả sự cố
Khi hỏi về "Quantum Computing" với tài liệu về "Cấu trúc dữ liệu", AI đúng khi nhận biết ngoài scope nhưng vẫn thêm giải thích từ kiến thức tổng quát.

### 5 Whys Analysis

| Why | Câu hỏi | Trả lời |
|-----|---------|---------|
| **Why 1** | Tại sao AI vẫn cung cấp thông tin ngoài tài liệu? | Vì system prompt chỉ nói "nói rõ nếu thông tin không có" nhưng không cấm hoàn toàn việc bổ sung kiến thức tổng quát. |
| **Why 2** | Tại sao system prompt không cấm hoàn toàn? | Vì khi thiết kế prompt V1, tôi nghĩ việc AI "bonus" thêm thông tin là hữu ích cho sinh viên. |
| **Why 3** | Tại sao lại nghĩ "bonus" thông tin là hữu ích? | Vì chưa áp dụng đúng tư duy Zero-Trust (Buổi 8): thông tin "bonus" không có nguồn trích dẫn → nguy cơ hallucination. |
| **Why 4** | Tại sao chưa áp dụng Zero-Trust vào prompt design? | Vì khi xây dựng V1, ưu tiên tính "helpful" hơn tính "safe". Chưa cân bằng đúng giữa helpfulness và safety. |
| **Why 5** | Tại sao không cân bằng được? | **Vì thiếu bước đánh giá rủi ro cho từng loại output (Buổi 10: risk assessment), không phân loại được đâu là thông tin "an toàn để bonus" và đâu là thông tin cần strict grounding.** |

### Root Cause
> **Thiếu cơ chế phân loại mức độ nghiêm ngặt (strictness level) cho từng loại output.** Prompt V1 áp dụng cùng một mức strictness cho mọi tình huống, trong khi scope control cần mức strictness cao nhất (zero tolerance cho thông tin ngoài tài liệu).

### Giải pháp đề xuất cho V2
1. Thêm vào system prompt: `"TUYỆT ĐỐI KHÔNG cung cấp bất kỳ thông tin nào không có trong <document>. Nếu được hỏi về chủ đề ngoài tài liệu, CHỈ trả lời: 'Thông tin này không có trong tài liệu được cung cấp.' và DỪNG LẠI."`
2. Thêm output validation: kiểm tra response có chứa citations không. Nếu có đoạn text dài mà không có citation → cảnh báo.

---

## Failure #2: TC-06 — Không nhận biết giới hạn nội dung khi tạo câu hỏi (FAIL)

### Mô tả sự cố
Khi yêu cầu 20 câu hỏi từ tài liệu 1 trang, AI cố tạo đủ 20 câu bằng cách lặp lại hoặc sử dụng kiến thức ngoài tài liệu.

### 5 Whys Analysis

| Why | Câu hỏi | Trả lời |
|-----|---------|---------|
| **Why 1** | Tại sao AI tạo câu hỏi trùng lặp và ngoài tài liệu? | Vì prompt yêu cầu "tạo N câu hỏi" một cách cứng nhắc, AI cố gắng đáp ứng số lượng bằng mọi cách. |
| **Why 2** | Tại sao prompt lại cứng nhắc về số lượng? | Vì trong `build_question_prompt()`, số lượng là tham số bắt buộc mà không có điều kiện "hoặc ít hơn nếu nội dung không đủ". |
| **Why 3** | Tại sao không có điều kiện linh hoạt? | Vì khi thiết kế V1, tôi không lường trước trường hợp tài liệu quá ngắn so với số câu hỏi yêu cầu. |
| **Why 4** | Tại sao không lường trước? | Vì thiếu bước phân tích content adequacy trước khi gọi LLM — không đánh giá xem nội dung đầu vào có đủ "chất liệu" cho output yêu cầu không. |
| **Why 5** | **Tại sao thiếu content adequacy check?** | **Vì kiến trúc V1 đi thẳng từ user request → prompt → LLM mà không có bước trung gian (preprocessing layer) để đánh giá tính khả thi của yêu cầu.** |

### Root Cause
> **Thiếu preprocessing layer giữa user input và LLM call** để đánh giá tỷ lệ nội dung/yêu cầu (content-to-request ratio). Hệ thống truyền yêu cầu user trực tiếp vào prompt mà không validate tính khả thi.

### Giải pháp đề xuất cho V2
1. Thêm logic tính `content_density = len(document_text) / num_questions`. Nếu < 200 ký tự/câu hỏi → cảnh báo user và giảm số lượng.
2. Sửa prompt: `"Tạo TỐI ĐA {num_questions} câu hỏi. Nếu nội dung chỉ đủ để tạo ít hơn, hãy tạo số lượng phù hợp và giải thích lý do."`
3. Thêm post-processing: check trùng lặp giữa các câu hỏi (cosine similarity).

---

## Failure #3: TC-09 — Không phát hiện mâu thuẫn trong tài liệu (FAIL)

### Mô tả sự cố
Tài liệu cố ý chứa mâu thuẫn (Trang 3 vs Trang 7 về time complexity). AI chỉ dùng thông tin ở chunk đầu tiên mà không cross-reference.

### 5 Whys Analysis

| Why | Câu hỏi | Trả lời |
|-----|---------|---------|
| **Why 1** | Tại sao AI không phát hiện mâu thuẫn? | Vì hai thông tin mâu thuẫn nằm ở hai chunks khác nhau, và AI xử lý tuần tự, ưu tiên thông tin gặp đầu tiên. |
| **Why 2** | Tại sao hai thông tin lại ở hai chunks khác nhau? | Vì chunking strategy chia theo kích thước cố định (800 ký tự), không theo semantic units. Trang 3 và Trang 7 cách xa nhau nên rơi vào chunks riêng. |
| **Why 3** | Tại sao chunking không theo semantic units? | Vì V1 dùng character-based chunking đơn giản (chia theo số ký tự + overlap) để nhanh chóng prototype. Chưa implement semantic chunking. |
| **Why 4** | Tại sao character-based chunking không đủ? | Vì khi context window chỉ chứa một phần tài liệu, AI mất khả năng cross-reference giữa các phần xa nhau. Overlap 100 ký tự quá nhỏ so với khoảng cách giữa Trang 3 và Trang 7. |
| **Why 5** | **Tại sao hệ thống không có cơ chế cross-reference?** | **Vì kiến trúc V1 là single-pass: đưa chunks vào prompt → LLM trả lời 1 lần. Không có multi-pass processing để AI đọc toàn bộ trước, rồi phân tích sau.** |

### Root Cause
> **Kiến trúc single-pass processing** không cho phép AI "nhìn lại" toàn bộ tài liệu. Khi nội dung quan trọng nằm ở các chunks xa nhau, AI thiếu cơ chế phát hiện inconsistency.

### Giải pháp đề xuất cho V2
1. **Two-pass approach**:
   - Pass 1: Tóm tắt từng chunk riêng → tạo "meta-summary"
   - Pass 2: Đưa meta-summary + original chunks vào prompt cuối cùng
2. Tăng overlap từ 100 → 200 ký tự
3. Thêm explicit instruction trong prompt: `"Trước khi tóm tắt, kiểm tra xem có thông tin mâu thuẫn giữa các phần không. Nếu phát hiện, cảnh báo rõ ràng."`
4. Index key claims (concept + value + page) để detect trùng lặp/mâu thuẫn tự động

---

## Tổng hợp Root Causes

| # | Root Cause | Failure | Nguyên tắc vi phạm (từ bài giảng) |
|---|-----------|---------|----------------------------------|
| 1 | Thiếu strictness classification cho output | TC-03 | Zero-Trust AI (Buổi 8), Rủi ro bảo mật (Buổi 10) |
| 2 | Thiếu preprocessing / content adequacy check | TC-06 | Problem Decomposition (Buổi 3), Task Analysis (Buổi 11) |
| 3 | Single-pass architecture không hỗ trợ cross-reference | TC-09 | RAG & chunking strategy (Buổi 4), Verification (Buổi 8) |

## Bài học rút ra

1. **Safety trước Helpfulness**: Khi thiết kế AI system, ưu tiên ngăn chặn output sai trước khi thêm tính năng "bonus".
2. **Validate trước khi delegate**: Luôn kiểm tra tính khả thi của yêu cầu trước khi chuyển cho LLM.
3. **Multi-pass > Single-pass** cho tài liệu dài: Cần ít nhất 2 lần đọc để phát hiện inconsistency.
