# Deliverable 1: Bản Mô Tả Bài Toán & Vấn Đề Thực Tế Cần Giải Quyết

## Tên dự án
**AI Study Assistant - Trợ lý Học tập Thông minh cho Sinh viên Đại học**

---

## 1. Bối cảnh thực tế

Sinh viên đại học tại Việt Nam, đặc biệt tại các trường kỹ thuật như HCMUT, thường phải đối mặt với:

- **Khối lượng tài liệu lớn**: Mỗi môn học có hàng trăm trang slide, giáo trình, và tài liệu tham khảo. Sinh viên mất nhiều thời gian đọc nhưng không nắm được trọng tâm.
- **Thiếu phương pháp học hiệu quả**: Phần lớn sinh viên học theo kiểu đọc lại (passive re-reading) thay vì active recall và spaced repetition - hai phương pháp được chứng minh hiệu quả nhất.
- **Không có người hướng dẫn 24/7**: Khi gặp khó khăn ngoài giờ học, sinh viên không có ai giải đáp thắc mắc kịp thời.
- **Ôn thi thiếu hệ thống**: Sinh viên thường ôn thi kiểu "nhồi nhét" vào phút chót thay vì học dàn trải và kiểm tra kiến thức định kỳ.

## 2. Vấn đề cốt lõi

> **Sinh viên thiếu một công cụ hỗ trợ học tập cá nhân hóa**, có khả năng: tóm tắt tài liệu theo trọng tâm, tạo câu hỏi ôn tập ở nhiều mức độ, giải thích khái niệm từng bước, và theo dõi tiến độ học tập - tất cả đều dựa trên nội dung bài giảng thực tế của họ.

## 3. Đối tượng sử dụng (Users)

| Đối tượng | Nhu cầu chính | Pain Point |
|-----------|--------------|------------|
| Sinh viên năm 1-2 | Hiểu khái niệm cơ bản, tạo flashcard | Chưa có phương pháp học hiệu quả |
| Sinh viên năm 3-4 | Ôn thi chuyên sâu, phân tích case study | Khối lượng kiến thức lớn, thiếu thời gian |
| Sinh viên làm đồ án | Nghiên cứu tài liệu, tổng hợp thông tin | Cần đọc nhiều paper/tài liệu kỹ thuật |

## 4. Giải pháp đề xuất

Xây dựng một **AI Study Assistant** với các tính năng chính:

### 4.1. Tóm tắt tài liệu thông minh (Smart Summarization)
- Upload bài giảng (PDF/text) → AI tóm tắt theo 3 lớp (key points, structured analysis, critical insights)
- Áp dụng kỹ thuật **Layered Summarization** từ Buổi 4

### 4.2. Tạo câu hỏi ôn tập (Question Generation)
- Tự động tạo câu hỏi ở 3 mức: Nhớ (Recall), Áp dụng (Application), Phân tích (Analysis)
- Hỗ trợ xuất flashcard định dạng Anki (TSV)
- Áp dụng kỹ thuật từ Buổi 7

### 4.3. Giải thích từng bước (Step-by-Step Explanation)
- Giải thích khái niệm khó bằng phương pháp Chain of Thought
- Hỗ trợ Socratic Tutoring - hỏi ngược để kiểm tra hiểu biết
- Áp dụng kỹ thuật từ Buổi 3

### 4.4. Đánh giá & phản hồi (Evaluation & Feedback)
- Sinh viên trả lời câu hỏi → AI đánh giá, chỉ ra lỗi, gợi ý cải thiện
- Theo dõi error log cá nhân
- Áp dụng kỹ thuật từ Buổi 9

## 5. Phạm vi dự án (Scope)

### Trong phạm vi (In Scope)
- Web application đơn giản (Streamlit)
- Tích hợp API của Claude/GPT
- Xử lý tài liệu PDF/text (dưới 50 trang)
- 4 tính năng chính như mô tả
- Hỗ trợ tiếng Việt

### Ngoài phạm vi (Out of Scope)
- Mobile app
- Tích hợp LMS (Moodle, Google Classroom)
- Real-time collaboration
- Xử lý hình ảnh/video trong tài liệu
- Fine-tuning model riêng

## 6. Tiêu chí thành công

| Tiêu chí | Mục tiêu | Cách đo lường |
|----------|---------|---------------|
| Chất lượng tóm tắt | ≥ 80% nội dung trọng tâm được bao phủ | Human evaluation trên 10 tài liệu |
| Chất lượng câu hỏi | ≥ 70% câu hỏi hợp lệ và đúng mức độ | Human evaluation trên 50 câu hỏi |
| Độ chính xác giải thích | ≥ 85% giải thích chính xác về mặt nội dung | So sánh với tài liệu gốc |
| Thời gian phản hồi | < 30 giây cho mỗi yêu cầu | Đo thời gian response |
| Trải nghiệm người dùng | ≥ 4/5 điểm hài lòng | Khảo sát 5 sinh viên thử nghiệm |

## 7. Công nghệ sử dụng

- **Frontend**: Streamlit (Python)
- **LLM API**: Anthropic Claude API (primary), OpenAI GPT API (backup/swap test)
- **Document Processing**: PyPDF2, python-docx
- **Data Storage**: JSON files (prototype level)
- **Deployment**: Local / Streamlit Cloud

## 8. Rủi ro chính

| Rủi ro | Mức độ | Biện pháp giảm thiểu |
|--------|--------|---------------------|
| AI hallucination trong nội dung học thuật | Cao | Zero-Trust verification, citation từ tài liệu gốc |
| Rò rỉ dữ liệu cá nhân sinh viên | Trung bình | Data minimization, không lưu PII |
| Phụ thuộc vào một LLM provider | Trung bình | Model Swap architecture |
| Chi phí API cao khi scale | Thấp | Caching, prompt optimization |
