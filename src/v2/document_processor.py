"""
Document Processor Module - V2
Cải tiến: semantic chunking, content adequacy check, conflict detection support
"""

import io
import re
from typing import List, Dict, Tuple

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text từ file PDF đã upload qua Streamlit."""
    if PdfReader is None:
        raise ImportError("PyPDF2 chưa được cài đặt. Chạy: pip install PyPDF2")

    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)

    if total_pages > 50:
        raise ValueError(f"File có {total_pages} trang, vượt quá giới hạn 50 trang.")

    text_parts = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text_parts.append(f"[Trang {i + 1}]\n{page_text}")

    return "\n\n".join(text_parts)


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 200,  # V2: tăng overlap từ 100 → 200
) -> List[str]:
    """
    V2: Chunking cải tiến với overlap lớn hơn và chia theo semantic boundaries.
    """
    if not text.strip():
        return []

    # V2: Thử chia theo [Trang X] markers trước (semantic chunking)
    page_pattern = r"\[Trang \d+\]"
    pages = re.split(f"(?={page_pattern})", text)
    pages = [p.strip() for p in pages if p.strip()]

    # Nếu mỗi trang ngắn, ghép các trang lại thành chunks
    chunks = []
    current_chunk = ""

    for page in pages:
        if len(current_chunk) + len(page) <= chunk_size:
            current_chunk += "\n\n" + page if current_chunk else page
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # Nếu một trang dài hơn chunk_size, chia nhỏ
            if len(page) > chunk_size:
                sub_chunks = _split_long_text(page, chunk_size, overlap)
                chunks.extend(sub_chunks)
                current_chunk = ""
            else:
                current_chunk = page

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else _split_long_text(text, chunk_size, overlap)


def _split_long_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Fallback: chia text dài theo character boundaries."""
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
        start = end - overlap

    return chunks


def check_content_adequacy(chunks: List[str], num_questions: int) -> Dict:
    """
    V2 NEW: Kiểm tra tài liệu có đủ nội dung cho số câu hỏi yêu cầu.

    Returns:
        Dict với keys: is_adequate, recommended_count, reason
    """
    total_chars = sum(len(c) for c in chunks)
    total_words = sum(len(c.split()) for c in chunks)

    # Heuristic: cần ít nhất ~100 words per question cho câu hỏi chất lượng
    recommended_count = max(3, total_words // 100)

    if recommended_count >= num_questions:
        return {
            "is_adequate": True,
            "recommended_count": num_questions,
            "reason": None,
        }
    else:
        return {
            "is_adequate": False,
            "recommended_count": min(recommended_count, num_questions),
            "reason": (
                f"Tài liệu chỉ có ~{total_words} từ, "
                f"chỉ đủ để tạo {recommended_count} câu hỏi chất lượng "
                f"(yêu cầu: {num_questions})."
            ),
        }


def build_meta_summary(chunks: List[str]) -> str:
    """
    V2 NEW: Tạo meta-summary cho two-pass processing.
    Trích xuất key claims từ mỗi chunk để hỗ trợ conflict detection.
    """
    meta_parts = []
    for i, chunk in enumerate(chunks):
        # Lấy 2 dòng đầu tiên làm đại diện
        lines = chunk.split("\n")
        preview = " | ".join(line.strip() for line in lines[:3] if line.strip())
        meta_parts.append(f"[Chunk {i+1}]: {preview[:200]}")

    return "\n".join(meta_parts)
