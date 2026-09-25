# Deliverable 7: Cấu Hình / Mã Nguồn Phiên Bản Nâng Cấp Prototype V2

## Tổng quan thay đổi V1 → V2

### Mục tiêu nâng cấp
Giải quyết 3 failure cases được phát hiện trong kiểm thử V1:
- **TC-03** (Partial Fail): AI cung cấp thông tin ngoài tài liệu
- **TC-06** (Fail): Không nhận biết giới hạn nội dung
- **TC-09** (Fail): Không phát hiện mâu thuẫn trong tài liệu

---

## Chi tiết các thay đổi

### 1. `prompt_engine.py` — Strict Scope Enforcement (Fix TC-03)

**Vấn đề V1:** System prompt nói "nói rõ nếu không có" nhưng không cấm hoàn toàn bonus thông tin.

**Thay đổi V2:**
```python
# V1 (yếu):
# "Nếu thông tin không có trong tài liệu, nói rõ"

# V2 (mạnh):
"""
2. Nếu câu hỏi về chủ đề KHÔNG CÓ trong tài liệu:
   - Trả lời CHÍNH XÁC: "Thông tin này không có trong tài liệu được cung cấp."
   - DỪNG LẠI. KHÔNG giải thích thêm, KHÔNG bổ sung kiến thức tổng quát.
3. Mọi claim PHẢI có trích dẫn [Trang X]. Không có citation → KHÔNG đưa vào.
"""
```

**Thêm vào `build_explain_prompt()`:**
```python
# V2: Kiểm tra scope TRƯỚC KHI giải thích
"""QUAN TRỌNG: Trước tiên, kiểm tra xem "{concept}" có trong <document> không.
- Nếu KHÔNG → "Thông tin này không có trong tài liệu được cung cấp." và DỪNG.
- Nếu CÓ → tiếp tục giải thích CHỈ dựa trên nội dung tài liệu."""
```

### 2. `document_processor.py` — Content Adequacy Check (Fix TC-06)

**Vấn đề V1:** Không có preprocessing layer, truyền yêu cầu thẳng vào LLM.

**Thay đổi V2:**
```python
# NEW: Hàm check_content_adequacy()
def check_content_adequacy(chunks, num_questions):
    total_words = sum(len(c.split()) for c in chunks)
    recommended_count = max(3, total_words // 100)  # ~100 words per question
    return {
        "is_adequate": recommended_count >= num_questions,
        "recommended_count": min(recommended_count, num_questions),
        "reason": f"Tài liệu chỉ có ~{total_words} từ..."
    }
```

**Thay đổi trong `build_question_prompt()`:**
```python
# V2: Prompt linh hoạt thay vì cứng nhắc
"""Tạo TỐI ĐA {actual_count} câu hỏi CHẤT LƯỢNG thay vì cố đạt {num_questions}.
KHÔNG tạo câu trùng lặp. KHÔNG sử dụng kiến thức ngoài tài liệu.
Nếu tạo ít hơn số yêu cầu, giải thích lý do ở cuối."""
```

### 3. `document_processor.py` — Semantic Chunking & Two-pass (Fix TC-09)

**Vấn đề V1:** Character-based chunking + single-pass → mất cross-reference.

**Thay đổi V2:**

a) **Semantic chunking** — chia theo `[Trang X]` markers thay vì ký tự cố định:
```python
# V2: Chia theo page markers
page_pattern = r"\[Trang \d+\]"
pages = re.split(f"(?={page_pattern})", text)
```

b) **Tăng overlap** từ 100 → 200 ký tự

c) **Meta-summary** cho two-pass processing:
```python
# NEW: build_meta_summary()
def build_meta_summary(chunks):
    """Tạo tổng quan ngắn gọn từ mỗi chunk để cross-reference."""
    meta_parts = []
    for i, chunk in enumerate(chunks):
        preview = " | ".join(lines[:3])
        meta_parts.append(f"[Chunk {i+1}]: {preview[:200]}")
    return "\n".join(meta_parts)
```

d) **Two-pass prompt** trong `build_summary_prompt()`:
```python
# V2: Đưa meta_summary vào prompt
"""BƯỚC ĐẦU TIÊN: Đọc meta_summary và document,
kiểm tra có thông tin mâu thuẫn giữa các trang không.
Nếu phát hiện → thêm section "⚠️ CẢNH BÁO MÂU THUẪN" ở đầu."""
```

### 4. `llm_gateway.py` — Output Validation (New)

**Thay đổi V2:**
```python
# NEW: validate_output()
def validate_output(response):
    warnings = []
    # Check 1: Có citations không?
    citations = re.findall(r"\[Trang \d+\]", response)
    if paragraphs and not citations:
        warnings.append("Kết quả không chứa trích dẫn nguồn.")
    # Check 2: Dấu hiệu thông tin ngoài tài liệu?
    for indicator in ["theo kiến thức chung", "thông thường", ...]:
        if indicator in response.lower():
            warnings.append(f'Phát hiện "{indicator}" — cần kiểm chứng.')
    return {"warnings": warnings}
```

### 5. `app.py` — UI cải tiến

- Hiển thị cảnh báo content adequacy trước khi tạo câu hỏi
- Hiển thị meta-summary trong sidebar (debug mode)
- Thêm thông tin version vào eval log
- Cải thiện error messages

---

## Cấu trúc thư mục V2

```
src/v2/
├── app.py                  # Main Streamlit app (cải tiến UI)
├── document_processor.py   # PDF extract, semantic chunking, adequacy check
├── prompt_engine.py        # Prompt templates (strict grounding, two-pass)
├── llm_gateway.py          # LLM API calls (output validation)
└── requirements.txt        # Dependencies
```

## Cách chạy

```bash
cd src/v2
pip install -r requirements.txt
streamlit run app.py
```
