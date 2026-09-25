"""
AI Study Assistant - Prototype V1
Trợ lý Học tập Thông minh cho Sinh viên Đại học

Tác giả: Ngô Minh Triết
Khóa: AOTS - HCMUT
"""

import streamlit as st
import json
import time
import os
from datetime import datetime

# --- Module imports ---
from document_processor import extract_text_from_pdf, chunk_text
from prompt_engine import (
    build_summary_prompt,
    build_question_prompt,
    build_explain_prompt,
    build_evaluate_prompt,
)
from llm_gateway import call_llm

# --- Page Config ---
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide",
)

# --- Session State Init ---
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "eval_log" not in st.session_state:
    st.session_state.eval_log = []
if "subject" not in st.session_state:
    st.session_state.subject = ""


def main():
    st.title("📚 AI Study Assistant V1")
    st.caption("Trợ lý Học tập Thông minh - Prototype V1")

    # --- Sidebar: Upload Document ---
    with st.sidebar:
        st.header("📄 Upload Tài Liệu")
        uploaded_file = st.file_uploader(
            "Chọn file PDF hoặc TXT",
            type=["pdf", "txt"],
            help="Hỗ trợ file PDF (≤ 50 trang) hoặc TXT (≤ 100KB)",
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
                    if uploaded_file.type == "application/pdf":
                        text = extract_text_from_pdf(uploaded_file)
                    else:
                        text = uploaded_file.read().decode("utf-8")

                    if len(text.strip()) < 50:
                        st.error("File trống hoặc không thể đọc được nội dung.")
                    else:
                        st.session_state.document_text = text
                        st.session_state.chunks = chunk_text(text)
                        st.success(
                            f"✅ Đã xử lý: {len(st.session_state.chunks)} chunks"
                        )

        # --- Model Selection ---
        st.divider()
        st.header("⚙️ Cấu hình")
        model_provider = st.selectbox(
            "LLM Provider",
            ["Claude (Anthropic)", "GPT (OpenAI)"],
            index=0,
        )
        st.session_state.model_provider = (
            "claude" if "Claude" in model_provider else "openai"
        )

        # --- API Key ---
        api_key = st.text_input("API Key", type="password")
        if api_key:
            st.session_state.api_key = api_key

    # --- Main Content: Tabs ---
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
            ["Lớp 1: Key Points", "Lớp 2: Phân tích có cấu trúc", "Lớp 3: Nhận xét sâu"],
            horizontal=True,
        )

        if st.button("Tạo Tóm Tắt", key="btn_summary"):
            if "api_key" not in st.session_state:
                st.error("Vui lòng nhập API Key ở sidebar!")
                return

            with st.spinner("Đang tóm tắt..."):
                start_time = time.time()
                prompt = build_summary_prompt(
                    st.session_state.chunks,
                    st.session_state.subject,
                    summary_level,
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
            st.caption(f"⏱️ Thời gian: {elapsed:.1f}s")

            # Log for evaluation
            st.session_state.eval_log.append({
                "timestamp": datetime.now().isoformat(),
                "function": "summary",
                "level": summary_level,
                "latency_s": round(elapsed, 2),
                "model": st.session_state.model_provider,
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

        if st.button("Tạo Câu Hỏi", key="btn_questions"):
            if "api_key" not in st.session_state:
                st.error("Vui lòng nhập API Key ở sidebar!")
                return

            with st.spinner("Đang tạo câu hỏi..."):
                start_time = time.time()
                prompt = build_question_prompt(
                    st.session_state.chunks,
                    st.session_state.subject,
                    num_questions,
                    difficulty,
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
                anki_prompt = f"""Từ các câu hỏi trên, tạo flashcard Anki ở định dạng TSV.
Mỗi dòng: Question[TAB]Answer
Không có header. Chỉ output nội dung TSV thuần túy.
"""
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
                "difficulty": difficulty,
                "latency_s": round(elapsed, 2),
                "model": st.session_state.model_provider,
            })

    # --- Tab 3: Step-by-Step Explanation ---
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
            })

    # --- Tab 4: Evaluate Answer ---
    with tab4:
        st.header("Đánh Giá Câu Trả Lời")
        question = st.text_area(
            "Câu hỏi:",
            placeholder="Nhập hoặc paste câu hỏi...",
        )
        student_answer = st.text_area(
            "Câu trả lời của bạn:",
            placeholder="Nhập câu trả lời...",
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
            })

    # --- Footer: Disclaimer ---
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
                log_json = json.dumps(st.session_state.eval_log, indent=2, ensure_ascii=False)
                st.download_button(
                    "⬇️ Download Log",
                    log_json,
                    file_name="eval_log.json",
                    mime="application/json",
                )


if __name__ == "__main__":
    main()
