"""
LLM Gateway Module - V2
Cải tiến: output validation, citation checking, detailed logging
"""

import time
import re
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def call_llm(
    prompt: str,
    provider: str = "gemini",
    api_key: str = "",
    temperature: float = 0.3,
    max_tokens: int = 2000,
    retry_count: int = 2,
) -> str:
    """Gọi LLM API với retry logic và output validation."""
    if not api_key:
        return "❌ Lỗi: Chưa cung cấp API Key. Vui lòng nhập API Key ở sidebar."

    for attempt in range(retry_count + 1):
        try:
            if provider == "gemini":
                response = _call_gemini(prompt, api_key, temperature, max_tokens)
            elif provider == "claude":
                response = _call_claude(prompt, api_key, temperature, max_tokens)
            elif provider == "openai":
                response = _call_openai(prompt, api_key, temperature, max_tokens)
            else:
                return f"❌ Provider không hỗ trợ: {provider}"

            # V2: Output validation
            validation = validate_output(response)
            if validation["warnings"]:
                warning_text = "\n".join(
                    f"⚠️ {w}" for w in validation["warnings"]
                )
                response = f"{warning_text}\n\n---\n\n{response}"

            return response

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retry_count:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                return f"❌ Lỗi sau {retry_count + 1} lần thử: {str(e)}"

    return "❌ Lỗi không xác định"


def validate_output(response: str) -> Dict:
    """
    V2 NEW: Kiểm tra chất lượng output.
    Returns dict với 'warnings' list.
    """
    warnings = []

    # Check 1: Có citations không?
    citations = re.findall(r"\[Trang \d+\]|\[Section .+?\]|\[Trích dẫn:.+?\]", response)
    paragraphs = [p for p in response.split("\n\n") if len(p.strip()) > 100]

    if paragraphs and not citations:
        warnings.append(
            "Kết quả không chứa trích dẫn nguồn. "
            "Vui lòng đối chiếu với tài liệu gốc để xác minh."
        )

    # Check 2: Có dấu hiệu thông tin ngoài tài liệu?
    outside_indicators = [
        "theo kiến thức chung",
        "thông thường",
        "nói chung",
        "theo hiểu biết của tôi",
        "ngoài tài liệu",
        "bổ sung thêm",
    ]
    for indicator in outside_indicators:
        if indicator in response.lower():
            warnings.append(
                f'Phát hiện cụm từ "{indicator}" — '
                "có thể chứa thông tin ngoài tài liệu. Cần kiểm chứng."
            )
            break

    return {"warnings": warnings, "citation_count": len(citations)}


def _call_gemini(
    prompt: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """Gọi Google Gemini API (miễn phí)."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return "❌ Chưa cài đặt thư viện google-genai. Chạy: pip install google-genai"

    client = genai.Client(api_key=api_key)

    # Tách system prompt và user message
    parts = prompt.split("\n\n", 1)
    system_msg = parts[0] if len(parts) > 1 else ""
    user_msg = parts[1] if len(parts) > 1 else prompt

    config = types.GenerateContentConfig(
        system_instruction=system_msg if system_msg else None,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_msg,
        config=config,
    )

    return response.text


def _call_claude(
    prompt: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """Gọi Anthropic Claude API."""
    try:
        from anthropic import Anthropic
    except ImportError:
        return "❌ Chưa cài đặt thư viện anthropic. Chạy: pip install anthropic"

    client = Anthropic(api_key=api_key)

    parts = prompt.split("\n\n", 1)
    system_msg = parts[0] if len(parts) > 1 else ""
    user_msg = parts[1] if len(parts) > 1 else prompt

    response = client.messages.create(
        model="claude-sonnet-4-6-20250819",
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_msg,
        messages=[{"role": "user", "content": user_msg}],
    )

    return response.content[0].text


def _call_openai(
    prompt: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """Gọi OpenAI GPT API."""
    try:
        from openai import OpenAI
    except ImportError:
        return "❌ Chưa cài đặt thư viện openai. Chạy: pip install openai"

    client = OpenAI(api_key=api_key)

    parts = prompt.split("\n\n", 1)
    system_msg = parts[0] if len(parts) > 1 else ""
    user_msg = parts[1] if len(parts) > 1 else prompt

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    return response.choices[0].message.content
