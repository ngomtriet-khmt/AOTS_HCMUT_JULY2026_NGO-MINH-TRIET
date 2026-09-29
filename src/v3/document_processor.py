"""
Document Processor Module - V3 (Gemini-only, hỗ trợ file lớn)

Cải tiến so với V2:
- Bỏ giới hạn cứng 50 trang / 100KB. Chỉ chặn khi file thực sự quá lớn.
- Thêm reader cho DOCX (python-docx) bên cạnh PDF và TXT.
- Ước lượng token để quyết định gửi 1-lần (single-call) hay map-reduce.
- Chèn marker trích dẫn cho mọi định dạng: [Trang X] cho PDF, [Phần X] cho DOCX/TXT.
- select_relevant_context(): chọn ngữ cảnh phù hợp khi tài liệu vượt quá context window.
- sanitize_text(): che PII (email, SĐT, MSSV, API key) trước khi gửi model (học từ TaskLens).

Tác giả: Ngô Minh Triết — AOTS HCMUT
"""

import io
import re
import math
from typing import List, Dict, Tuple

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx  # python-docx
except ImportError:
    docx = None


# --- Cấu hình xử lý file lớn ---
# Ước lượng token thô: tiếng Việt/Anh trộn ~3 ký tự/token (ước tính an toàn, thiên cao).
CHARS_PER_TOKEN = 3

# Trần an toàn để đọc file (tránh treo app với file khổng lồ). ~15 triệu ký tự ≈ 5M token.
MAX_CHARS_HARD_LIMIT = 15_000_000

# Regex nhận diện marker trích dẫn dùng chung cho toàn hệ thống.
CITATION_MARKER = r"\[(?:Trang|Phần) \d+\]"


def estimate_tokens(text: str) -> int:
    """Ước lượng số token theo heuristic (không gọi API, không tốn quota)."""
    return math.ceil(len(text) / CHARS_PER_TOKEN)


# ---------------------------------------------------------------------------
# Trích xuất text theo định dạng
# ---------------------------------------------------------------------------
def extract_text(uploaded_file) -> str:
    """
    Điểm vào chung: tự nhận diện định dạng và trả về text đã gắn marker trích dẫn.
    Hỗ trợ: PDF, DOCX, TXT.
    """
    name = (getattr(uploaded_file, "name", "") or "").lower()
    mime = getattr(uploaded_file, "type", "") or ""

    if name.endswith(".pdf") or mime == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif name.endswith(".docx") or "wordprocessingml" in mime:
        text = extract_text_from_docx(uploaded_file)
    elif name.endswith(".txt") or mime == "text/plain":
        raw = uploaded_file.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore")
        text = _add_section_markers(raw)
    else:
        raise ValueError(
            f"Định dạng không hỗ trợ: {name or mime}. "
            "Chỉ hỗ trợ PDF, DOCX, TXT."
        )

    if len(text) > MAX_CHARS_HARD_LIMIT:
        raise ValueError(
            f"File quá lớn ({len(text):,} ký tự, vượt trần {MAX_CHARS_HARD_LIMIT:,}). "
            "Vui lòng tách nhỏ tài liệu."
        )
    return text


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text từ PDF. V3: KHÔNG giới hạn số trang cứng."""
    if PdfReader is None:
        raise ImportError("PyPDF2 chưa được cài đặt. Chạy: pip install PyPDF2")

    reader = PdfReader(uploaded_file)
    text_parts = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text and page_text.strip():
            text_parts.append(f"[Trang {i + 1}]\n{page_text}")

    if not text_parts:
        raise ValueError(
            "Không đọc được text từ PDF. File có thể là bản scan/ảnh "
            "(cần PDF có text layer)."
        )
    return "\n\n".join(text_parts)


def extract_text_from_docx(uploaded_file) -> str:
    """Extract text từ DOCX (đoạn văn + bảng), gắn marker [Phần X]."""
    if docx is None:
        raise ImportError("python-docx chưa được cài đặt. Chạy: pip install python-docx")

    data = uploaded_file.read()
    document = docx.Document(io.BytesIO(data))

    parts = []
    for para in document.paragraphs:
        if para.text and para.text.strip():
            parts.append(para.text.strip())

    # Trích cả nội dung bảng để không bỏ sót dữ liệu.
    for table in document.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text and c.text.strip()]
            if cells:
                parts.append(" | ".join(cells))

    if not parts:
        raise ValueError("File DOCX trống hoặc không đọc được nội dung.")

    return _add_section_markers("\n".join(parts))


def _add_section_markers(text: str, block_chars: int = 1500) -> str:
    """
    Chèn marker [Phần X] cho tài liệu không có sẵn khái niệm trang (DOCX/TXT),
    để trích dẫn vẫn hoạt động. Cắt tại ranh giới dòng gần nhất.
    """
    text = text.strip()
    if not text:
        return ""

    lines = text.split("\n")
    blocks: List[str] = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > block_chars and current:
            blocks.append(current.strip())
            current = line
        else:
            current += ("\n" + line) if current else line
    if current.strip():
        blocks.append(current.strip())

    return "\n\n".join(f"[Phần {i + 1}]\n{b}" for i, b in enumerate(blocks))


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    """
    Chia text thành chunk nhỏ (dùng cho retrieval khi tài liệu quá lớn).
    Ưu tiên cắt theo marker [Trang X]/[Phần X] để giữ ranh giới ngữ nghĩa.
    """
    if not text.strip():
        return []

    segments = re.split(f"(?={CITATION_MARKER})", text)
    segments = [s.strip() for s in segments if s.strip()]

    chunks: List[str] = []
    current = ""
    for seg in segments:
        if len(current) + len(seg) <= chunk_size:
            current += ("\n\n" + seg) if current else seg
        else:
            if current:
                chunks.append(current.strip())
            if len(seg) > chunk_size:
                chunks.extend(_split_long_text(seg, chunk_size, overlap))
                current = ""
            else:
                current = seg
    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else _split_long_text(text, chunk_size, overlap)


def _split_long_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Fallback: chia text dài theo ranh giới câu/đoạn."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            newline_pos = text.rfind("\n\n", start, end)
            if newline_pos > start + chunk_size // 2:
                end = newline_pos + 2
            else:
                period_pos = text.rfind(". ", start, end)
                if period_pos > start + chunk_size // 2:
                    end = period_pos + 2
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, start + 1)
    return chunks


def split_into_segments(text: str, max_chars: int) -> List[str]:
    """
    Chia tài liệu thành các SEGMENT LỚN cho map-reduce (mỗi segment là 1 lần gọi map).
    Giữ nguyên marker trích dẫn trong từng segment.
    """
    if not text.strip():
        return []

    units = re.split(f"(?={CITATION_MARKER})", text)
    units = [u for u in units if u.strip()]

    segments: List[str] = []
    current = ""
    for unit in units:
        if len(current) + len(unit) <= max_chars:
            current += unit
        else:
            if current.strip():
                segments.append(current.strip())
            # Đơn vị đơn lẻ quá lớn → cắt cứng theo ký tự.
            if len(unit) > max_chars:
                for i in range(0, len(unit), max_chars):
                    segments.append(unit[i:i + max_chars].strip())
                current = ""
            else:
                current = unit
    if current.strip():
        segments.append(current.strip())
    return segments


# ---------------------------------------------------------------------------
# Chọn ngữ cảnh cho các tác vụ hỏi-đáp khi tài liệu lớn
# ---------------------------------------------------------------------------
def select_relevant_context(
    full_text: str,
    chunks: List[str],
    budget_tokens: int,
    query: str = "",
) -> Tuple[str, bool]:
    """
    Chọn ngữ cảnh vừa với ngân sách token.

    - Nếu toàn bộ tài liệu vừa budget → trả về full_text (truncated=False).
    - Nếu vượt → xếp hạng chunk:
        + có `query`: theo độ trùng từ khóa với query.
        + không `query`: lấy mẫu trải đều toàn tài liệu.
      Ghép các chunk đến khi gần chạm budget (truncated=True).
    """
    if estimate_tokens(full_text) <= budget_tokens:
        return full_text, False

    budget_chars = budget_tokens * CHARS_PER_TOKEN

    if query:
        keywords = {w for w in re.findall(r"\w+", query.lower()) if len(w) > 2}
        scored = []
        for idx, ch in enumerate(chunks):
            low = ch.lower()
            score = sum(low.count(k) for k in keywords)
            scored.append((score, idx, ch))
        scored.sort(key=lambda x: (-x[0], x[1]))
        ordered = [(idx, ch) for score, idx, ch in scored if score > 0]
        if not ordered:  # không match → rơi về lấy mẫu đều
            ordered = _even_sample(chunks)
    else:
        ordered = _even_sample(chunks)

    selected: List[Tuple[int, str]] = []
    total = 0
    for idx, ch in ordered:
        if total + len(ch) > budget_chars:
            continue
        selected.append((idx, ch))
        total += len(ch)
        if total >= budget_chars * 0.95:
            break

    # Sắp xếp lại theo thứ tự tài liệu gốc để giữ mạch nội dung.
    selected.sort(key=lambda x: x[0])
    context = "\n---\n".join(ch for _, ch in selected)
    return context, True


def _even_sample(chunks: List[str]) -> List[Tuple[int, str]]:
    """Trả về danh sách (index, chunk) theo thứ tự trải đều toàn tài liệu."""
    return list(enumerate(chunks))


# ---------------------------------------------------------------------------
# Tiện ích V2 giữ lại
# ---------------------------------------------------------------------------
def check_content_adequacy(chunks: List[str], num_questions: int) -> Dict:
    """Kiểm tra tài liệu có đủ nội dung cho số câu hỏi yêu cầu."""
    total_words = sum(len(c.split()) for c in chunks)
    recommended_count = max(3, total_words // 100)

    if recommended_count >= num_questions:
        return {"is_adequate": True, "recommended_count": num_questions, "reason": None}
    return {
        "is_adequate": False,
        "recommended_count": min(recommended_count, num_questions),
        "reason": (
            f"Tài liệu chỉ có ~{total_words} từ, chỉ đủ để tạo "
            f"{recommended_count} câu hỏi chất lượng (yêu cầu: {num_questions})."
        ),
    }


def build_meta_summary(chunks: List[str], max_chunks: int = 60) -> str:
    """Tạo meta-summary (bản đồ nội dung) hỗ trợ phát hiện mâu thuẫn."""
    meta_parts = []
    for i, chunk in enumerate(chunks[:max_chunks]):
        lines = chunk.split("\n")
        preview = " | ".join(line.strip() for line in lines[:3] if line.strip())
        meta_parts.append(f"[Chunk {i + 1}]: {preview[:200]}")
    if len(chunks) > max_chunks:
        meta_parts.append(f"... (+{len(chunks) - max_chunks} chunk khác)")
    return "\n".join(meta_parts)


# ---------------------------------------------------------------------------
# Che PII trước khi gửi model (học từ TaskLens)
# ---------------------------------------------------------------------------
_PII_PATTERNS = [
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "[EMAIL]"),
    (re.compile(r"\b(?:AIza|sk-)[A-Za-z0-9_\-]{16,}\b"), "[API_KEY]"),
    (re.compile(r"\b(?:0|\+84)\d{9,10}\b"), "[SĐT]"),
    (re.compile(r"\b\d{7,8}\b"), "[MSSV]"),  # mã số sinh viên HCMUT 7-8 chữ số
]


def sanitize_text(text: str) -> Tuple[str, int]:
    """
    Che các thông tin cá nhân nhạy cảm trước khi gửi model.
    Trả về (text_đã_che, số_lượng_thay_thế).
    """
    count = 0
    for pattern, repl in _PII_PATTERNS:
        text, n = pattern.subn(repl, text)
        count += n
    return text, count
