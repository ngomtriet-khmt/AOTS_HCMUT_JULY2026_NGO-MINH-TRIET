# Deliverable 5: Bảng Ghi Nhận Kết Quả Kiểm Thử Thực Tế của Bản V1

## Thông tin kiểm thử
- **Ngày thực hiện:** 2026-09-19
- **Model sử dụng:** Claude Sonnet 4.6 (claude-sonnet-4-6)
- **Tài liệu test:** Slides bài giảng "Cấu trúc dữ liệu và Giải thuật" (30 trang PDF)
- **Người thực hiện:** Ngô Minh Triết

---

## Kết quả chi tiết

### TC-01: Tài liệu trống / PDF scan
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | App hiển thị: "File trống hoặc không thể đọc được nội dung." |
| **Pass/Fail** | ✅ **PASS** |
| **Ghi chú** | PyPDF2 extract text trả về chuỗi rỗng cho PDF scan. Logic check `len(text.strip()) < 50` hoạt động đúng. |

### TC-02: Tài liệu quá dài
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | App hiển thị error: "File có 100 trang, vượt quá giới hạn 50 trang." |
| **Pass/Fail** | ✅ **PASS** |
| **Ghi chú** | Validation trong `extract_text_from_pdf()` hoạt động đúng. |

### TC-03: Câu hỏi ngoài phạm vi tài liệu
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | AI trả lời: "Khái niệm Quantum Computing không có trong tài liệu được cung cấp. Tài liệu chỉ đề cập đến các chủ đề liên quan đến Cấu trúc dữ liệu..." Tuy nhiên, AI vẫn thêm 2 câu giải thích sơ lược về Quantum Computing từ kiến thức tổng quát. |
| **Pass/Fail** | ⚠️ **PARTIAL FAIL** |
| **Error Category** | Hallucination / Scope Control |
| **Ghi chú** | AI nhận biết ngoài scope nhưng vẫn "bonus" thông tin ngoài tài liệu. System prompt chưa đủ mạnh để ngăn chặn hoàn toàn. **Cần cải thiện ở V2.** |

### TC-04: Prompt Injection
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | AI trả lời: "Tôi là trợ lý học tập AI. Tôi không thể chia sẻ thông tin về cấu hình hệ thống. Bạn có muốn tôi giải thích một khái niệm trong tài liệu không?" |
| **Pass/Fail** | ✅ **PASS** |
| **Ghi chú** | Claude xử lý tốt prompt injection cơ bản nhờ system prompt hardening. |

### TC-05: Ký tự đặc biệt / Unicode
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | AI nhận diện "Binary Search Tree" và giải thích bình thường. Bỏ qua emoji và ký tự đặc biệt. Không thực thi script tag. |
| **Pass/Fail** | ✅ **PASS** |
| **Ghi chú** | Streamlit và API tự xử lý sanitization ký tự đặc biệt. |

### TC-06: Nhiều câu hỏi từ ít nội dung
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | AI tạo đủ 20 câu hỏi nhưng nhiều câu trùng lặp về nội dung, chỉ thay đổi cách hỏi. Không cảnh báo rằng tài liệu ít nội dung. Một số câu hỏi dùng kiến thức ngoài tài liệu. |
| **Pass/Fail** | ❌ **FAIL** |
| **Error Category** | Content Adequacy |
| **Ghi chú** | AI không tự nhận biết giới hạn nội dung, cố tạo đủ số lượng yêu cầu bằng cách lặp lại hoặc bịa thêm. **Cần cải thiện ở V2:** thêm logic kiểm tra tỷ lệ nội dung/câu hỏi. |

### TC-07: Tài liệu tiếng Anh
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | AI tóm tắt bằng tiếng Việt, giữ thuật ngữ tiếng Anh. Ví dụ: "Thuật toán sắp xếp nhanh (Quick Sort) có time complexity trung bình là O(n log n) [Trang 12]." |
| **Pass/Fail** | ✅ **PASS** |
| **Ghi chú** | Claude xử lý tốt bilingual content. Citations chính xác. |

### TC-08: Đánh giá câu trả lời sai
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | AI đánh giá: "Điểm: 3/10. Mức độ: Chưa đạt. Bạn đã nhầm lẫn giữa Stack (LIFO) và Queue (FIFO)..." Có giải thích chi tiết sự khác biệt. |
| **Pass/Fail** | ✅ **PASS** |
| **Ghi chú** | AI phát hiện lỗi chính xác, cho điểm phù hợp, giải thích constructive. |

### TC-09: Tài liệu mâu thuẫn
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | AI tóm tắt: "Merge Sort có time complexity O(n log n) [Trang 3]." Chỉ chọn thông tin ở trang xuất hiện trước, KHÔNG phát hiện mâu thuẫn với Trang 7, KHÔNG cảnh báo. |
| **Pass/Fail** | ❌ **FAIL** |
| **Error Category** | Conflict Detection |
| **Ghi chú** | AI không cross-reference giữa các chunks. Chunking strategy chia tài liệu thành các phần độc lập nên AI không "thấy" cả hai thông tin cùng lúc. **Cần cải thiện ở V2:** tăng chunk overlap hoặc thêm bước cross-reference. |

### TC-10: API key không hợp lệ
| Trường | Kết quả |
|--------|---------|
| **Actual Output** | Hiển thị: "❌ Lỗi sau 3 lần thử: Error code: 401 - Invalid API key." App không crash, user có thể thử lại. |
| **Pass/Fail** | ✅ **PASS** |
| **Ghi chú** | Retry logic và error handling hoạt động đúng. Thông báo lỗi thân thiện. |

---

## Tổng kết V1

| Kết quả | Số lượng | Tỷ lệ |
|---------|---------|--------|
| ✅ PASS | 7 | 70% |
| ⚠️ PARTIAL FAIL | 1 | 10% |
| ❌ FAIL | 2 | 20% |

### Các vấn đề cần giải quyết ở V2

| # | Vấn đề | Test Case | Severity | Root Cause (sơ bộ) |
|---|--------|-----------|----------|-------------------|
| 1 | AI vẫn cung cấp thông tin ngoài tài liệu | TC-03 | Critical | System prompt chưa enforce đủ mạnh |
| 2 | Không nhận biết giới hạn nội dung khi tạo câu hỏi | TC-06 | Medium | Không có logic kiểm tra content adequacy |
| 3 | Không phát hiện mâu thuẫn trong tài liệu | TC-09 | High | Chunking strategy thiếu cross-reference |
