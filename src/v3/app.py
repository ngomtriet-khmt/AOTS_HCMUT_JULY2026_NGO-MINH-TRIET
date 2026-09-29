"""
AI Study Assistant - Prototype V3 (Gemini-only, hỗ trợ file lớn)

Cải tiến so với V2:
1. CHỈ dùng Google Gemini (chỉ cần Google AI API key) — bỏ Claude/OpenAI cho gọn nhẹ.
2. Hỗ trợ FILE LỚN: bỏ giới hạn 50 trang/100KB, thêm DOCX. Tự động chọn
   single-call (tận dụng context ~1M token) hoặc MAP-REDUCE khi tài liệu quá lớn.
3. Che PII trước khi gửi model (tùy chọn) — học từ TaskLens.
4. Hiển thị ước lượng token + chế độ xử lý + thanh tiến trình cho tác vụ dài.

Tác giả: Ngô Minh Triết — AOTS HCMUT
"""

import streamlit as st
import json
import time
from datetime import datetime

import document_processor as dp
import llm_gateway as gw

st.set_page_config(page_title="AI Study Assistant V3", page_icon="📚", layout="wide")

# --- Session State ---
_defaults = {
    "document_text": "",
    "chunks": [],
    "meta_summary": "",
    "eval_log": [],
    "subject": "",
    "api_key": "",
    "sanitize_pii": True,
    "last_questions": "",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _log(entry: dict):
    entry.update({"timestamp": datetime.now().isoformat(), "version": "V3"})
    st.session_state.eval_log.append(entry)


def main():
    st.title("📚 AI Study Assistant V3")
    st.caption(
        "Gemini-only · Hỗ trợ file lớn (single-call ↔ map-reduce) · "
        "Strict Grounding · Che PII"
    )

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.header("🔑 Google AI API Key")
        api_key = st.text_input(
            "API Key",
            type="password",
            value=st.session_state.api_key,
            help="Miễn phí tại: https://aistudio.google.com/apikey (bắt đầu bằng AIza...)",
        )
        if api_key:
            st.session_state.api_key = api_key

        st.divider()
        st.header("📄 Upload Tài Liệu")
        uploaded_file = st.file_uploader(
            "Chọn file PDF, DOCX hoặc TXT",
            type=["pdf", "docx", "txt"],
            help="Hỗ trợ file lớn — không giới hạn số trang.",
        )
        st.session_state.subject = st.text_input(
            "Tên môn học",
            value=st.session_state.subject,
            placeholder="VD: Cấu trúc dữ liệu và giải thuật",
        )

        if uploaded_file:
            with st.spinner("Đang xử lý tài liệu..."):
                try:
                    text = dp.extract_text(uploaded_file)
                    if len(text.strip()) < 50:
                        st.error("File trống hoặc không đọc được nội dung.")
                    else:
                        st.session_state.document_text = text
                        st.session_state.chunks = dp.chunk_text(text)
                        st.session_state.meta_summary = dp.build_meta_summary(
                            st.session_state.chunks
                        )
                        tokens = dp.estimate_tokens(text)
                        mode = (
                            "single-call"
                            if tokens <= gw.SINGLE_CALL_TOKEN_BUDGET
                            else "map-reduce"
                        )
                        st.success(
                            f"✅ {len(st.session_state.chunks)} chunks · "
                            f"{len(text):,} ký tự · ~{tokens:,} token"
                        )
                        st.info(f"Chế độ xử lý tóm tắt: **{mode}**")
                except (ValueError, ImportError) as e:
                    st.error(str(e))

        st.divider()
        st.header("⚙️ Cấu hình")
        model_options = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        selected_model = st.selectbox(
            "Model chính",
            model_options,
            help="Nếu model này bị quá tải (503), sẽ tự động fallback sang model khác.",
        )
        st.session_state["selected_model"] = selected_model
        fallback_list = [m for m in model_options if m != selected_model]
        if fallback_list:
            st.caption(f"Fallback: {' → '.join(fallback_list)}")
        st.session_state.sanitize_pii = st.checkbox(
            "🔒 Che PII trước khi gửi (email, SĐT, MSSV, API key)",
            value=st.session_state.sanitize_pii,
        )

        if st.session_state.meta_summary:
            with st.expander("📋 Meta-summary (debug)"):
                st.text(st.session_state.meta_summary[:800])

    # ---------------- Main ----------------
    if not st.session_state.document_text:
        st.info("👈 Nhập API Key và upload tài liệu ở sidebar để bắt đầu.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📝 Tóm Tắt", "❓ Câu Hỏi Ôn Tập", "💡 Giải Thích", "📊 Đánh Giá"]
    )

    _tab_summary(tab1)
    _tab_questions(tab2)
    _tab_explain(tab3)
    _tab_evaluate(tab4)

    # ---------------- Footer ----------------
    st.divider()
    st.caption(
        "⚠️ **Disclaimer**: Kết quả từ AI cần được kiểm chứng với tài liệu gốc. "
        "AI có thể tạo thông tin không chính xác (hallucination). "
        "Luôn áp dụng tư duy Zero-Trust khi dùng kết quả AI."
    )
    _export_log()


def _require_key() -> bool:
    if not st.session_state.api_key:
        st.error("Vui lòng nhập Google AI API Key ở sidebar!")
        return False
    return True


# ---------------- Tab: Tóm tắt ----------------
def _tab_summary(tab):
    with tab:
        st.header("Tóm Tắt Tài Liệu")
        level = st.radio(
            "Mức độ tóm tắt:",
            ["Lớp 1: Key Points", "Lớp 2: Phân tích có cấu trúc", "Lớp 3: Nhận xét sâu"],
            horizontal=True,
        )
        if st.button("Tạo Tóm Tắt", key="btn_summary"):
            if not _require_key():
                return

            progress = st.progress(0.0, text="Bắt đầu...")

            def cb(done, total, msg):
                progress.progress(min(done / max(total, 1), 1.0), text=msg)

            start = time.time()
            response, mode = gw.run_summary(
                st.session_state.document_text,
                st.session_state.chunks,
                st.session_state.subject,
                level,
                st.session_state.api_key,
                meta_summary=st.session_state.meta_summary,
                sanitize=st.session_state.sanitize_pii,
                progress_cb=cb,
                model=st.session_state.get("selected_model", gw.DEFAULT_MODEL),
            )
            elapsed = time.time() - start
            progress.empty()

            st.markdown(response)
            used = gw.generate.last_model_used
            st.caption(f"⏱️ {elapsed:.1f}s · Chế độ: {mode} · Model: {used}")
            _log({"function": "summary", "level": level, "mode": mode,
                  "latency_s": round(elapsed, 2)})


# ---------------- Tab: Câu hỏi ----------------
def _tab_questions(tab):
    with tab:
        st.header("Tạo Câu Hỏi Ôn Tập")
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.slider("Số lượng câu hỏi:", 5, 30, 10)
        with col2:
            difficulty = st.selectbox(
                "Phân bố mức độ:",
                [
                    "Cân bằng (40% Recall, 30% Apply, 30% Analyze)",
                    "Dễ (70% Recall, 20% Apply, 10% Analyze)",
                    "Khó (20% Recall, 30% Apply, 50% Analyze)",
                ],
            )

        adequacy = dp.check_content_adequacy(st.session_state.chunks, num_questions)
        if not adequacy["is_adequate"]:
            st.warning(
                f"⚠️ {adequacy['reason']} Đề xuất: tạo {adequacy['recommended_count']} câu."
            )

        if st.button("Tạo Câu Hỏi", key="btn_questions"):
            if not _require_key():
                return
            with st.spinner("Đang tạo câu hỏi..."):
                start = time.time()
                response = gw.run_questions(
                    st.session_state.document_text,
                    st.session_state.chunks,
                    st.session_state.subject,
                    num_questions,
                    difficulty,
                    adequacy,
                    st.session_state.api_key,
                    sanitize=st.session_state.sanitize_pii,
                    model=st.session_state.get("selected_model", gw.DEFAULT_MODEL),
                )
                elapsed = time.time() - start
            st.session_state.last_questions = response
            st.markdown(response)
            st.caption(f"⏱️ {elapsed:.1f}s · Model: {gw.generate.last_model_used}")
            _log({"function": "question_gen", "num_questions": num_questions,
                  "difficulty": difficulty, "latency_s": round(elapsed, 2)})

        # Anki export dựa trên bộ câu hỏi gần nhất.
        if st.session_state.last_questions:
            st.divider()
            st.subheader("📥 Xuất Anki Flashcards")
            if st.button("Tạo file Anki TSV", key="btn_anki"):
                if not _require_key():
                    return
                with st.spinner("Đang tạo TSV..."):
                    tsv = gw.run_anki(
                        st.session_state.last_questions, st.session_state.api_key
                    )
                st.download_button(
                    "⬇️ Download Anki TSV", tsv,
                    file_name="flashcards.tsv", mime="text/tab-separated-values",
                )


# ---------------- Tab: Giải thích ----------------
def _tab_explain(tab):
    with tab:
        st.header("Giải Thích Từng Bước")
        concept = st.text_input(
            "Nhập khái niệm cần giải thích:", placeholder="VD: Binary Search Tree"
        )
        mode = st.radio(
            "Chế độ:",
            ["Chain of Thought (giải thích từng bước)", "Socratic Tutoring (hỏi ngược)"],
            horizontal=True,
        )
        if st.button("Giải Thích", key="btn_explain") and concept:
            if not _require_key():
                return
            with st.spinner("Đang giải thích..."):
                start = time.time()
                response = gw.run_explain(
                    st.session_state.document_text,
                    st.session_state.chunks,
                    concept,
                    mode,
                    st.session_state.api_key,
                    sanitize=st.session_state.sanitize_pii,
                    model=st.session_state.get("selected_model", gw.DEFAULT_MODEL),
                )
                elapsed = time.time() - start
            st.markdown(response)
            st.caption(f"⏱️ {elapsed:.1f}s · Model: {gw.generate.last_model_used}")
            _log({"function": "explain", "concept": concept, "mode": mode,
                  "latency_s": round(elapsed, 2)})


# ---------------- Tab: Đánh giá ----------------
def _tab_evaluate(tab):
    with tab:
        st.header("Đánh Giá Câu Trả Lời")
        question = st.text_area("Câu hỏi:", placeholder="Nhập câu hỏi...")
        student_answer = st.text_area("Câu trả lời của bạn:", placeholder="Nhập câu trả lời...")
        if st.button("Đánh Giá", key="btn_evaluate") and question and student_answer:
            if not _require_key():
                return
            with st.spinner("Đang đánh giá..."):
                start = time.time()
                response = gw.run_evaluate(
                    st.session_state.document_text,
                    st.session_state.chunks,
                    question,
                    student_answer,
                    st.session_state.api_key,
                    sanitize=st.session_state.sanitize_pii,
                    model=st.session_state.get("selected_model", gw.DEFAULT_MODEL),
                )
                elapsed = time.time() - start
            st.markdown(response)
            st.caption(f"⏱️ {elapsed:.1f}s · Model: {gw.generate.last_model_used}")
            _log({"function": "evaluate", "latency_s": round(elapsed, 2)})


def _export_log():
    if st.session_state.eval_log:
        with st.sidebar:
            st.divider()
            if st.button("📊 Xuất Eval Log"):
                log_json = json.dumps(
                    st.session_state.eval_log, indent=2, ensure_ascii=False
                )
                st.download_button(
                    "⬇️ Download Log", log_json,
                    file_name="eval_log_v3.json", mime="application/json",
                )


if __name__ == "__main__":
    main()
