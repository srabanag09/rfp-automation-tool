"""
RFP Automation Tool
AI-powered RFP response generator using Claude, with retrieval-augmented
generation over a knowledge base of past RFP answers.

Built by Srabana Guha
"""

import json
import io
import os
from datetime import datetime

import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import anthropic

from theme import inject_theme

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="RFP Automation Tool", page_icon="📄", layout="wide")
inject_theme()

KB_PATH = "knowledge_base.json"
MODEL = "claude-sonnet-5"


def load_knowledge_base():
    if os.path.exists(KB_PATH):
        with open(KB_PATH, "r") as f:
            return json.load(f)
    return []


def save_knowledge_base(kb):
    with open(KB_PATH, "w") as f:
        json.dump(kb, f, indent=2)


def get_api_key():
    # Priority: Streamlit secrets (for deployed app) -> env var -> sidebar input
    # st.secrets raises StreamlitSecretNotFoundError if no secrets.toml exists at
    # all (not just if the key is missing), so this must be caught explicitly.
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    return st.session_state.get("manual_api_key", "")


def retrieve_relevant_answers(query, kb, top_k=3):
    """TF-IDF cosine similarity retrieval over past Q&A pairs."""
    if not kb:
        return []

    questions = [item["question"] for item in kb]
    corpus = questions + [query]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(corpus)

    query_vec = tfidf[-1]
    doc_vecs = tfidf[:-1]
    sims = cosine_similarity(query_vec, doc_vecs).flatten()

    ranked = sorted(zip(sims, kb), key=lambda x: x[0], reverse=True)
    results = [(score, item) for score, item in ranked[:top_k] if score > 0.05]
    return results


def build_prompt(question, retrieved, extra_context):
    context_block = ""
    if retrieved:
        context_block = "\n\nRelevant past RFP answers (use these for tone, facts, and consistency):\n"
        for score, item in retrieved:
            context_block += f"\n- Q: {item['question']}\n  A: {item['answer']}\n"

    extra = f"\n\nAdditional context provided:\n{extra_context}" if extra_context else ""

    prompt = f"""You are helping draft a professional response to an RFP (Request for Proposal) question.

RFP Question:
{question}
{context_block}{extra}

Write a clear, confident, professional response. Match the tone and factual claims of past answers where relevant. Keep it concise (3-6 sentences) unless the question requires more detail. Do not invent specific numbers, certifications, or claims that are not supported by the context provided."""
    return prompt


def generate_response(client, question, retrieved, extra_context):
    prompt = build_prompt(question, retrieved, extra_context)
    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_demo_response(question, retrieved, extra_context):
    """
    Synthesizes a response from retrieved knowledge-base answers without
    calling any API. Lets the app run and demo fully offline, with no key
    and no cost, while still showing the retrieval-grounding behavior.
    """
    if retrieved:
        best_score, best_item = retrieved[0]
        answer = best_item["answer"]
        if len(retrieved) > 1:
            answer += " " + retrieved[1][1]["answer"]
        if extra_context:
            answer += f" This response has been tailored to reflect: {extra_context.strip()}"
        return answer

    if extra_context:
        return (
            "[Demo mode] No close match found in the knowledge base for this question. "
            "In live mode, Claude would draft a response grounded in your provided context: "
            f"\"{extra_context.strip()}\". Add more entries to the knowledge base to see "
            "retrieval-grounded answers here."
        )

    return (
        "[Demo mode] No close match found in the knowledge base for this question. "
        "Add a relevant past answer in the sidebar, or connect a live Anthropic API key "
        "to have Claude draft an original response."
    )


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "kb" not in st.session_state:
    st.session_state.kb = load_knowledge_base()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Setup")

    api_key_present = bool(get_api_key())

    demo_mode = st.toggle(
        "🎭 Demo Mode (no API key needed)",
        value=not api_key_present,
        help="Runs fully offline using retrieval over the knowledge base only — no API calls, no cost, no key required.",
    )

    if not demo_mode:
        if not api_key_present:
            st.warning("No API key found in secrets.")
            manual_key = st.text_input("Anthropic API key", type="password")
            if manual_key:
                st.session_state.manual_api_key = manual_key
                api_key_present = True
        else:
            st.success("API key loaded ✓")
    else:
        st.info("Demo mode is on — responses are synthesized from the knowledge base, not generated live by Claude.")

    st.divider()
    st.header("📚 Knowledge Base")
    st.caption(f"{len(st.session_state.kb)} past Q&A pairs loaded")

    with st.expander("➕ Add a past RFP answer"):
        new_q = st.text_area("Question", key="new_q")
        new_a = st.text_area("Answer", key="new_a")
        if st.button("Add to knowledge base"):
            if new_q and new_a:
                st.session_state.kb.append({"question": new_q, "answer": new_a})
                save_knowledge_base(st.session_state.kb)
                st.success("Added.")
                st.rerun()

    with st.expander("📄 Upload knowledge base (CSV)"):
        st.caption("CSV with columns: question, answer")
        kb_upload = st.file_uploader("Upload CSV", type=["csv"], key="kb_upload")
        if kb_upload is not None:
            df = pd.read_csv(kb_upload)
            if {"question", "answer"}.issubset(df.columns):
                new_items = df[["question", "answer"]].to_dict("records")
                st.session_state.kb.extend(new_items)
                save_knowledge_base(st.session_state.kb)
                st.success(f"Added {len(new_items)} entries.")
                st.rerun()
            else:
                st.error("CSV must have 'question' and 'answer' columns.")

    if st.session_state.kb:
        with st.expander("👀 View knowledge base"):
            for i, item in enumerate(st.session_state.kb):
                st.markdown(f"**Q{i+1}:** {item['question']}")
                st.markdown(f"**A{i+1}:** {item['answer']}")
                st.markdown("---")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
st.title("📄 RFP Automation Tool")
st.caption("AI-powered RFP response generator using Claude, grounded in your team's past answers.")

tab1, tab2 = st.tabs(["✏️ Single Question", "📋 Bulk Generate"])

# --- Single question mode ---
with tab1:
    st.subheader("Draft a single RFP response")
    question = st.text_area("Paste the RFP question", height=100)
    extra_context = st.text_area(
        "Additional context (optional)",
        placeholder="e.g. This customer cares about SOC 2 compliance and multi-region deployment.",
        height=80,
    )

    if st.button("Generate Response", type="primary", key="single_gen"):
        if not demo_mode and not api_key_present:
            st.error("Add your Anthropic API key in the sidebar, or turn on Demo Mode.")
        elif not question.strip():
            st.error("Paste a question first.")
        else:
            with st.spinner("Retrieving relevant past answers and drafting response..."):
                retrieved = retrieve_relevant_answers(question, st.session_state.kb)
                if demo_mode:
                    answer = generate_demo_response(question, retrieved, extra_context)
                else:
                    client = anthropic.Anthropic(api_key=get_api_key())
                    answer = generate_response(client, question, retrieved, extra_context)

            if retrieved:
                with st.expander(f"🔍 Used {len(retrieved)} past answer(s) as grounding"):
                    for score, item in retrieved:
                        st.markdown(f"**Match ({score:.2f}):** {item['question']}")

            st.subheader("Draft Response")
            st.write(answer)
            st.download_button(
                "Download as .txt",
                data=answer,
                file_name=f"rfp_response_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            )

# --- Bulk mode ---
with tab2:
    st.subheader("Generate responses for a full RFP")
    st.caption("Upload a CSV with a 'question' column (optional 'context' column).")
    bulk_upload = st.file_uploader("Upload RFP questions CSV", type=["csv"], key="bulk_upload")

    if bulk_upload is not None:
        bulk_df = pd.read_csv(bulk_upload)
        st.dataframe(bulk_df.head(10))

        if st.button("Generate All Responses", type="primary", key="bulk_gen"):
            if not demo_mode and not api_key_present:
                st.error("Add your Anthropic API key in the sidebar, or turn on Demo Mode.")
            elif "question" not in bulk_df.columns:
                st.error("CSV must have a 'question' column.")
            else:
                client = None if demo_mode else anthropic.Anthropic(api_key=get_api_key())
                results = []
                progress = st.progress(0, text="Generating responses...")

                for i, row in bulk_df.iterrows():
                    q = row["question"]
                    ctx = row.get("context", "") if "context" in bulk_df.columns else ""
                    retrieved = retrieve_relevant_answers(q, st.session_state.kb)
                    if demo_mode:
                        ans = generate_demo_response(q, retrieved, ctx)
                    else:
                        ans = generate_response(client, q, retrieved, ctx)
                    results.append({"question": q, "generated_answer": ans})
                    progress.progress((i + 1) / len(bulk_df), text=f"Generated {i+1}/{len(bulk_df)}")

                result_df = pd.DataFrame(results)
                st.success(f"Generated {len(result_df)} responses.")
                st.dataframe(result_df)

                csv_buffer = io.StringIO()
                result_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    "Download all responses as CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"rfp_responses_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                )

st.divider()
st.caption("Built with Streamlit + Claude · [Srabana Guha](https://www.linkedin.com/)")
