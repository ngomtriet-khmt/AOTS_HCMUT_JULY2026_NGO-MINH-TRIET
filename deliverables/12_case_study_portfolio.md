# Deliverable 12: Bài Viết Case Study Chuẩn Portfolio — GitHub / LinkedIn

---

# AI Study Assistant: Building a Zero-Trust AI Learning Tool

## Case Study — Ngô Minh Triết | HCMUT × AOTS AI Engineering Program

---

## TL;DR
Built an AI-powered study assistant that helps Vietnamese university students learn more effectively from lecture materials. Applied Zero-Trust AI principles to reduce hallucination from 18% to 5%, achieving 90% pass rate across 10 stress-test scenarios.

---

## Situation (Tình huống)

Sinh viên đại học Việt Nam thường phải đối mặt với khối lượng tài liệu lớn nhưng thiếu công cụ hỗ trợ cá nhân hóa. Nghiên cứu cho thấy phần lớn sinh viên học theo phương pháp passive re-reading (đọc lại thụ động) — phương pháp kém hiệu quả nhất — thay vì active recall và spaced repetition.

Trong khóa học AI Engineering tại HCMUT (chương trình AOTS), tôi quyết định xây dựng một **AI Study Assistant** giải quyết vấn đề này, áp dụng toàn bộ kiến thức từ 12 buổi học về prompt engineering, Zero-Trust AI, và AI system design.

## Task (Nhiệm vụ)

Xây dựng một ứng dụng web AI có khả năng:
1. **Tóm tắt thông minh** tài liệu bài giảng theo 3 lớp chi tiết
2. **Tạo câu hỏi ôn tập** theo Bloom's Taxonomy (Recall / Application / Analysis)
3. **Giải thích từng bước** khái niệm khó bằng Chain of Thought
4. **Đánh giá câu trả lời** của sinh viên với phản hồi constructive

Yêu cầu kỹ thuật: strict grounding (không hallucinate), safety-first, model-agnostic architecture.

## Action (Hành động)

### Phase 1: System Design (AI System Design Checklist — 11 thành phần)

Áp dụng AI System Design Checklist từ Buổi 12 để thiết kế toàn diện:

| Thành phần | Quyết định thiết kế |
|-----------|-------------------|
| Problem Definition | Hỗ trợ học tập từ tài liệu, KHÔNG thay thế việc học |
| Data Strategy | Session-based, không persist PII, chunking theo semantic boundaries |
| Model Selection | Claude Sonnet 4.6 (primary) + GPT-4o-mini (backup) |
| Prompt Architecture | PTCF cho tóm tắt, RISEN cho câu hỏi, CoT cho giải thích |
| Architecture Level | AI Workflow (Level 2: AI Does, Human Checks) |
| Guardrails | 6-layer defense: input validation → prompt hardening → output filtering → action constraints → monitoring → human oversight |
| Human-in-the-Loop | Checkpoints tại mỗi output — user verify trước khi tin |

### Phase 2: Prototype V1 & Evaluation

Xây dựng V1 với Streamlit + Claude API. Tạo **10 stress-test scenarios** bao gồm:
- Empty/oversized files
- Out-of-scope queries
- Prompt injection attempts
- Contradictory document content
- API failure handling

**Kết quả V1: 70% pass rate** — 3 failures phát hiện:

| Failure | Root Cause (5-Whys) |
|---------|---------------------|
| AI "bonus" thông tin ngoài tài liệu | System prompt chưa enforce strict grounding |
| Tạo câu hỏi trùng lặp từ tài liệu ngắn | Thiếu content adequacy preprocessing |
| Không phát hiện mâu thuẫn trong tài liệu | Single-pass architecture, chunking thiếu cross-reference |

### Phase 3: V2 Improvements (Data-Driven)

Dựa trên 5-Whys analysis, thực hiện 4 cải tiến:

1. **Strict Scope Enforcement**: Viết lại system prompt với explicit "DỪNG LẠI" instructions + output validation layer kiểm tra citations
2. **Content Adequacy Check**: Thêm preprocessing layer tính word-to-question ratio trước khi gọi LLM
3. **Two-Pass Processing**: Meta-summary + conflict detection instructions trong prompt
4. **Output Validation**: Tự động phát hiện claims thiếu citation và dấu hiệu thông tin ngoài tài liệu

### Phase 4: Model Swap Test

Thay Claude bằng GPT-4o-mini với **cùng prompt architecture**:

| Metric | Claude | GPT-4o-mini | Gap |
|--------|--------|-------------|-----|
| Scope compliance | 98% | 72% | -26% |
| Citation rate | 95% | 62% | -33% |
| Hallucination | 2% | 12% | +10% |
| Latency | 9.8s | 7.3s | -2.5s |

**Insight**: Prompt portability trung bình — architecture không lock-in, nhưng instruction-following quality phụ thuộc model. Claude tuân thủ strict instructions tốt hơn đáng kể.

## Result (Kết quả)

### Quantitative Improvements V1 → V2

| Metric | V1 | V2 | Improvement |
|--------|----|----|-------------|
| **Stress-test pass rate** | 70% | 90% | +20% |
| **Hallucination rate** | 18% | 5% | -13% |
| **Citation rate** | 60% | 95% | +35% |
| **Scope compliance** | 70% | 95% | +25% |
| **Question validity** | 72% | 88% | +16% |

### Architecture Diagram

```
User → Streamlit UI → Document Processor (semantic chunking + adequacy check)
                    → Prompt Engine (PTCF/RISEN/CoT templates + strict grounding)
                    → LLM Gateway (Claude/GPT swap + retry + output validation)
                    → Response + Warnings + Citations
```

### Key Trade-offs Made
- **Safety > Helpfulness**: AI từ chối giải thích ngoài tài liệu thay vì "bonus" — đúng với Zero-Trust
- **Quality > Speed**: Two-pass processing tăng latency 15% nhưng giảm hallucination 72%
- **Fewer > More**: Tạo ít câu hỏi hơn yêu cầu nếu nội dung không đủ — tránh câu hỏi kém chất lượng

---

## Lessons Learned (Bài học)

### 1. "Safety First" không phải slogan
System prompt V1 nói "nói rõ nếu không có" nhưng không cấm bonus → AI vẫn hallucinate 18%. V2 nói "DỪNG LẠI. KHÔNG giải thích thêm." → giảm xuống 5%. **Instruction cần explicit, không ambiguous.**

### 2. Validate trước khi delegate
Content adequacy check (200 dòng code) ngăn chặn hàng chục câu hỏi kém chất lượng. **Preprocessing đơn giản có thể tiết kiệm nhiều API calls lãng phí.**

### 3. Model swap test là bắt buộc
Prompt hoạt động tốt trên Claude nhưng kém trên GPT-4o-mini (citation rate giảm 33%). **Architecture portable ≠ Quality portable.**

### 4. 5-Whys thay đổi cách debug
Thay vì fix triệu chứng (thêm filter), 5-Whys giúp tìm root cause (kiến trúc single-pass). **Fix root cause giải quyết nhiều vấn đề cùng lúc.**

---

## Tech Stack
- **Frontend**: Streamlit (Python)
- **LLM**: Claude Sonnet 4.6 (Anthropic API) + GPT-4o-mini (OpenAI API)
- **Document Processing**: PyPDF2
- **Prompt Frameworks**: PTCF, RISEN, Chain of Thought, Socratic Tutoring
- **Evaluation**: 10-scenario stress-test suite, 7-field LLM evaluation cases

## Links
- **GitHub Repository**: [link — điền sau khi push]
- **Live Demo**: [link Streamlit Cloud — điền sau khi deploy]
- **Video Demo**: [link YouTube — điền sau khi upload]

---

*Built during the AOTS AI Engineering Program at Ho Chi Minh City University of Technology (HCMUT), 2026.*

*Applying concepts from: Prompt Engineering, Chain of Thought, Zero-Trust AI, RAG, AI System Design, Security Risk Assessment, and Human-in-the-Loop principles.*
