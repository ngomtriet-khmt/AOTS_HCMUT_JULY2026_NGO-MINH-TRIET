"""
LLM Gateway Module - V1
Quản lý kết nối với các LLM providers (Claude, OpenAI)
Hỗ trợ model swap cho testing
"""

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def call_llm(
    prompt: str,
    provider: str = "claude",
    api_key: str = "",
    temperature: float = 0.3,
    max_tokens: int = 2000,
    retry_count: int = 2,
) -> str:
    """
    Gọi LLM API với retry logic.

    Args:
        prompt: Full prompt (system + user)
        provider: "claude" hoặc "openai"
        api_key: API key
        temperature: 0.0-1.0
        max_tokens: Giới hạn output tokens
        retry_count: Số lần retry khi lỗi

    Returns:
        Response text từ LLM
    """
    if not api_key:
        return "❌ Lỗi: Chưa cung cấp API Key. Vui lòng nhập API Key ở sidebar."

    for attempt in range(retry_count + 1):
        try:
            if provider == "claude":
                return _call_claude(prompt, api_key, temperature, max_tokens)
            elif provider == "openai":
                return _call_openai(prompt, api_key, temperature, max_tokens)
            else:
                return f"❌ Provider không hỗ trợ: {provider}"

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retry_count:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s
                time.sleep(wait_time)
            else:
                return f"❌ Lỗi sau {retry_count + 1} lần thử: {str(e)}"

    return "❌ Lỗi không xác định"


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

    # Tách system prompt và user message
    parts = prompt.split("\n\n", 1)
    system_msg = parts[0] if len(parts) > 1 else ""
    user_msg = parts[1] if len(parts) > 1 else prompt

    response = client.messages.create(
        model="claude-sonnet-4-6-20250819",
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_msg,
        messages=[
            {"role": "user", "content": user_msg}
        ],
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

    # Tách system prompt và user message
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
