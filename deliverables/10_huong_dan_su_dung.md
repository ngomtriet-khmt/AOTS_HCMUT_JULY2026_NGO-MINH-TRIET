# Deliverable 10: Tài Liệu Hướng Dẫn Sử Dụng, Giới Hạn và Khuyến Cáo An Toàn

## AI Study Assistant V2 — User Guide

---

## 1. Hướng dẫn cài đặt

### Yêu cầu hệ thống
- Python 3.10 trở lên
- Kết nối Internet (để gọi API)
- API Key: Anthropic Claude hoặc OpenAI GPT

### Cài đặt
```bash
# Clone hoặc download source code
cd src/v2

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
streamlit run app.py
```

### Cấu hình API Key
1. Mở ứng dụng trong trình duyệt (mặc định: `http://localhost:8501`)
2. Ở sidebar bên trái, chọn **LLM Provider** (Claude hoặc GPT)
3. Nhập **API Key** vào ô mật khẩu
4. API Key chỉ lưu trong session, không persist trên server

---

## 2. Hướng dẫn sử dụng

### 2.1. Upload tài liệu
1. Click "Browse files" ở sidebar
2. Chọn file PDF (≤ 50 trang) hoặc TXT (≤ 100KB)
3. Nhập tên môn học để AI hiểu ngữ cảnh
4. Chờ xử lý → hiển thị số chunks đã tạo

### 2.2. Tóm tắt tài liệu
1. Chọn tab **📝 Tóm Tắt**
2. Chọn mức độ:
   - **Lớp 1**: 5-7 bullet points chính
   - **Lớp 2**: Phân tích có heading, chi tiết hơn
   - **Lớp 3**: Nhận xét sâu, liên hệ các khái niệm
3. Click "Tạo Tóm Tắt"
4. **Kiểm tra**: Đối chiếu [Trang X] với tài liệu gốc

### 2.3. Tạo câu hỏi ôn tập
1. Chọn tab **❓ Câu Hỏi Ôn Tập**
2. Điều chỉnh số lượng (5-20) và mức độ khó
3. Lưu ý cảnh báo content adequacy nếu tài liệu ngắn
4. Click "Tạo Câu Hỏi"
5. Xuất sang Anki: click "Tạo file Anki TSV" → Download

### 2.4. Giải thích khái niệm
1. Chọn tab **💡 Giải Thích**
2. Nhập khái niệm cần giải thích
3. Chọn chế độ:
   - **Chain of Thought**: Giải thích từng bước, rõ ràng
   - **Socratic Tutoring**: Hỏi ngược để bạn tự khám phá
4. Click "Giải Thích"

### 2.5. Đánh giá câu trả lời
1. Chọn tab **📊 Đánh Giá**
2. Nhập câu hỏi và câu trả lời của bạn
3. Click "Đánh Giá"
4. Xem điểm, phản hồi, và gợi ý cải thiện

---

## 3. Giới hạn (Limitations)

### 3.1. Giới hạn kỹ thuật
| Giới hạn | Mô tả | Ảnh hưởng |
|----------|-------|-----------|
| **File format** | Chỉ hỗ trợ PDF có text layer và TXT | File scan (hình ảnh) không đọc được |
| **Kích thước file** | Tối đa 50 trang PDF / 100KB text | Giáo trình dài cần chia nhỏ |
| **Ngôn ngữ** | Tiếng Việt và tiếng Anh | Các ngôn ngữ khác chưa test |
| **Context window** | Phụ thuộc vào model (200K tokens) | Tài liệu rất dài có thể bị truncate |
| **Conversation memory** | Không có — mỗi request độc lập | Không nhớ câu hỏi trước |
| **Real-time data** | Không truy cập Internet | Không tra cứu thông tin mới |

### 3.2. Giới hạn chất lượng
| Giới hạn | Mô tả |
|----------|-------|
| **Hallucination** | Dù đã giảm (~5%), vẫn có thể tạo thông tin không chính xác |
| **Conflict detection** | Phát hiện mâu thuẫn chưa hoàn hảo khi thông tin ở xa nhau |
| **Đánh giá chủ quan** | AI đánh giá câu trả lời dựa trên pattern matching, không phải hiểu sâu |
| **Câu hỏi mở** | Khó đánh giá câu trả lời cho câu hỏi phân tích, sáng tạo |
| **Đồ thị / Hình ảnh** | Không xử lý được nội dung hình ảnh trong tài liệu |

---

## 4. Khuyến cáo an toàn

### 4.1. Tư duy Zero-Trust (Buổi 8)
> **Quy tắc vàng: KHÔNG BAO GIỜ tin AI 100%. Luôn kiểm chứng.**

- Mọi thông tin AI đưa ra đều PHẢI được đối chiếu với tài liệu gốc
- Chú ý citations [Trang X] — nếu thiếu citation, cần nghi ngờ
- Nếu thấy cảnh báo ⚠️ → đặc biệt cẩn thận kiểm tra

### 4.2. Bảo mật dữ liệu (Buổi 10)
| Việc nên làm | Việc KHÔNG nên làm |
|-------------|-------------------|
| Upload tài liệu học thuật công khai | Upload bài thi/đề thi chưa công bố |
| Sử dụng câu hỏi ôn tập chung | Nhập thông tin cá nhân (MSSV, email, SĐT) |
| Dùng API key cá nhân | Chia sẻ API key cho người khác |
| Đăng xuất/đóng tab sau khi dùng | Để session mở trên máy công cộng |

### 4.3. Data Classification trước khi upload
| Level | Có thể upload? | Ví dụ |
|-------|----------------|-------|
| **Public** | ✅ Có | Slides đã publish, giáo trình online |
| **Internal** | ⚠️ Cẩn thận | Slides nội bộ lớp học |
| **Sensitive** | ❌ Không | Đề thi, bài giải chính thức |
| **Secret** | ❌ Tuyệt đối không | Dữ liệu cá nhân, thông tin mật |

### 4.4. Sử dụng AI có trách nhiệm
1. **AI là công cụ hỗ trợ, không thay thế việc học**: Dùng AI để hiểu sâu hơn, không phải để bỏ qua việc đọc tài liệu.
2. **Active Recall**: Thử tự trả lời trước khi xem đáp án AI.
3. **Trung thực học thuật**: Không sử dụng AI để gian lận trong thi cử. Kết quả từ AI Study Assistant là tài liệu ôn tập, không phải bài làm.
4. **Phản hồi lỗi**: Nếu phát hiện AI trả lời sai → ghi nhận để cải thiện hệ thống.

### 4.5. Mô hình 4 mức độ sử dụng AI phù hợp (Buổi 11)

| Hoạt động | Mức AI đề xuất | Lý do |
|-----------|---------------|-------|
| Tóm tắt tài liệu | Level 2 (AI làm, người kiểm tra) | Cần verify accuracy |
| Tạo flashcards | Level 3 (AI làm phần lớn) | Kiểm tra quality ở cuối |
| Giải thích khái niệm | Level 2 | Cần đối chiếu với hiểu biết |
| Ôn thi | Level 1 (AI hỗ trợ, người tự làm) | Cần active recall |
| Viết bài tiểu luận | Level 1 | AI chỉ tham khảo, tự viết |

---

## 5. Xử lý sự cố

| Sự cố | Nguyên nhân | Cách khắc phục |
|-------|------------|----------------|
| "Chưa cung cấp API Key" | Chưa nhập key ở sidebar | Nhập API Key ở sidebar bên trái |
| "File trống" | PDF scan hoặc bị mã hóa | Convert sang text hoặc dùng PDF khác |
| "Vượt quá giới hạn 50 trang" | File quá dài | Chia file thành nhiều phần nhỏ |
| Kết quả không chính xác | Hallucination | Đối chiếu với tài liệu gốc, thử lại |
| Response rất chậm (>30s) | API overloaded | Thử lại sau vài phút |
| Cảnh báo ⚠️ trong output | Output validation phát hiện rủi ro | Kiểm tra kỹ nội dung được cảnh báo |
