"""
Document Processor Module - V1
Xử lý tài liệu: extract text từ PDF, chunking
"""

import io
from typing import List

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

    # Giới hạn 50 trang
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
    overlap: int = 100,
) -> List[str]:
    """
    Chia text thành các chunks có overlap.

    Args:
        text: Full text đã extract
        chunk_size: Số ký tự tối đa mỗi chunk (xấp xỉ 200-400 tokens)
        overlap: Số ký tự overlap giữa các chunk

    Returns:
        List các chunks
    """
    if not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Tìm điểm cắt tự nhiên (cuối câu, cuối paragraph)
        if end < len(text):
            # Ưu tiên cắt ở cuối paragraph
            newline_pos = text.rfind("\n\n", start, end)
            if newline_pos > start + chunk_size // 2:
                end = newline_pos + 2
            else:
                # Cắt ở cuối câu
                period_pos = text.rfind(". ", start, end)
                if period_pos > start + chunk_size // 2:
                    end = period_pos + 2

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks
