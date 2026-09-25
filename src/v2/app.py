"""
AI Study Assistant - Prototype V2
Cải tiến từ V1 dựa trên kết quả kiểm thử và phân tích 5-Whys

Các cải tiến chính:
1. Strict scope enforcement trong system prompt (fix TC-03)
2. Content adequacy check trước khi tạo câu hỏi (fix TC-06)
3. Two-pass processing với meta-summary cho conflict detection (fix TC-09)
4. Output validation với citation checking

Tác giả: Ngô Minh Triết
Khóa: AOTS - HCMUT
"""

import streamlit as st
import json
import time
import os
from datetime import datetime

from document_processor import (
    extract_text_from_pdf,
    chunk_text,
    check_content_adequacy,
    build_meta_summary,
)
from prompt_engine import (
    build_summary_prompt,
    build_question_prompt,
    build_explain_prompt,
    build_evaluate_prompt,
)
from llm_gateway import call_llm

# --- Page Config ---
st.set_page_config(
    page_title="AI Study Assistant V2",
    page_icon="📚",
    layout="wide",
)

# --- Session State Init ---
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "meta_summary" not in st.session_state:
    st.session_state.meta_summary = ""
if "eval_log" not in st.session_state:
    st.session_state.eval_log = []
if "subject" not in st.session_state:
    st.session_state.subject = ""


def main():
    st.title("📚 AI Study Assistant V2")
    st.caption(
        "Trợ lý Học tập Thông minh - Prototype V2 | "
        "Cải tiến: Strict Grounding, Content Adequacy, Conflict Detection"
    )

    # --- Sidebar ---
    with st.sidebar:
        st.header("📄 Upload Tài Liệu")
        uploaded_file = st.file_uploader(
            "Chọn file PDF hoặc TXT",
            type=["pdf", "txt"],
            help="PDF (≤ 50 trang) hoặc TXT (≤ 100KB)",
        )

        subject = st.text_input(
            "Tên môn học",
            placeholder="VD: Cấu trúc dữ liệu và giải thuật",
        )
        st.session_state.subject = subject

        if uploaded_file:
            file_size = uploaded_file.size
            if file_size > 100 * 1024 and uploaded_file.type == "text/plain":
                st.error("File text vượt quá 100KB!")
            else:
                with st.spinner("Đang xử lý tài liệu..."):
                    try:
                        if uploaded_file.type == "application/pdf":
                            text = extract_text_from_pdf(uploaded_file)
                        else:
                            text = uploaded_file.read().decode("utf-8")

                        if len(text.strip()) < 50:
                            st.error(
                                "File trống hoặc không thể đọc được nội dung. "
                                "Vui lòng upload file PDF có text layer."
                            )
                        else:
                            st.session_state.document_text = text
                            st.session_state.chunks = chunk_text(text)
                            # V2: Build meta-summary
                            st.session_state.meta_summary = build_meta_summary(
                                st.session_state.chunks
                            )
                            st.success(
                                f"✅ Đã xử lý: {len(st.session_state.chunks)} chunks "
                                f"({len(text)} ký tự)"
                            )
                    except ValueError as e:
                        st.error(str(e))

        st.divider()
        st.header("⚙️ Cấu hình")
        model_provider = st.selectbox(
            "LLM Provider",
            [
                "Gemini (Google — Miễn phí)",
                "Claude (Anthropic)",
                "GPT (OpenAI)",
            ],
            index=0,
        )
        provider_map = {
            "Gemini (Google — Miễn phí)": "gemini",
            "Claude (Anthropic)": "claude",
            "GPT (OpenAI)": "openai",
        }
        st.session_state.model_provider = provider_map[model_provider]

        # Hướng dẫn lấy API key theo provider
        help_urls = {
            "gemini": "Miễn phí tại: https://aistudio.google.com/apikey",
            "claude": "Đăng ký tại: https://console.anthropic.com/",
            "openai": "Đăng ký tại: https://platform.openai.com/api-keys",
        }
        api_key = st.text_input(
            "API Key",
            type="password",
            help=help_urls[st.session_state.model_provider],
        )
        if api_key:
            st.session_state.api_key = api_key

        # V2: Hiển thị meta-summary
        if st.session_state.meta_summary:
            with st.expander("📋 Meta-summary (debug)"):
                st.text(st.session_state.meta_summary[:500])

    # --- Main Content ---
    if not st.session_state.document_text:
        st.info("👈 Hãy upload tài liệu ở sidebar để bắt đầu.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📝 Tóm Tắt", "❓ Câu Hỏi Ôn Tập", "💡 Giải Thích", "📊 Đánh Giá"]
    )

    # --- Tab 1: Summarize ---
    with tab1:
        st.header("Tóm Tắt Tài Liệu")
        summary_level = st.radio(
            "Mức độ tóm tắt:",
            [
                "Lớp 1: Key Points",
                "Lớp 2: Phân tích có cấu trúc",
                "Lớp 3: Nhận xét sâu",
            ],
            horizontal=True,
        )

        if st.button("Tạo Tóm Tắt", key="btn_summary"):
            if "api_key" not in st.session_state:
                st.error("Vui lòng nhập API Key ở sidebar!")
                return

            with st.spinner("Đang tóm tắt (two-pass processing)..."):
                start_time = time.time()
                # V2: Two-pass with meta-summary
                prompt = build_summary_prompt(
                    st.session_state.chunks,
                    st.session_state.subject,
                    summary_level,
                    meta_summary=st.session_state.meta_summary,
                )
                response = call_llm(
                    prompt,
                    st.session_state.model_provider,
                    st.session_state.api_key,
                    temperature=0.3,
                    max_tokens=2000,
                )
                elapsed = time.time() - start_time

            st.markdown(response)
            st.caption(f"⏱️ Thời gian: {elapsed:.1f}s | Model: {st.session_state.model_provider}")

            st.session_state.eval_log.append({
                "timestamp": datetime.now().isoformat(),
                "function": "summary",
                "level": summary_level,
                "latency_s": round(elapsed, 2),
                "model": st.session_state.model_provider,
                "version": "V2",
            })

    # --- Tab 2: Question Generation ---
    with tab2:
        st.header("Tạo Câu Hỏi Ôn Tập")
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.slider("Số lượng câu hỏi:", 5, 20, 10)
        with col2:
            difficulty = st.selectbox(
                "Phân bố mức độ:",
                [
                    "Cân bằng (40% Recall, 30% Apply, 30% Analyze)",
                    "Dễ (70% Recall, 20% Apply, 10% Analyze)",
                    "Khó (20% Recall, 30% Apply, 50% Analyze)",
                ],
            )

        # V2: Content adequacy check
        adequacy = check_content_adequacy(st.session_state.chunks, num_questions)
        if not adequacy["is_adequate"]:
            st.warning(
                f"⚠️ {adequacy['reason']} "
                f"Đề xuất: tạo {adequacy['recommended_count']} câu."
            )

        if st.button("Tạo Câu Hỏi", key="btn_questions"):
            if "api_key" not in st.session_state:
                st.error("Vui lòng nhập API Key ở sidebar!")
                return

            with st.spinner("Đang tạo câu hỏi..."):
                start_time = time.time()
                # V2: Pass content adequacy info
                prompt = build_question_prompt(
                    st.session_state.chunks,
                    st.session_state.subject,
                    num_questions,
                    difficulty,
                    content_adequacy=adequacy,
                )
                response = call_llm(
                    prompt,
                    st.session_state.model_provider,
                    st.session_state.api_key,
                    temperature=0.7,
                    max_tokens=3000,
                )
                elapsed = time.time() - start_time

            st.markdown(response)
            st.caption(f"⏱️ Thời gian: {elapsed:.1f}s")

            # Anki export
            st.divider()
            st.subheader("📥 Xuất Anki Flashcards")
            if st.button("Tạo file Anki TSV", key="btn_anki"):
                anki_prompt = (
                    "Từ các câu hỏi trên, tạo flashcard Anki ở định dạng TSV.\n"
                    "Mỗi dòng: Question[TAB]Answer\n"
                    "Không header. Chỉ output TSV thuần túy."
                )
                anki_response = call_llm(
                    anki_prompt,
                    st.session_state.model_provider,
                    st.session_state.api_key,
                    temperature=0.3,
                    max_tokens=2000,
                )
                st.download_button(
                    "⬇️ Download Anki TSV",
                    anki_response,
                    file_name="flashcards.tsv",
                    mime="text/tab-separated-values",
                )

            st.session_state.eval_log.append({
                "timestamp": datetime.now().isoformat(),
                "function": "question_gen",
                "num_questions": num_questions,
                "actual_recommended": adequacy["recommended_count"],
                "difficulty": difficulty,
                "latency_s": round(elapsed, 2),
                "model": st.session_state.model_provider,
                "version": "V2",
            })

    # --- Tab 3: Explanation ---
    with tab3:
        st.header("Giải Thích Từng Bước")
        concept = st.text_input(
            "Nhập khái niệm cần giải thích:",
            placeholder="VD: Binary Search Tree",
        )
        mode = st.radio(
            "Chế độ:",
            ["Chain of Thought (giải thích từng bước)", "Socratic Tutoring (hỏi ngược)"],
            horizontal=True,
        )

        if st.button("Giải Thích", key="btn_explain") and concept:
            if "api_key" not in st.session_state:
                st.error("Vui lòng nhập API Key ở sidebar!")
                return

            with st.spinner("Đang giải thích..."):
                start_time = time.time()
                prompt = build_explain_prompt(
                    st.session_state.chunks,
                    concept,
                    mode,
                )
                response = call_llm(
                    prompt,
                    st.session_state.model_provider,
                    st.session_state.api_key,
                    temperature=0.3,
                    max_tokens=3000,
                )
                elapsed = time.time() - start_time

            st.markdown(response)
            st.caption(f"⏱️ Thời gian: {elapsed:.1f}s")

            st.session_state.eval_log.append({
                "timestamp": datetime.now().isoformat(),
                "function": "explain",
                "concept": concept,
                "mode": mode,
                "latency_s": round(elapsed, 2),
                "model": st.session_state.model_provider,
                "version": "V2",
            })

    # --- Tab 4: Evaluate ---
    with tab4:
        st.header("Đánh Giá Câu Trả Lời")
        question = st.text_area("Câu hỏi:", placeholder="Nhập câu hỏi...")
        student_answer = st.text_area(
            "Câu trả lời của bạn:", placeholder="Nhập câu trả lời..."
        )

        if st.button("Đánh Giá", key="btn_evaluate") and question and student_answer:
            if "api_key" not in st.session_state:
                st.error("Vui lòng nhập API Key ở sidebar!")
                return

            with st.spinner("Đang đánh giá..."):
                start_time = time.time()
                prompt = build_evaluate_prompt(
                    st.session_state.chunks,
                    question,
                    student_answer,
                )
                response = call_llm(
                    prompt,
                    st.session_state.model_provider,
                    st.session_state.api_key,
                    temperature=0.3,
                    max_tokens=1500,
                )
                elapsed = time.time() - start_time

            st.markdown(response)
            st.caption(f"⏱️ Thời gian: {elapsed:.1f}s")

            st.session_state.eval_log.append({
                "timestamp": datetime.now().isoformat(),
                "function": "evaluate",
                "latency_s": round(elapsed, 2),
                "model": st.session_state.model_provider,
                "version": "V2",
            })

    # --- Footer ---
    st.divider()
    st.caption(
        "⚠️ **Disclaimer**: Kết quả từ AI cần được kiểm chứng với tài liệu gốc. "
        "AI có thể tạo ra thông tin không chính xác (hallucination). "
        "Luôn áp dụng tư duy Zero-Trust khi sử dụng kết quả AI."
    )

    # --- Export eval log ---
    if st.session_state.eval_log:
        with st.sidebar:
            st.divider()
            if st.button("📊 Xuất Eval Log"):
                log_json = json.dumps(
                    st.session_state.eval_log, indent=2, ensure_ascii=False
                )
                st.download_button(
                    "⬇️ Download Log",
                    log_json,
                    file_name="eval_log_v2.json",
                    mime="application/json",
                )


if __name__ == "__main__":
    main()
