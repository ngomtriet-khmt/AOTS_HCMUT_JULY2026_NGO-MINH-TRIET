# AI Study Assistant

**Trợ lý Học tập Thông minh cho Sinh viên Đại học**

Ứng dụng AI giúp sinh viên tóm tắt tài liệu, tạo câu hỏi ôn tập, giải thích khái niệm từng bước, và đánh giá câu trả lời — tất cả dựa trên nội dung bài giảng thực tế.

**Tác giả:** Ngô Minh Triết
**Khóa:** AOTS AI Engineering Program — HCMUT
**Ngày:** 2026-09-22

---

## Dùng Thử Nhanh (2 phút)

### Bước 1: Lấy API Key miễn phí (Google Gemini)

1. Truy cập: https://aistudio.google.com/apikey
2. Đăng nhập bằng tài khoản Google
3. Nhấn **"Create API key"**
4. Copy key vừa tạo (bắt đầu bằng `AIza...`)

> Hoàn toàn miễn phí, không cần thẻ tín dụng.

### Bước 2: Cài đặt và chạy

**Yêu cầu:** Python 3.10 trở lên ([tải tại đây](https://www.python.org/downloads/))

Mở Terminal (hoặc Command Prompt trên Windows) và chạy lần lượt:

```bash
# 1. Tải source code (hoặc Download ZIP từ GitHub)
git clone <link-repo>.git
cd END_OF_COURSE_PROJECT

# 2. Cài đặt thư viện
cd src/v3
pip install -r requirements.txt

# 3. Khởi chạy ứng dụng
streamlit run app.py
```

Trình duyệt sẽ tự mở tại `http://localhost:8501`

### Bước 3: Sử dụng

1. **Dán API Key** vào ô "API Key" ở thanh bên trái
2. **Upload tài liệu** (file PDF hoặc TXT)
3. **Chọn tính năng** ở các tab phía trên

Xem hướng dẫn chi tiết từng bước tại [HUONG_DAN_SU_DUNG.md](./HUONG_DAN_SU_DUNG.md)

---

## Tính năng chính

| Tính năng | Mô tả |
|-----------|-------|
| **Tóm Tắt Tài Liệu** | Tóm tắt 3 mức độ: Key Points, Phân tích có cấu trúc, Nhận xét sâu |
| **Tạo Câu Hỏi Ôn Tập** | Tự động tạo câu hỏi theo Bloom's Taxonomy (Nhớ / Áp dụng / Phân tích) |
| **Giải Thích Khái Niệm** | Giải thích từng bước (Chain of Thought) hoặc hỏi ngược (Socratic) |
| **Đánh Giá Câu Trả Lời** | Chấm điểm, chỉ ra lỗi sai, gợi ý cải thiện |
| **Xuất Anki Flashcards** | Xuất câu hỏi sang file TSV để import vào Anki |

## AI Provider

Từ **V3**, dự án chạy **hoàn toàn bằng Google Gemini** — chỉ cần một Google AI API key miễn phí.

| Provider | Model | Chi phí | Context |
|----------|-------|---------|---------|
| **Google Gemini** | `gemini-3.8-flash` | Miễn phí | ~1M token |

> V1/V2 vẫn giữ hỗ trợ đa provider (Claude/OpenAI) để đối chiếu lịch sử. V3 tối giản về Gemini-only.

### V3 có gì mới

- **Gemini-only**: gọn nhẹ, chỉ cần Google AI key.
- **Hỗ trợ file lớn**: bỏ giới hạn 50 trang/100KB; thêm định dạng **DOCX**.
- **Hybrid xử lý**: tài liệu vừa context ~1M token → gửi **single-call**; quá lớn → tự động **map-reduce** (tóm tắt từng phần rồi tổng hợp).
- **Che PII** trước khi gửi model (email, SĐT, MSSV, API key) — học từ [TaskLens](https://github.com/truonghienminh-HCMUT/tasklens).
- **Trích dẫn** `[Trang X]` (PDF) / `[Phần X]` (DOCX/TXT) + cảnh báo khi output thiếu nguồn.

---

## Cấu trúc thư mục

```
END_OF_COURSE_PROJECT/
├── README.md                    # File này
├── HUONG_DAN_SU_DUNG.md         # Hướng dẫn chi tiết cho người dùng
├── Lectures/                    # 12 bài giảng PDF
├── deliverables/                # 12 tài liệu bàn giao
│   ├── 01_mo_ta_bai_toan.md
│   ├── 02_thiet_ke_he_thong.md
│   ├── 04_eval_suite.md
│   ├── 05_ket_qua_kiem_thu_v1.md
│   ├── 06_phan_tich_nguyen_nhan_5whys.md
│   ├── 07_cau_hinh_v2.md
│   ├── 08_doi_chieu_v1_v2.md
│   ├── 09_model_swap_test.md
│   ├── 10_huong_dan_su_dung.md
│   ├── 11_video_demo_script.md
│   └── 12_case_study_portfolio.md
└── src/
    ├── v1/                      # Prototype V1 (phiên bản gốc, đa provider)
    ├── v2/                      # Prototype V2 (grounding/adequacy/conflict)
    └── v3/                      # Prototype V3 (Gemini-only + file lớn) ← khuyến nghị
        ├── app.py               # Ứng dụng chính
        ├── document_processor.py # PDF/DOCX/TXT, chunk, map-reduce split, che PII
        ├── prompt_engine.py      # Prompt single-call + map/reduce
        ├── llm_gateway.py        # Gemini client + orchestration hybrid
        └── requirements.txt
```

## 12 Deliverables

| # | Deliverable | File |
|---|------------|------|
| 1 | Bản mô tả bài toán | `deliverables/01_mo_ta_bai_toan.md` |
| 2 | Thiết kế hệ thống 11 thành phần | `deliverables/02_thiet_ke_he_thong.md` |
| 3 | Mã nguồn Prototype V1 | `src/v1/` |
| 4 | Eval Suite (10 kịch bản) | `deliverables/04_eval_suite.md` |
| 5 | Kết quả kiểm thử V1 | `deliverables/05_ket_qua_kiem_thu_v1.md` |
| 6 | Phân tích 5-Whys | `deliverables/06_phan_tich_nguyen_nhan_5whys.md` |
| 7 | Mã nguồn Prototype V2 | `src/v2/` + `deliverables/07_cau_hinh_v2.md` |
| 8 | Đối chiếu V1 vs V2 | `deliverables/08_doi_chieu_v1_v2.md` |
| 9 | Model Swap Test | `deliverables/09_model_swap_test.md` |
| 10 | Hướng dẫn sử dụng & an toàn | `deliverables/10_huong_dan_su_dung.md` |
| 11 | Video Demo script | `deliverables/11_video_demo_script.md` |
| 12 | Case Study Portfolio | `deliverables/12_case_study_portfolio.md` |

---

## Giới hạn & Lưu ý an toàn

- Chỉ hỗ trợ file có text layer (không đọc được PDF scan/ảnh)
- V3: hỗ trợ file lớn (không giới hạn số trang, trần an toàn ~15M ký tự); file cực lớn xử lý bằng map-reduce nên tốn nhiều lần gọi API hơn
- AI có thể tạo thông tin không chính xác (~5% hallucination rate)
- **Luôn đối chiếu kết quả AI với tài liệu gốc trước khi tin**
- Không upload thông tin cá nhân hoặc đề thi chưa công bố

---

*Dự án cuối khóa AOTS AI Engineering Program tại Đại học Bách Khoa TP.HCM (HCMUT), 2026.*
