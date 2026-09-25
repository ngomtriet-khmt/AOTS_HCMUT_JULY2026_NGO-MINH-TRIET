# Deliverable 11: Video Demo 3 Phút — Kịch Bản & Hướng Dẫn Quay

## Thông tin
- **Thời lượng:** 3 phút
- **Công cụ quay:** OBS Studio / ShareX / Built-in Screen Recording (Win+G)
- **Resolution:** 1920x1080 (Full HD)

---

## Kịch Bản Video (Script)

### [0:00 - 0:20] Opening — Giới thiệu
**Hiển thị:** Title slide hoặc Streamlit app homepage
**Lời dẫn:**
> "Xin chào, tôi là Ngô Minh Triết, sinh viên HCMUT khóa AOTS. Hôm nay tôi sẽ demo AI Study Assistant — một ứng dụng AI giúp sinh viên học tập hiệu quả hơn từ tài liệu bài giảng. Ứng dụng được xây dựng bằng Streamlit, tích hợp Claude API, áp dụng các nguyên tắc từ khóa học như Zero-Trust AI, prompt engineering, và human-in-the-loop."

### [0:20 - 0:50] Demo 1 — Upload & Tóm Tắt
**Thao tác:**
1. Mở app Streamlit
2. Upload file PDF bài giảng (slides CTDL)
3. Nhập tên môn học
4. Chọn "Lớp 1: Key Points" → Click "Tạo Tóm Tắt"
5. Highlight citations [Trang X] trong kết quả

**Lời dẫn:**
> "Bước đầu tiên: upload tài liệu. Tôi upload slides 30 trang về Cấu trúc dữ liệu. Hệ thống tự động chia thành các chunks. Khi tôi yêu cầu tóm tắt Lớp 1, AI tạo 5-7 key points, mỗi điểm đều có trích dẫn trang cụ thể — đây là cách đảm bảo grounding, tránh hallucination."

### [0:50 - 1:20] Demo 2 — Tạo Câu Hỏi Ôn Tập
**Thao tác:**
1. Chuyển tab "Câu Hỏi Ôn Tập"
2. Chọn 10 câu, mức "Cân bằng"
3. Click "Tạo Câu Hỏi"
4. Scroll qua kết quả, highlight [Recall], [Application], [Analysis]
5. Click "Tạo file Anki TSV" → Download

**Lời dẫn:**
> "Tiếp theo, tạo 10 câu hỏi ôn tập phân bố theo Bloom's Taxonomy. AI tạo câu hỏi ở 3 mức: Recall, Application, và Analysis. Mỗi câu đều có đáp án tham chiếu từ tài liệu. Tôi có thể xuất sang Anki để ôn tập theo spaced repetition."

### [1:20 - 1:50] Demo 3 — Giải Thích + Scope Rejection
**Thao tác:**
1. Chuyển tab "Giải Thích"
2. Nhập "Binary Search Tree" → Chain of Thought → Click
3. Nhanh chóng cho kết quả → highlight 5 bước
4. Thử nhập "Quantum Computing" (ngoài tài liệu)
5. AI từ chối: "Thông tin này không có trong tài liệu"

**Lời dẫn:**
> "Khi tôi hỏi về Binary Search Tree — có trong tài liệu — AI giải thích từng bước rõ ràng với citations. Nhưng khi tôi thử hỏi Quantum Computing — không có trong tài liệu — AI từ chối và dừng lại. Đây là strict scope enforcement, nguyên tắc Zero-Trust: không bịa thông tin ngoài nguồn."

### [1:50 - 2:20] Demo 4 — Đánh Giá & Safety
**Thao tác:**
1. Chuyển tab "Đánh Giá"
2. Nhập câu hỏi về Stack, trả lời sai (FIFO)
3. AI phát hiện lỗi, cho điểm 3/10, giải thích chi tiết
4. Scroll xuống footer → Highlight disclaimer

**Lời dẫn:**
> "Tính năng đánh giá: tôi cố ý trả lời sai — nói Stack là FIFO. AI phát hiện lỗi ngay, giải thích Stack là LIFO, và cho điểm phù hợp. Lưu ý disclaimer ở cuối: kết quả cần kiểm chứng với tài liệu gốc — luôn human-in-the-loop."

### [2:20 - 2:50] Kiến trúc & Cải tiến V1→V2
**Hiển thị:** Slide hoặc diagram kiến trúc hệ thống
**Lời dẫn:**
> "Về kiến trúc: ứng dụng có 4 module — Document Processor, Prompt Engine, LLM Gateway với model swap support, và Output Validator. Từ V1 sang V2, tôi đã cải thiện: strict scope enforcement giảm hallucination từ 18% xuống 5%, thêm content adequacy check, và two-pass processing cho conflict detection. Pass rate tăng từ 70% lên 90% trên 10 stress-test scenarios."

### [2:50 - 3:00] Closing
**Lời dẫn:**
> "AI Study Assistant — xây dựng với tinh thần Zero-Trust, human-in-the-loop, và continuous improvement. Cảm ơn các thầy cô và khóa AOTS."

---

## Cách quay video

### Bước 1: Chuẩn bị
- Cài OBS Studio hoặc dùng Win+G (Xbox Game Bar)
- Mở app Streamlit: `streamlit run src/v2/app.py`
- Chuẩn bị file PDF test sẵn
- Nhập API Key trước

### Bước 2: Quay
- Record screen + audio (micro)
- Làm theo script trên
- Nếu quay riêng → edit ghép bằng CapCut/DaVinci Resolve

### Bước 3: Export
- Format: MP4 H.264
- Resolution: 1920x1080
- Upload lên YouTube (Unlisted) hoặc Google Drive

### Link demo (điền sau khi quay):
- **YouTube:** [điền link]
- **Google Drive:** [điền link]

---

## Alternative: Link Trải Nghiệm Trực Tiếp

Nếu deploy lên Streamlit Cloud:
```bash
# Push code lên GitHub
# Connect GitHub repo tại share.streamlit.io
# Config secrets (API key) trong Streamlit Cloud settings
```

**Link app (điền sau khi deploy):** [điền link Streamlit Cloud]
