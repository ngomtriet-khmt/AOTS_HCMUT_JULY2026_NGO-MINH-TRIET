"""
LLM Gateway Module - V3 (Gemini-only)

Nhiệm vụ:
- Gọi Google Gemini API (chỉ dùng Google AI API key).
- Orchestrate pipeline xử lý file lớn:
    + summary: single-call nếu vừa context window, ngược lại tự động MAP-REDUCE.
    + question/explain/evaluate: chọn ngữ cảnh phù hợp (select_relevant_context).
- Output validation: cảnh báo khi thiếu trích dẫn hoặc có dấu hiệu kiến thức ngoài tài liệu.

Tác giả: Ngô Minh Triết — AOTS HCMUT
"""

import time
import re
import logging
from typing import Dict, List, Callable, Optional, Tuple

import prompt_engine as pe
import document_processor as dp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Cấu hình model & ngân sách token ---
DEFAULT_MODEL = "gemini-2.0-flash"

# Danh sách fallback: nếu model chính bị 503/overloaded, tự động thử model tiếp theo.
FALLBACK_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

# Trần token đầu vào cho 1 lần gọi (chừa chỗ cho output & overhead trong ~1M context).
SINGLE_CALL_TOKEN_BUDGET = 800_000

# Kích thước tối đa mỗi segment ở giai đoạn MAP (theo ký tự, ~40k token/segment).
MAP_SEGMENT_CHARS = 120_000


# ---------------------------------------------------------------------------
# Lõi gọi Gemini
# ---------------------------------------------------------------------------
def generate(
    system: str,
    user: str,
    api_key: str,
    temperature: float = 0.3,
    max_tokens: int = 4000,
    model: str = DEFAULT_MODEL,
    retry_count: int = 3,
    validate: bool = True,
) -> str:
    """Gọi Gemini với retry + fallback model + (tuỳ chọn) output validation."""
    if not api_key:
        return "❌ Lỗi: Chưa cung cấp Google AI API Key. Vui lòng nhập ở sidebar."

    # Xây danh sách models: model được chọn trước, rồi fallback (bỏ trùng).
    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_error = ""

    for current_model in models_to_try:
        for attempt in range(retry_count + 1):
            try:
                response = _call_gemini(
                    system, user, api_key, temperature, max_tokens, current_model
                )
                if validate:
                    warnings = validate_output(response)["warnings"]
                    if warnings:
                        prefix = "\n".join(f"⚠️ {w}" for w in warnings)
                        response = f"{prefix}\n\n---\n\n{response}"
                # Ghi nhận model thực tế đã dùng (để hiển thị trên UI).
                generate.last_model_used = current_model
                return response
            except Exception as e:
                last_error = str(e)
                is_overloaded = any(
                    code in last_error for code in ["503", "429", "UNAVAILABLE", "overloaded"]
                )
                logger.warning(
                    f"[{current_model}] Attempt {attempt + 1}/{retry_count + 1} failed: {e}"
                )
                if is_overloaded and attempt < retry_count:
                    wait = min(2 ** (attempt + 1), 16)
                    logger.info(f"  → Retry sau {wait}s...")
                    time.sleep(wait)
                elif is_overloaded:
                    # Hết retry cho model này → thử fallback model tiếp theo.
                    logger.info(f"  → Model {current_model} quá tải, chuyển sang fallback...")
                    break
                else:
                    # Lỗi khác (auth, invalid request...) → không cần thử model khác.
                    generate.last_model_used = current_model
                    return f"❌ Lỗi: {last_error}"

    generate.last_model_used = models_to_try[-1]
    return (
        f"❌ Tất cả models đều không khả dụng sau nhiều lần thử.\n\n"
        f"Models đã thử: {', '.join(models_to_try)}\n\n"
        f"Lỗi cuối: {last_error}\n\n"
        f"💡 Gợi ý: Đợi vài phút rồi thử lại, hoặc kiểm tra API key."
    )

# Thuộc tính lưu model thực tế đã dùng lần gần nhất.
generate.last_model_used = DEFAULT_MODEL


def _call_gemini(
    system: str,
    user: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    model: str,
) -> str:
    """Gọi Google Gemini API (google-genai SDK)."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError(
            "Chưa cài đặt thư viện google-genai. Chạy: pip install google-genai"
        )

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        system_instruction=system or None,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    response = client.models.generate_content(
        model=model,
        contents=user,
        config=config,
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError(
            "Model không trả về nội dung (có thể bị chặn bởi safety filter "
            "hoặc vượt giới hạn output)."
        )
    return text


def validate_output(response: str) -> Dict:
    """Kiểm tra chất lượng output: trích dẫn & dấu hiệu kiến thức ngoài tài liệu."""
    warnings = []

    citations = re.findall(dp.CITATION_MARKER, response)
    long_paragraphs = [p for p in response.split("\n\n") if len(p.strip()) > 100]
    if long_paragraphs and not citations:
        warnings.append(
            "Kết quả không chứa trích dẫn nguồn. "
            "Vui lòng đối chiếu với tài liệu gốc để xác minh."
        )

    outside_indicators = [
        "theo kiến thức chung",
        "thông thường",
        "theo hiểu biết của tôi",
        "ngoài tài liệu",
    ]
    lower = response.lower()
    for indicator in outside_indicators:
        if indicator in lower:
            warnings.append(
                f'Phát hiện cụm từ "{indicator}" — có thể chứa thông tin '
                "ngoài tài liệu. Cần kiểm chứng."
            )
            break

    return {"warnings": warnings, "citation_count": len(citations)}


# ---------------------------------------------------------------------------
# Chuẩn bị ngữ cảnh (dùng chung, có che PII tùy chọn)
# ---------------------------------------------------------------------------
def _prepare_context(
    full_text: str,
    chunks: List[str],
    query: str = "",
    sanitize: bool = False,
    budget: int = SINGLE_CALL_TOKEN_BUDGET,
) -> Tuple[str, bool]:
    context, truncated = dp.select_relevant_context(
        full_text, chunks, budget_tokens=budget, query=query
    )
    if sanitize:
        context, _ = dp.sanitize_text(context)
    return context, truncated


# ---------------------------------------------------------------------------
# Orchestration: TÓM TẮT (hybrid single-call / map-reduce)
# ---------------------------------------------------------------------------
def run_summary(
    full_text: str,
    chunks: List[str],
    subject: str,
    level: str,
    api_key: str,
    meta_summary: str = "",
    sanitize: bool = False,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
    model: str = DEFAULT_MODEL,
) -> Tuple[str, str]:
    """
    Tóm tắt tài liệu. Trả về (kết_quả, chế_độ) với chế_độ ∈ {"single-call", "map-reduce"}.
    """
    working_text = full_text
    if sanitize:
        working_text, _ = dp.sanitize_text(working_text)

    # Đủ nhỏ → gửi 1 lần, tận dụng context lớn của Gemini.
    if dp.estimate_tokens(working_text) <= SINGLE_CALL_TOKEN_BUDGET:
        if progress_cb:
            progress_cb(1, 1, "Đang tóm tắt (single-call)...")
        user = pe.build_summary_prompt(working_text, subject, level, meta_summary)
        return generate(pe.SYSTEM_PROMPT, user, api_key, 0.3, 4000, model), "single-call"

    # Quá lớn → MAP-REDUCE.
    segments = dp.split_into_segments(working_text, MAP_SEGMENT_CHARS)
    partials: List[str] = []
    for i, seg in enumerate(segments):
        if progress_cb:
            progress_cb(i, len(segments) + 1, f"MAP: tóm tắt phần {i + 1}/{len(segments)}...")
        user = pe.build_map_summary_prompt(seg, subject)
        part = generate(
            pe.SYSTEM_PROMPT, user, api_key, 0.3, 2000, model, validate=False
        )
        partials.append(part)

    if progress_cb:
        progress_cb(len(segments), len(segments) + 1, "REDUCE: tổng hợp kết quả...")

    # Nếu tổng các bản tóm tắt bộ phận VẪN quá lớn → reduce theo tầng.
    while dp.estimate_tokens("\n\n".join(partials)) > SINGLE_CALL_TOKEN_BUDGET:
        grouped: List[str] = []
        step = 5
        for i in range(0, len(partials), step):
            batch = partials[i:i + step]
            user = pe.build_reduce_summary_prompt(batch, subject, level)
            grouped.append(
                generate(pe.SYSTEM_PROMPT, user, api_key, 0.3, 3000, model, validate=False)
            )
        partials = grouped

    user = pe.build_reduce_summary_prompt(partials, subject, level)
    result = generate(pe.SYSTEM_PROMPT, user, api_key, 0.3, 4000, model)
    return result, "map-reduce"


# ---------------------------------------------------------------------------
# Orchestration: CÂU HỎI / GIẢI THÍCH / ĐÁNH GIÁ
# ---------------------------------------------------------------------------
def run_questions(
    full_text: str,
    chunks: List[str],
    subject: str,
    num_questions: int,
    difficulty: str,
    content_adequacy: dict,
    api_key: str,
    sanitize: bool = False,
    model: str = DEFAULT_MODEL,
) -> str:
    context, truncated = _prepare_context(full_text, chunks, sanitize=sanitize)
    user = pe.build_question_prompt(
        context, subject, num_questions, difficulty,
        content_adequacy=content_adequacy, context_truncated=truncated,
    )
    return generate(pe.SYSTEM_PROMPT, user, api_key, 0.7, 3000, model)


def run_explain(
    full_text: str,
    chunks: List[str],
    concept: str,
    mode: str,
    api_key: str,
    sanitize: bool = False,
    model: str = DEFAULT_MODEL,
) -> str:
    context, _ = _prepare_context(full_text, chunks, query=concept, sanitize=sanitize)
    user = pe.build_explain_prompt(context, concept, mode)
    return generate(pe.SYSTEM_PROMPT, user, api_key, 0.3, 3000, model)


def run_evaluate(
    full_text: str,
    chunks: List[str],
    question: str,
    student_answer: str,
    api_key: str,
    sanitize: bool = False,
    model: str = DEFAULT_MODEL,
) -> str:
    query = f"{question} {student_answer}"
    context, _ = _prepare_context(full_text, chunks, query=query, sanitize=sanitize)
    user = pe.build_evaluate_prompt(context, question, student_answer)
    return generate(pe.SYSTEM_PROMPT, user, api_key, 0.3, 1500, model)


def run_anki(previous_questions: str, api_key: str, model: str = DEFAULT_MODEL) -> str:
    """Chuyển bộ câu hỏi thành TSV cho Anki."""
    user = (
        "Từ các câu hỏi dưới đây, tạo flashcard Anki ở định dạng TSV.\n"
        "Mỗi dòng: Question[TAB]Answer. Không header. Chỉ output TSV thuần túy.\n\n"
        f"{previous_questions}"
    )
    return generate("", user, api_key, 0.3, 2000, model, validate=False)
