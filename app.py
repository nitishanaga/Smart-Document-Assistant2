import hashlib
import html
import json
import math
import os
import re
import csv
import io
import urllib.error
import urllib.request
import zipfile
import xml.etree.ElementTree as ElementTree

import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="Smart Document Assistant",
    page_icon=":material/auto_awesome:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink:#f5f1e8; --muted:#a7b4b8; --line:#33454b; --mint:#b7f3df; --teal:#63e6c2; --coral:#ff927d; --panel:#17252b; --paper:#f5f1e8; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
    h1, h2, h3 { font-family:'Space Grotesk',sans-serif; letter-spacing:0; }
    [data-testid="stAppViewContainer"] { background:radial-gradient(circle at 84% 2%,rgba(255,146,125,.18),transparent 24rem),radial-gradient(circle at 8% 78%,rgba(99,230,194,.08),transparent 22rem),#0d171b; }
    [data-testid="stHeader"] { background:rgba(13,23,27,.75); }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#142329 0%,#101b20 100%); border-right:1px solid #33454b; }
    [data-testid="stSidebar"] * { color:var(--ink); }
    .hero { padding:2.8rem 0 1.2rem; max-width:880px; }
    .eyebrow, .section-label { color:var(--teal); font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }
    .hero h1 { font-size:clamp(2.5rem,5vw,4.8rem); line-height:.98; margin:.35rem 0 1rem; max-width:760px; }
    .hero h1 { color:var(--paper); text-shadow:0 0 32px rgba(99,230,194,.1); }
    .hero p { color:var(--muted); font-size:1.08rem; max-width:620px; }
    .section-label { letter-spacing:.08em; margin-bottom:.35rem; }
    div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line); border-radius:18px; background:linear-gradient(145deg,rgba(28,45,51,.94),rgba(20,33,38,.94)); box-shadow:0 16px 40px rgba(0,0,0,.16); }
    div[data-testid="stForm"] { padding:1.25rem; }
    .stButton > button, .stFormSubmitButton > button { border-radius:11px; border:1px solid var(--teal); background:rgba(99,230,194,.08); color:var(--paper); font-weight:600; transition:transform .18s ease,box-shadow .18s ease,background .18s ease; }
    .stButton > button:hover, .stFormSubmitButton > button:hover { transform:translateY(-2px); background:rgba(99,230,194,.18); box-shadow:0 8px 22px rgba(99,230,194,.16); }
    [data-testid="stMetric"] { background:rgba(23,37,43,.85); border:1px solid var(--line); border-radius:15px; padding:.8rem 1rem; }
    [data-testid="stMetricValue"] { color:var(--mint); }
    [data-testid="stFileUploaderDropzone"] { border:1px dashed #477b70; background:rgba(99,230,194,.06); border-radius:14px; }
    [data-testid="stFileUploaderDropzone"] small, [data-testid="stFileUploaderDropzone"] span { color:var(--muted); }
    .source-chip { display:inline-block; background:rgba(99,230,194,.14); border:1px solid rgba(99,230,194,.35); border-radius:999px; color:var(--mint); font-size:.82rem; margin:.15rem .3rem .15rem 0; padding:.35rem .7rem; }
    [data-baseweb="input"], [data-baseweb="select"] { background:#0f1c21; border-color:#40545a; }
    [data-baseweb="input"] input, [data-baseweb="select"] * { color:var(--paper); }
    [data-testid="stTabs"] button[aria-selected="true"] { color:var(--teal); }
    .score-card { background:linear-gradient(135deg,rgba(99,230,194,.12),rgba(255,146,125,.08)); border:1px solid rgba(99,230,194,.28); border-radius:16px; padding:1rem 1.1rem; }
    .score-value { color:var(--mint); font-family:'Space Grotesk',sans-serif; font-size:1.8rem; font-weight:700; }
    .score-label { color:var(--muted); font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; }
    .memory-note { color:var(--muted); font-size:.86rem; padding:.65rem .8rem; border-left:2px solid var(--coral); background:rgba(255,146,125,.06); }
    .chat-scroll { border:1px solid var(--line); border-radius:18px; padding:1rem; background:rgba(10,20,24,.48); }
    [data-testid="stChatMessage"] { background:transparent; padding:.65rem .35rem; }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] { color:var(--paper); }
    .chat-question { color:var(--paper); font-weight:600; }
    .chat-meta { color:var(--muted); font-size:.78rem; margin-bottom:.35rem; }
    .mindmap-board { padding:1.25rem; border:1px solid rgba(99,230,194,.28); border-radius:18px; background:linear-gradient(145deg,rgba(23,45,48,.9),rgba(13,28,32,.92)); }
    .mindmap-root { display:flex; align-items:center; justify-content:center; min-height:4rem; margin:0 auto 1.1rem; max-width:460px; padding:1rem 1.25rem; border:1px solid var(--teal); border-radius:14px; background:rgba(99,230,194,.16); color:var(--mint); font-family:'Space Grotesk',sans-serif; font-weight:700; text-align:center; box-shadow:0 0 0 5px rgba(99,230,194,.05); }
    .mindmap-connector { width:2px; height:1.4rem; margin:0 auto; background:rgba(99,230,194,.48); }
    .mindmap-branches { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:1rem; position:relative; }
    .mindmap-branches:before { content:''; position:absolute; top:-.7rem; left:8%; right:8%; height:1px; background:rgba(99,230,194,.4); }
    .mindmap-branch { position:relative; padding:1rem; border:1px solid rgba(255,146,125,.38); border-radius:13px; background:rgba(255,146,125,.07); }
    .mindmap-branch:before { content:''; position:absolute; top:-.72rem; left:50%; width:1px; height:.72rem; background:rgba(99,230,194,.4); }
    .mindmap-heading { color:#ffd0c5; font-family:'Space Grotesk',sans-serif; font-weight:700; margin-bottom:.65rem; }
    .mindmap-detail { color:var(--muted); font-size:.88rem; padding:.35rem 0; border-top:1px solid rgba(167,180,184,.12); }
    .flashcard-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:1rem; }
    .flashcard { min-height:190px; padding:1.1rem; border:1px solid rgba(99,230,194,.28); border-radius:15px; background:linear-gradient(145deg,rgba(28,51,55,.96),rgba(17,32,37,.96)); box-shadow:0 12px 28px rgba(0,0,0,.14); }
    .flashcard-number { color:var(--teal); font-size:.75rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
    .flashcard-question { color:var(--paper); font-family:'Space Grotesk',sans-serif; font-size:1.05rem; font-weight:700; margin:.55rem 0 1rem; }
    .flashcard-answer { padding-top:.75rem; border-top:1px solid rgba(99,230,194,.2); color:var(--muted); line-height:1.5; }
    .flashcard-source { color:var(--teal); font-size:.75rem; margin-top:1rem; }
    .history-question { color:var(--paper); font-weight:600; }
    .shortcut-row { color:var(--muted); font-size:.82rem; padding:.55rem .75rem; border:1px solid rgba(99,230,194,.16); border-radius:10px; background:rgba(99,230,194,.04); }
    kbd { color:var(--paper); background:#0f1c21; border:1px solid #40545a; border-bottom-width:2px; border-radius:5px; padding:.1rem .35rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.session_state.setdefault("chunks", [])
st.session_state.setdefault("index", None)
st.session_state.setdefault("last_answer", None)
st.session_state.setdefault("conversation", [])
st.session_state.setdefault("question_input", "")
st.session_state.setdefault("suggested_applied", None)
st.session_state.setdefault("summaries", {})
st.session_state.setdefault("mindmaps", {})
st.session_state.setdefault("flashcards", {})
st.session_state.setdefault("library_fingerprint", None)
st.session_state.setdefault("analysis", None)
st.session_state.setdefault("ai_client", None)
st.session_state.setdefault("ai_model", None)
st.session_state.setdefault("gemini_unavailable", False)


def render_source_chips(sources):
    chips = "".join(f'<span class="source-chip">{source}</span>' for source in sources)
    st.markdown(chips, unsafe_allow_html=True)


def confidence_details(top_score, scores):
    """Translate normalized cosine similarity into simple user-facing signals."""
    confidence = int(max(0, min(100, round(((top_score - 0.30) / 0.70) * 100))))
    evidence_score = int(max(0, min(100, round(sum(scores) / len(scores) * 100)))) if scores else 0
    if confidence >= 75:
        label = "Strong match"
    elif confidence >= 45:
        label = "Useful match"
    else:
        label = "Weak match"
    return confidence, evidence_score, label


def meaningful_terms(text):
    stop_words = {
        "a", "an", "and", "are", "do", "does", "find", "for", "how", "in",
        "is", "it", "me", "of", "on", "the", "this", "to", "what", "which",
        "who", "why", "with", "you", "your",
    }
    irregular_forms = {
        "caused": "cause",
        "causes": "cause",
        "offered": "offer",
        "offers": "offer",
        "travellers": "traveler",
    }
    terms = set()
    for term in re.findall(r"[a-z0-9]+", text.lower()):
        if len(term) <= 2 or term in stop_words:
            continue
        term = irregular_forms.get(term, term)
        if term.endswith("ies") and len(term) > 4:
            term = term[:-3] + "y"
        elif term.endswith("ing") and len(term) > 5:
            term = term[:-3]
        elif term.endswith("ed") and len(term) > 5:
            term = term[:-2]
        elif term.endswith("s") and not term.endswith("ss") and len(term) > 3:
            term = term[:-1]
        terms.add(term)
    return terms


def hybrid_retrieval(question, semantic_query, scores, positions):
    """Rank passages with both semantic similarity and exact term overlap."""
    query_terms = meaningful_terms(f"{question} {semantic_query}")
    candidates = []
    for score, position in zip(scores, positions):
        if position >= 0:
            chunk_terms = meaningful_terms(st.session_state["chunks"][position]["text"])
            overlap = (
                len(query_terms & chunk_terms) / len(query_terms)
                if query_terms else 0.0
            )
            combined_score = (float(score) * 0.7) + (overlap * 0.3)
            candidates.append((combined_score, position))

    for position, chunk in enumerate(st.session_state["chunks"]):
        chunk_terms = meaningful_terms(chunk["text"])
        if not query_terms or not chunk_terms:
            continue
        overlap = len(query_terms & chunk_terms) / len(query_terms)
        if query_terms and query_terms.issubset(chunk_terms):
            overlap = min(1.0, overlap + 0.15)
        if overlap > 0:
            candidates.append((overlap * 0.3, position))

    best_by_position = {}
    for score, position in candidates:
        best_by_position[position] = max(score, best_by_position.get(position, -1.0))
    ranked = sorted(best_by_position.items(), key=lambda item: item[1], reverse=True)
    document_limit = max(1, len(get_document_names()))
    selected = []
    document_counts = {}
    selected_positions = set()

    # Keep at least one strongest passage from every uploaded document so
    # cross-document questions have evidence from each relevant source.
    for position, score in ranked:
        chunk = st.session_state["chunks"][position]
        document = document_name_from_source(chunk["source"])
        if document in document_counts:
            continue
        selected.append((position, score))
        selected_positions.add(position)
        document_counts[document] = 1

    for position, score in ranked:
        if position in selected_positions:
            continue
        chunk = st.session_state["chunks"][position]
        document = document_name_from_source(chunk["source"])
        if document_counts.get(document, 0) >= 3:
            continue
        selected.append((position, score))
        selected_positions.add(position)
        document_counts[document] = document_counts.get(document, 0) + 1
        if len(selected) >= max(6, document_limit * 2):
            break
    return [
        {"chunk": st.session_state["chunks"][position], "score": float(score)}
        for position, score in selected
    ]


def expand_retrieved_context(retrieved, max_items=12):
    """Add nearby chunks so answers can use context split across boundaries."""
    chunks = st.session_state["chunks"]
    selected_positions = {
        index
        for index, chunk in enumerate(chunks)
        if any(chunk is item["chunk"] for item in retrieved)
    }
    for item in list(retrieved):
        position = chunks.index(item["chunk"])
        for neighbor in (position - 1, position + 1):
            if 0 <= neighbor < len(chunks):
                same_document = document_name_from_source(chunks[neighbor]["source"]) == document_name_from_source(item["chunk"]["source"])
                if same_document:
                    selected_positions.add(neighbor)
    expanded = list(retrieved)
    for position in sorted(selected_positions):
        if not any(item["chunk"] is chunks[position] for item in expanded):
            expanded.append({"chunk": chunks[position], "score": 0.21})
    return expanded[:max_items]


def recent_memory():
    """Keep follow-ups focused without making the prompt grow forever."""
    return "\n".join(
        f"Earlier user question: {item.get('question', '')}\nEarlier answer: {item.get('answer', '')}"
        for item in st.session_state["conversation"][-6:]
    )


def contextual_follow_up_fallback(question, answer):
    """Keep fallback suggestions tied to the latest exchange."""
    topic = question.strip().rstrip("?")
    return [
        f"What evidence in the document supports the answer about {topic.lower()}?",
        f"What related detail does the document mention about {topic.lower()}?",
        "Can you explain the previous answer in simpler terms?",
    ]


def fresh_follow_up_questions(questions, question, previous_questions=()):
    """Keep only new, usable follow-ups for the latest answer."""
    previous = {item.strip().casefold() for item in previous_questions}
    current = question.strip().casefold()
    fresh = []
    for item in questions:
        cleaned = str(item).strip()
        normalized = cleaned.casefold()
        if cleaned and normalized != current and normalized not in previous and normalized not in {
            value.casefold() for value in fresh
        }:
            fresh.append(cleaned)
    return fresh[:3]


def generate_query_repair_suggestions(question):
    """Generate clickable topics from document vocabulary, never document answers."""
    excerpts_by_document = {}
    for chunk in st.session_state["chunks"]:
        document = document_name_from_source(chunk["source"])
        excerpts_by_document.setdefault(document, [])
        if len(excerpts_by_document[document]) < 2:
            excerpts_by_document[document].append(
                f"Source: {chunk['source']}\nText: {chunk['text'][:700]}"
            )
    excerpts = "\n\n".join(
        "\n\n".join(document_excerpts)
        for document_excerpts in excerpts_by_document.values()
    )
    try:
        content = groq_chat(
            [
                {
                    "role": "system",
                    "content": "Return JSON only as {\"suggestions\": [\"...\", \"...\", \"...\"]}. Create exactly three short topic prompts, 3 to 10 words each, using only named people, places, events, or subjects explicitly present in the supplied document excerpts. Do not answer the user's question, add facts, or invent topics.",
                },
                {
                    "role": "user",
                    "content": f"User query: {question}\n\nDocument excerpts:\n{excerpts}",
                },
            ],
            json_mode=True,
        )
        suggestions = json.loads(content).get("suggestions", [])
        if isinstance(suggestions, list):
            return fresh_follow_up_questions(suggestions, question)[:3]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, RuntimeError):
        pass

    fallback = []
    for chunk in st.session_state["chunks"][:3]:
        words = re.findall(r"[A-Za-z][A-Za-z'-]+", chunk["text"])
        topic = " ".join(words[:6]).strip()
        if topic and topic.casefold() not in {item.casefold() for item in fallback}:
            fallback.append(f"Tell me about {topic}")
    return fallback[:3]


def get_document_names():
    return sorted(set(document_name_from_source(chunk["source"]) for chunk in st.session_state["chunks"]))


def document_name_from_source(source):
    """Remove page, slide, and sheet suffixes while preserving the filename."""
    return re.split(r" - (?:page|slide|sheet) ", source, maxsplit=1)[0]


def fallback_suggestions():
    names = get_document_names()
    if not names:
        return ["What are the key takeaways?", "Summarize the risks", "Find important dates"]
    if len(names) > 1:
        return [
            f"Give me a quick overview of {names[0]}",
            f"What are the key decisions in {names[0]}?",
            f"Compare {names[0]} with {names[1]}",
        ]
    return [
        f"Give me a quick overview of {names[0]}",
        f"What are the key decisions in {names[0]}?",
        f"Find important dates in {names[0]}",
    ]


def make_library_fingerprint(uploaded_files):
    digest = hashlib.sha256()
    for uploaded_file in uploaded_files or []:
        digest.update(uploaded_file.name.encode("utf-8"))
        digest.update(uploaded_file.getvalue())
    return digest.hexdigest() if uploaded_files else None


def get_ai_client():
    """Load the Google AI Studio key without importing an SDK."""
    api_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GOOGLE_AI_STUDIO_KEY"]
        except (KeyError, FileNotFoundError):
            api_key = None
    if not api_key:
        raise RuntimeError(
            "GOOGLE_AI_STUDIO_KEY is not configured. Add it to "
            ".streamlit/secrets.toml or set the environment variable, then restart Streamlit."
        )
    if st.session_state["ai_client"] != api_key:
        st.session_state["ai_client"] = api_key
    return st.session_state["ai_client"]


def gemini_request(model, payload):
    """Call Google AI Studio's Gemini REST API using the standard library."""
    api_key = get_ai_client()
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
    }
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 429:
            raise RuntimeError("Gemini is rate-limiting requests (HTTP 429). Wait a moment and try again.") from error
        raise RuntimeError(
            f"Google AI Studio request failed with HTTP {error.code}. "
            "Check GOOGLE_AI_STUDIO_KEY and GEMINI_MODEL."
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError("Could not connect to Google AI Studio. Check the network connection.") from error


def get_ai_model(force_refresh=False):
    """Choose the configured Gemini model."""
    if force_refresh:
        st.session_state["ai_model"] = None
    if st.session_state["ai_model"]:
        return st.session_state["ai_model"]
    configured_model = os.getenv("GEMINI_MODEL")
    if not configured_model:
        try:
            configured_model = st.secrets.get("GEMINI_MODEL")
        except (KeyError, FileNotFoundError):
            configured_model = None
    st.session_state["ai_model"] = configured_model or "gemini-3.5-flash-lite"
    return st.session_state["ai_model"]


def get_groq_key():
    """Load an optional Groq fallback key without requiring it."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
        except (KeyError, FileNotFoundError):
            api_key = None
    return api_key


def groq_fallback_request(messages, json_mode=False):
    """Call Groq only when Gemini is unavailable and a fallback key exists."""
    api_key = get_groq_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured for fallback use.")
    model = os.getenv("GROQ_MODEL")
    if not model:
        try:
            model = st.secrets.get("GROQ_MODEL")
        except (KeyError, FileNotFoundError):
            model = None
    payload = {"model": model or "openai/gpt-oss-20b", "messages": messages}
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "smart-document-assistant/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Groq fallback failed with HTTP {error.code}.") from error
    except (urllib.error.URLError, KeyError, IndexError, TypeError, ValueError) as error:
        raise RuntimeError("Groq fallback could not return an answer.") from error


def groq_chat(messages, json_mode=False):
    """Use Gemini first, then Groq, while preserving existing call sites."""
    system_parts = [item["content"] for item in messages if item.get("role") == "system"]
    contents = [
        {"role": "user", "parts": [{"text": item["content"]}]}
        for item in messages
        if item.get("role") != "system"
    ]
    payload = {"contents": contents}
    if system_parts:
        payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}
    if json_mode:
        payload["generationConfig"] = {"responseMimeType": "application/json"}
    gemini_error = None
    if not st.session_state["gemini_unavailable"]:
        try:
            response = gemini_request(get_ai_model(), payload)
            return response["candidates"][0]["content"]["parts"][0]["text"]
        except (RuntimeError, KeyError, IndexError, TypeError) as error:
            gemini_error = error
            if "rate-limiting" in str(error) or "quota" in str(error).lower():
                st.session_state["gemini_unavailable"] = True
    if gemini_error is None:
        gemini_error = RuntimeError("Gemini is unavailable for this session.")
    try:
        return groq_fallback_request(messages, json_mode=json_mode)
    except RuntimeError as groq_error:
        raise RuntimeError(
            f"Gemini unavailable ({gemini_error}); Groq fallback unavailable ({groq_error})."
        ) from gemini_error


def generate_document_suggestions():
    """Ask the model for questions grounded across the indexed documents."""
    document_excerpts = []
    seen_documents = set()
    for chunk in st.session_state["chunks"]:
        document = document_name_from_source(chunk["source"])
        if document in seen_documents:
            continue
        seen_documents.add(document)
        document_excerpts.append(
            "\n\n".join(
                f"{item['source']}: {item['text'][:1000]}"
                for item in st.session_state["chunks"]
                if document_name_from_source(item["source"]) == document
            )
        )
    excerpts = "\n\n".join(
        document_excerpt[:2200]
        for document_excerpt in document_excerpts
    )
    try:
        content = groq_chat(
            [
                {
                    "role": "system",
                    "content": "Create exactly three useful questions answerable from the supplied document excerpts. Return JSON as {\"questions\": [\"...\", \"...\", \"...\"]}. Do not invent topics.",
                },
                {"role": "user", "content": excerpts},
            ],
            json_mode=True,
        )
        questions = json.loads(content)["questions"]
        if isinstance(questions, list) and len(questions) >= 3:
            return [str(question) for question in questions[:3]]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError, RuntimeError):
        pass
    return fallback_suggestions()


def analyze_question(question):
    """Use the user's wording locally to avoid an extra API request per question."""
    return question.strip()


def build_library(uploaded_files):
    all_chunks = []
    for uploaded_file in uploaded_files or []:
        for page in read_uploaded_file(uploaded_file):
            all_chunks.extend(split_text(page["text"], page["source"]))
    if not all_chunks:
        return None
    embeddings = make_embeddings([chunk["text"] for chunk in all_chunks])
    return all_chunks, embeddings


def create_summary(document_name):
    """Generate one cached summary so switching back to the tab is instant."""
    document_text = "\n".join(
        chunk["text"]
        for chunk in st.session_state["chunks"]
        if chunk["source"].startswith(document_name)
    )
    return groq_chat(
        [
            {"role": "system", "content": "You create short, clear summaries of documents."},
            {"role": "user", "content": f"""
Summarize this document in simple bullet points.
Only use the text provided. Do not add facts.

Document:
{document_text}
"""},
        ],
    )


def document_text(document_name):
    return "\n".join(
        chunk["text"]
        for chunk in st.session_state["chunks"]
        if chunk["source"].startswith(document_name)
    )


def create_mindmap(document_name):
    """Create a document-grounded hierarchy for visual scanning."""
    content = groq_chat(
        [
            {
                "role": "system",
                "content": "Build a document-grounded mind map. Return JSON only as {\"title\": \"...\", \"branches\": [{\"label\": \"...\", \"details\": [\"...\"]}]}. Use only the supplied text. Create 4 to 8 main branches with concise details. Do not invent facts.",
            },
            {"role": "user", "content": f"Document: {document_name}\n\nText:\n{document_text(document_name)}"},
        ],
        json_mode=True,
    )
    cleaned_content = content.strip()
    if cleaned_content.startswith("```"):
        cleaned_content = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned_content, flags=re.IGNORECASE)
    parsed = json.loads(cleaned_content)
    branches = parsed.get("branches", [])
    if not isinstance(branches, list):
        raise ValueError("Mind map response did not contain branches.")
    normalized_branches = []
    for branch in branches:
        if not isinstance(branch, dict) or not branch.get("label"):
            continue
        details = branch.get("details", [])
        if isinstance(details, str):
            details = [details]
        normalized_branches.append(
            {
                "label": str(branch["label"]),
                "details": [
                    str(detail.get("text", detail)) if isinstance(detail, dict) else str(detail)
                    for detail in details
                    if str(detail.get("text", detail) if isinstance(detail, dict) else detail).strip()
                ],
            }
        )
    return {
        "title": str(parsed.get("title", document_name)),
        "branches": normalized_branches,
    }


def local_mindmap(document_name):
    """Build a useful fallback map from the selected document's text."""
    chunks = [
        chunk["text"].strip()
        for chunk in st.session_state["chunks"]
        if document_name_from_source(chunk["source"]) == document_name
    ]
    text = " ".join(chunks)
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", text) if item.strip()]
    branches = [
        {"label": f"Section {number}", "details": [sentence[:240]]}
        for number, sentence in enumerate(sentences[:8], start=1)
    ]
    return {"title": document_name, "branches": branches}


def create_flashcards(document_name):
    """Create study cards whose answers are supported by the document."""
    content = groq_chat(
        [
            {
                "role": "system",
                "content": "Create exactly 8 study flashcards from the supplied document. Return JSON only as {\"cards\": [{\"question\": \"...\", \"answer\": \"...\", \"source\": \"...\"}]}. Use only the supplied text, keep answers concise, and never invent facts.",
            },
            {"role": "user", "content": f"Document: {document_name}\n\nText:\n{document_text(document_name)}"},
        ],
        json_mode=True,
    )
    parsed = json.loads(content)
    cards = parsed.get("cards", [])
    if not isinstance(cards, list):
        raise ValueError("Flashcard response did not contain cards.")
    return [
        {
            "question": str(card.get("question", "")),
            "answer": str(card.get("answer", "")),
            "source": str(card.get("source", "")),
        }
        for card in cards
        if isinstance(card, dict) and card.get("question") and card.get("answer")
    ][:8]


def read_uploaded_file(uploaded_file):
    """Read common document formats and keep page, slide, or sheet metadata."""
    pages = []
    name = uploaded_file.name
    extension = name.lower().rsplit(".", 1)[-1] if "." in name else ""

    if extension == "pdf":
        reader = PdfReader(uploaded_file)

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({
                    "text": text,
                    "source": f"{name} - page {page_number}"
                })

    elif extension == "docx":
        from docx import Document

        document = Document(io.BytesIO(uploaded_file.getvalue()))
        text = "\n\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
        if text.strip():
            pages.append({"text": text, "source": name})

    elif extension == "pptx":
        presentation_xml = "http://schemas.openxmlformats.org/presentationml/2006/main"
        text_namespace = "http://schemas.openxmlformats.org/drawingml/2006/main"
        with zipfile.ZipFile(io.BytesIO(uploaded_file.getvalue())) as archive:
            slide_names = sorted(
                name for name in archive.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            )
            for slide_number, slide_name in enumerate(slide_names, start=1):
                root = ElementTree.fromstring(archive.read(slide_name))
                text = "\n".join(
                    node.text or ""
                    for node in root.iter(f"{{{text_namespace}}}t")
                )
                text = text.strip()
                if text:
                    pages.append({"text": text, "source": f"{name} - slide {slide_number}"})

    elif extension in {"xlsx", "xlsm"}:
        from openpyxl import load_workbook

        workbook = load_workbook(io.BytesIO(uploaded_file.getvalue()), read_only=True, data_only=True)
        for sheet in workbook.worksheets:
            rows = [
                " | ".join("" if value is None else str(value) for value in row)
                for row in sheet.iter_rows(values_only=True)
            ]
            text = "\n".join(row for row in rows if row.strip(" |"))
            if text.strip():
                pages.append({"text": text, "source": f"{name} - sheet {sheet.title}"})

    elif extension == "xls":
        import xlrd

        workbook = xlrd.open_workbook(file_contents=uploaded_file.getvalue(), on_demand=True)
        for sheet in workbook.sheets():
            rows = [
                " | ".join(str(value) for value in sheet.row_values(row_number))
                for row_number in range(sheet.nrows)
            ]
            text = "\n".join(row for row in rows if row.strip(" |"))
            if text.strip():
                pages.append({"text": text, "source": f"{name} - sheet {sheet.name}"})

    elif extension in {"csv", "tsv"}:
        delimiter = "\t" if extension == "tsv" else ","
        rows = csv.reader(io.StringIO(uploaded_file.getvalue().decode("utf-8", errors="ignore")), delimiter=delimiter)
        text = "\n".join(" | ".join(row) for row in rows)
        if text.strip():
            pages.append({"text": text, "source": name})

    elif extension in {"html", "htm"}:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(uploaded_file.getvalue(), "html.parser")
        text = soup.get_text("\n", strip=True)
        if text.strip():
            pages.append({"text": text, "source": name})

    elif extension == "json":
        try:
            text = json.dumps(json.loads(uploaded_file.getvalue().decode("utf-8", errors="ignore")), indent=2)
        except json.JSONDecodeError:
            text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        if text.strip():
            pages.append({"text": text, "source": name})

    elif extension in {"txt", "md", "markdown", "log", "rtf"}:
        text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        if text.strip():
            pages.append({
                "text": text,
                "source": name
            })

    else:
        text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        if text.strip():
            pages.append({"text": text, "source": name})

    return pages


def split_text(text, source, chunk_size=800, overlap=150):
    """Break long text into smaller overlapping pieces."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        paragraph_start = text[:start].count("\n\n") + 1
        paragraph_end = text[:min(end, len(text))].count("\n\n") + 1
        chunks.append({
            "text": text[start:end],
            "source": source,
            "paragraph_start": paragraph_start,
            "paragraph_end": paragraph_end,
        })
        start += chunk_size - overlap

    return chunks


def make_embeddings(texts):
    """Create deterministic local retrieval vectors without a model server."""
    dimensions = 384
    embeddings = []
    for text in texts:
        vector = [0.0] * dimensions
        for term in meaningful_terms(text):
            digest = hashlib.sha256(term.encode("utf-8")).digest()
            position = int.from_bytes(digest[:4], "little") % dimensions
            vector[position] += 1.0
        magnitude = math.sqrt(sum(value * value for value in vector))
        embeddings.append(
            [value / magnitude for value in vector] if magnitude else vector
        )
    return embeddings


def ranked_embedding_matches(query_embedding, embeddings, limit):
    """Return the highest cosine-similarity document vectors."""
    ranked = []
    for position, embedding in enumerate(embeddings):
        score = sum(left * right for left, right in zip(query_embedding, embedding))
        ranked.append((score, position))
    ranked.sort(reverse=True)
    selected = ranked[:limit]
    return [score for score, _ in selected], [position for _, position in selected]


def parse_answer_response(content, retrieved):
    """Normalize the model's grounded JSON response for the result panels."""
    try:
        parsed = json.loads(content)
        cited_ids = parsed.get("cited_source_ids", [])
        if not isinstance(cited_ids, list):
            cited_ids = []
        cited_ids = [int(item) for item in cited_ids if str(item).isdigit()]
        cited_ids = [item for item in cited_ids if 1 <= item <= len(retrieved)]
        answer = str(parsed.get("answer", "")).strip()
        citation_text = parsed.get(
            "citation",
            parsed.get("citations", parsed.get("source", parsed.get("source_id", ""))),
        )
        if not cited_ids and citation_text:
            if isinstance(citation_text, list):
                cited_ids = [
                    int(item.get("source_id", item.get("id")))
                    for item in citation_text
                    if isinstance(item, dict) and str(item.get("source_id", item.get("id", ""))).isdigit()
                ]
                cited_ids.extend(int(item) for item in citation_text if str(item).isdigit())
            else:
                cited_ids = [
                    int(marker)
                    for marker in re.findall(r"\[(\d+)\]", str(citation_text))
                ]
            cited_ids = [item for item in cited_ids if 1 <= item <= len(retrieved)]
        if cited_ids and not re.search(r"\[\d+\]", answer):
            answer = f"{answer} [{cited_ids[0]}]"
        cited_markers = {
            int(marker)
            for marker in re.findall(r"\[(\d+)\]", answer)
        }
        cited_ids = [item for item in cited_ids if item in cited_markers]
        no_answer = not answer or answer.lower().startswith(
            "i could not find this information in the uploaded documents"
        )
        has_citations = bool(cited_ids)
        if no_answer or not cited_ids:
            cited_ids = []
        confidence_score = 0 if no_answer or not has_citations else max(0, min(100, int(parsed.get("confidence_score", 0))))
        evidence_score = 0 if no_answer or not has_citations else max(0, min(100, int(parsed.get("evidence_score", 0))))
        follow_up_questions = parsed.get("follow_up_questions", [])
        if not isinstance(follow_up_questions, list):
            follow_up_questions = []
        return {
            "answer": answer,
            "cited_source_ids": sorted(set(cited_ids)),
            "confidence_score": confidence_score,
            "evidence_score": evidence_score,
            "confidence_reason": str(parsed.get("confidence_reason", "")).strip(),
            "evidence_summary": str(parsed.get("evidence_summary", "")).strip(),
            "follow_up_questions": [str(item).strip() for item in follow_up_questions[:3] if str(item).strip()],
        }
    except (TypeError, ValueError, json.JSONDecodeError):
        return {
            "answer": content.strip(),
            "cited_source_ids": [],
            "confidence_score": 0,
            "evidence_score": 0,
            "confidence_reason": "The answer was returned as plain text; the top matching excerpts are shown for verification.",
            "evidence_summary": "Evidence is based on the retrieved excerpts shown below.",
            "follow_up_questions": [],
        }


def local_extractive_answer(question, retrieved):
    """Answer from the strongest retrieved sentences when Groq is unavailable."""
    query_terms = meaningful_terms(question)
    candidates = []
    for source_id, item in enumerate(retrieved, start=1):
        sentences = re.split(r"(?<=[.!?])\s+|\n+", item["chunk"]["text"].strip())
        for sentence in sentences:
            cleaned = sentence.strip()
            if not cleaned:
                continue
            sentence_terms = meaningful_terms(cleaned)
            overlap = (
                len(query_terms & sentence_terms) / len(query_terms)
                if query_terms else 0.0
            )
            candidates.append((overlap, item["score"], source_id, cleaned))
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    useful = [item for item in candidates if item[0] > 0]
    if not useful:
        return None
    selected = useful[:2]
    answer = " ".join(f"{item[3]} [{item[2]}]" for item in selected)
    cited_ids = sorted({item[2] for item in selected})
    evidence_score = int(max(25, min(100, round(selected[0][0] * 100))))
    return {
        "answer": answer,
        "cited_source_ids": cited_ids,
        "confidence_score": evidence_score,
        "evidence_score": evidence_score,
        "confidence_reason": "Answer extracted directly from matching document sentences.",
        "evidence_summary": "The answer is based on the retrieved document text.",
        "follow_up_questions": [],
    }


def render_answer_details(result):
    """Render evidence details for one answer in the chat transcript."""
    score_col, evidence_col = st.columns(2)
    with score_col:
        st.markdown(
            f'<div class="score-card"><div class="score-label">Answer confidence</div><div class="score-value">{result["confidence"]}%</div><div>{result["confidence_label"]}</div><div>{result.get("confidence_reason", "")}</div></div>',
            unsafe_allow_html=True,
        )
    with evidence_col:
        st.markdown(
            f'<div class="score-card"><div class="score-label">Evidence strength</div><div class="score-value">{result["evidence_score"]}%</div><div>{result.get("evidence_summary", "")}</div></div>',
            unsafe_allow_html=True,
        )
    with st.expander(":material/bug_report: Debug retrieved text"):
        st.caption("Retrieved excerpts are numbered so you can verify the citations in the answer.")
        cited_source_ids = set(result.get("cited_source_ids", []))
        for number, item in enumerate(result.get("retrieved", []), start=1):
            chunk = item["chunk"]
            usage = "Used in answer" if number in cited_source_ids else "Retrieved but not cited"
            st.markdown(
                f"**[{number}] {chunk['source']}** · paragraphs {chunk.get('paragraph_start', 1)}-{chunk.get('paragraph_end', 1)} · {usage} · similarity: `{item['score']:.4f}`"
            )
            st.write(chunk["text"])

    if result.get("answer") and result.get("cited_matches"):
        with st.expander(":material/source: View sources used", expanded=True):
            shown_sources = []
            cited_matches = result["cited_matches"]
            for item in cited_matches:
                if item["source"] not in shown_sources:
                    shown_sources.append(item["source"])
            render_source_chips(shown_sources)
            st.caption("The answer citations map to these document excerpts. Page, slide, or sheet labels are shown when available.")
            for source_id, item in zip(result.get("cited_source_ids", []), cited_matches):
                st.markdown(
                    f"**[{source_id}] {item['source']}** · paragraphs {item.get('paragraph_start', 1)}-{item.get('paragraph_end', 1)}"
                )
                st.write(item["text"])

    if result.get("recovery_suggestions"):
        st.warning(
            "We couldn't find an answer for that query. Try asking about one of these document topics:",
            icon=":material/search_check:",
        )
        st.caption("The clickable topic suggestions are available in the question box below.")


def render_conversation():
    """Render the saved transcript so it remains visible during new requests."""
    if not st.session_state["conversation"]:
        return
    st.markdown("### Conversation")
    with st.container(height="content", border=True):
        for result in st.session_state["conversation"]:
            with st.chat_message("user"):
                st.markdown('<div class="chat-meta">You</div>', unsafe_allow_html=True)
                st.markdown(result["question"])
            with st.chat_message("assistant"):
                st.markdown('<div class="chat-meta">Document assistant</div>', unsafe_allow_html=True)
                if result.get("answer"):
                    st.markdown(result["answer"])
                else:
                    st.info("I could not find this information in the uploaded documents.")
                if result.get("answer_source"):
                    st.caption(f"Answer source: {result['answer_source']}")
                if "confidence" in result:
                    render_answer_details(result)
                else:
                    st.caption("Evidence details are available for new answers.")
with st.sidebar:
    st.markdown("## :material/folder_open: Your library")
    st.caption("Upload a file and your private analysis starts automatically.")
    uploaded_files = st.file_uploader(
        "Add document files",
        type=None,
        accept_multiple_files=True,
        help="Supports PDF, Word, PowerPoint, Excel, CSV, JSON, HTML, Markdown, text files, and other UTF-8 documents.",
    )

    current_fingerprint = make_library_fingerprint(uploaded_files)
    if current_fingerprint != st.session_state["library_fingerprint"]:
        st.session_state["library_fingerprint"] = current_fingerprint
        st.session_state["chunks"] = []
        st.session_state["index"] = None
        st.session_state["last_answer"] = None
        st.session_state["conversation"] = []
        st.session_state["summaries"] = {}
        st.session_state["mindmaps"] = {}
        st.session_state["flashcards"] = {}
        st.session_state["analysis"] = None
        st.session_state["suggested_question"] = None
        st.session_state["suggested_applied"] = None
        if uploaded_files:
            with st.status("Analyzing your document...", expanded=True) as status:
                st.write("Extracting readable text")
                library = build_library(uploaded_files)
                if library is None:
                    status.update(label="No readable text found", state="error")
                    st.error("Try a text-based PDF or a UTF-8 TXT file.")
                else:
                    st.session_state["chunks"], st.session_state["index"] = library
                    st.write("Creating local document suggestions")
                    st.session_state["analysis"] = fallback_suggestions()
                    status.update(label="Document ready", state="complete", expanded=False)
                    st.toast("Your document is ready to explore", icon=":material/check:")

    if st.session_state["chunks"]:
        document_names = get_document_names()
        st.markdown("### Current index")
        st.metric("Documents", len(document_names))
        st.metric("Searchable pieces", len(st.session_state["chunks"]))
        if st.button(":material/delete: Clear library", width="stretch"):
            st.session_state["chunks"] = []
            st.session_state["index"] = None
            st.session_state["library_fingerprint"] = None
            st.session_state["last_answer"] = None
            st.session_state["conversation"] = []
            st.rerun()

    if st.session_state["conversation"]:
        st.markdown("### Follow-up memory")
        st.caption(f"Remembering the last {len(st.session_state['conversation'])} exchange(s)")
        for item in st.session_state["conversation"][-3:]:
            st.markdown(
                f'<div class="history-question">{item["question"]}</div>',
                unsafe_allow_html=True,
            )
        if st.button(":material/history: Clear conversation", width="stretch"):
            st.session_state["conversation"] = []
            st.session_state["last_answer"] = None
            st.rerun()

    with st.expander(":material/keyboard: Shortcuts"):
        st.markdown(
            '<div class="shortcut-row"><kbd>Enter</kbd> send question &nbsp; <kbd>Tab</kbd> move focus &nbsp; <kbd>Esc</kbd> close panels</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Local intelligence workspace</div>
        <h1>Talk to the documents you already have.</h1>
        <p>Drop in a few files, build your private index, and get grounded answers with traceable sources.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state["chunks"]:
    st.success("Your library is ready for questions.", icon=":material/check_circle:")
else:
    st.info("Upload a PDF or TXT file in the sidebar to start automatic analysis.", icon=":material/upload_file:")

ask_tab, summary_tab, mindmap_tab, flashcard_tab = st.tabs([
    ":material/chat: Ask your library",
    ":material/auto_stories: Summarize a document",
    ":material/account_tree: Mind map",
    ":material/style: Flashcards",
])

with ask_tab:
    st.markdown('<div class="section-label">Ask anything</div>', unsafe_allow_html=True)
    conversation_slot = st.empty()
    with conversation_slot.container():
        render_conversation()
    previous_result = st.session_state.get("last_answer")
    suggestions = (
        previous_result.get("recovery_suggestions", [])
        or previous_result.get("follow_up_questions", [])
        if st.session_state["conversation"] and previous_result
        else st.session_state["analysis"] or fallback_suggestions()
    )
    if not suggestions:
        suggestions = ["Ask about a different part of the document"]
    previous_suggestions = list(suggestions)
    with st.container(border=True):
        st.markdown("**Suggested follow-up questions**")
        suggestion_key = f"suggested_question_{len(st.session_state['conversation'])}"
        suggested_prompt = st.pills(
            "Try a prompt",
            suggestions,
            label_visibility="collapsed",
            key=suggestion_key,
        )
        if suggested_prompt != st.session_state["suggested_applied"]:
            st.session_state["question_input"] = suggested_prompt or ""
            st.session_state["suggested_applied"] = suggested_prompt

        with st.form("question_form", border=False):
            input_col, send_col = st.columns([0.9, 0.1], vertical_alignment="bottom")
            with input_col:
                question = st.text_input(
                    "Your question",
                    placeholder="Ask a question, then press Enter...",
                    key="question_input",
                    help="Press Enter to submit your question.",
                )
            with send_col:
                submitted = st.form_submit_button(":material/send:", type="primary", width="content")

    if submitted:
        if st.session_state["index"] is None:
            st.warning("Upload and analyze at least one document first.", icon=":material/info:")
        elif not question.strip():
            st.warning("Type a question to get started.", icon=":material/edit:")
        else:
            with st.spinner("Generating your answer...", show_time=True):
                semantic_query = analyze_question(question)
                query_embedding = make_embeddings([semantic_query])
                scores, positions = ranked_embedding_matches(
                    query_embedding[0],
                    st.session_state["index"],
                    min(
                        len(st.session_state["chunks"]),
                        max(6, len(get_document_names()) * 3),
                    ),
                )
                retrieved = expand_retrieved_context(
                    hybrid_retrieval(question, semantic_query, scores, positions)
                )
                matches = [item["chunk"] for item in retrieved]

                if not retrieved:
                    st.warning(
                        "I could not find this information in the uploaded documents."
                    )
                    st.session_state["last_answer"] = {
                        "question": question,
                        "answer": None,
                        "matches": matches,
                        "retrieved": retrieved,
                        "confidence": 0,
                        "evidence_score": 0,
                        "confidence_label": "Below relevance threshold",
                        "confidence_reason": "No retrieved document passage was relevant enough to support an answer.",
                        "evidence_summary": "No answer-grounded evidence was identified.",
                        "follow_up_questions": [],
                        "recovery_suggestions": generate_query_repair_suggestions(question),
                    }
                    st.session_state["conversation"].append(st.session_state["last_answer"])
                else:
                    numbered_evidence = "\n\n".join(
                        f"[{number}] Source: {item['source']} | Paragraphs {item.get('paragraph_start', 1)}-{item.get('paragraph_end', 1)}\nText: {item['text']}"
                        for number, item in enumerate(matches, start=1)
                    )
                    prompt = f"""
Answer the user's question using ONLY the retrieved document text below.

Use simple, direct inferences when the text clearly supports them. For example,
if the text says "seven dwarf friends", the answer to "How many dwarfs?" is "Seven."
Do not say information is missing when it is stated using similar words, synonyms,
or a clear equivalent phrase.

If the answer is truly absent from the retrieved text, respond exactly:
"I could not find this information in the uploaded documents."

Answer precisely and concisely. Use only facts explicitly stated in the retrieved excerpts or direct, unavoidable inferences. Do not fill gaps with general knowledge, guesses, or details from memory. If the excerpts conflict or do not answer the exact question, say so instead of choosing a likely answer. Break complex answers into clear paragraphs or bullet points when useful.
Every factual claim must be supported by one or more retrieved source IDs such as [1] or [2].
When the question compares or asks about multiple documents, use evidence from each relevant document and identify each source clearly. Do not treat one document as evidence for another.
Put the matching source ID immediately after the supported claim, for example [1]. Only cite source IDs that appear in the retrieved evidence. The source panel will show the exact document excerpt and its page, slide, or sheet when available.
Return valid JSON only with this exact shape:
{{"answer": "detailed answer with inline citations like [1]", "cited_source_ids": [1], "confidence_score": 0, "evidence_score": 0, "confidence_reason": "why the cited text supports the answer", "evidence_summary": "what the cited excerpts establish", "follow_up_questions": ["question grounded in this answer and evidence"]}}
Set confidence_score and evidence_score from 0 to 100 based on how completely the cited excerpts support the answer, not on writing quality.
Generate exactly three follow_up_questions that continue this user's topic, refer to details in the answer or cited excerpts, and can be answered from the retrieved document text. If the answer is unsupported, return three questions that explore what the retrieved excerpts do establish instead.
When this is a follow-up, resolve words such as "it", "that", "they", or "the previous answer" using the earlier conversation and the immediately preceding answer. Do not generate generic questions unrelated to the current or earlier topic.
The cited_source_ids must refer only to the numbered excerpts below. Include all excerpts needed to verify the answer.
Do not use outside knowledge or invent facts.

Use the earlier exchange only to understand follow-up references. Do not treat it as a source of facts.

Earlier conversation:
{recent_memory() or "No earlier conversation."}

Question:
{question}

Semantic search query:
{semantic_query}

Retrieved document text:
{numbered_evidence}
"""
                    confidence, evidence_score, confidence_label = confidence_details(
                        retrieved[0]["score"],
                        [item["score"] for item in retrieved],
                    )
                    try:
                        content = groq_chat(
                            [
                                {
                                    "role": "system",
                                    "content": "You are a careful semantic document assistant. Answer only from supplied retrieved excerpts and return the requested JSON.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                            json_mode=True,
                        )
                        generated = parse_answer_response(content, retrieved)
                        generated["answer_source"] = "Gemini or Groq LLM"
                        recovery_suggestions = []
                        if not generated["cited_source_ids"]:
                            generated = local_extractive_answer(question, retrieved) or generated
                            generated["answer_source"] = "Local document fallback"
                            recovery_suggestions = fallback_suggestions()
                        fresh_questions = fresh_follow_up_questions(
                            generated["follow_up_questions"],
                            question,
                            previous_suggestions,
                        )
                        if len(fresh_questions) < 3:
                            fresh_questions.extend(
                                fresh_follow_up_questions(
                                    contextual_follow_up_fallback(question, generated["answer"]),
                                    question,
                                    previous_suggestions + fresh_questions,
                                )
                            )
                        generated["follow_up_questions"] = fresh_questions[:3]
                        generated["recovery_suggestions"] = recovery_suggestions
                    except RuntimeError as error:
                        generated = local_extractive_answer(question, retrieved) or {
                            "answer": str(error),
                            "cited_source_ids": [],
                            "confidence_score": 0,
                            "evidence_score": 0,
                            "confidence_reason": "The answer could not be generated from the document.",
                            "evidence_summary": "No matching document sentence was found.",
                            "follow_up_questions": [],
                        }
                        generated["answer_source"] = "Local document fallback"
                        generated["recovery_suggestions"] = fallback_suggestions()
                    cited_matches = [
                        retrieved[source_id - 1]["chunk"]
                        for source_id in generated["cited_source_ids"]
                    ]
                    st.session_state["last_answer"] = {
                        "question": question,
                        "answer": generated["answer"],
                        "matches": matches,
                        "cited_matches": cited_matches,
                        "cited_source_ids": generated["cited_source_ids"],
                        "confidence": generated["confidence_score"],
                        "evidence_score": generated["evidence_score"],
                        "confidence_reason": generated["confidence_reason"],
                        "evidence_summary": generated["evidence_summary"],
                        "follow_up_questions": generated["follow_up_questions"],
                        "recovery_suggestions": generated.get("recovery_suggestions", []),
                        "answer_source": generated.get("answer_source", "Gemini or Groq LLM"),
                        "retrieved": retrieved,
                        "confidence_label": (
                            "Strong support" if generated["confidence_score"] >= 75
                            else "Partial support" if generated["confidence_score"] >= 45
                            else "Unsupported or weak support"
                        ),
                    }
                    st.session_state["conversation"].append(st.session_state["last_answer"])

                    st.rerun()

    with conversation_slot.container():
        render_conversation()

with summary_tab:
    st.markdown('<div class="section-label">Make the long version short</div>', unsafe_allow_html=True)
    if not st.session_state["chunks"]:
        st.info("Your document summaries will appear here after you process a library.", icon=":material/menu_book:")
    else:
        names = get_document_names()
        selected_document = st.selectbox("Choose a document", names)
        if selected_document not in st.session_state["summaries"]:
            with st.status("Preparing your summary...", expanded=False) as status:
                try:
                    st.session_state["summaries"][selected_document] = create_summary(selected_document)
                    status.update(label="Summary ready", state="complete")
                except RuntimeError as error:
                    st.session_state["summaries"][selected_document] = None
                    status.update(label="Summary unavailable", state="error")
                    st.warning(str(error), icon=":material/key_off:")
        st.markdown("### Summary")
        summary = st.session_state["summaries"][selected_document]
        if summary:
            st.container(border=True).write(summary)
        st.caption("Summaries are generated once per document and remembered while this workspace is open.")

with mindmap_tab:
    st.markdown('<div class="section-label">See the structure at a glance</div>', unsafe_allow_html=True)
    if not st.session_state["chunks"]:
        st.info("Your document mind maps will appear here after you process a library.", icon=":material/account_tree:")
    else:
        names = get_document_names()
        selected_document = st.selectbox("Choose a document", names, key="mindmap_document")
        if selected_document not in st.session_state["mindmaps"]:
            with st.status("Building mind map...", expanded=False) as status:
                try:
                    st.session_state["mindmaps"][selected_document] = create_mindmap(selected_document)
                    status.update(label="Mind map ready", state="complete")
                except (RuntimeError, ValueError, KeyError, json.JSONDecodeError) as error:
                    st.session_state["mindmaps"][selected_document] = local_mindmap(selected_document)
                    status.update(label="Mind map ready from document text", state="complete")
                    st.info("The AI provider was unavailable, so this map was built directly from the selected document.", icon=":material/info:")
        mindmap = st.session_state["mindmaps"][selected_document]
        if mindmap:
            root = html.escape(mindmap["title"])
            branches = []
            for branch in mindmap["branches"]:
                details = "".join(
                    f'<div class="mindmap-detail">{html.escape(detail)}</div>'
                    for detail in branch["details"]
                )
                branches.append(
                    f'<div class="mindmap-branch"><div class="mindmap-heading">{html.escape(branch["label"])}</div>{details}</div>'
                )
            st.markdown(
                f'<div class="mindmap-board"><div class="mindmap-root">{root}</div><div class="mindmap-connector"></div><div class="mindmap-branches">{"".join(branches)}</div></div>',
                unsafe_allow_html=True,
            )
        st.caption("Mind maps are generated only from the selected document and cached while this workspace is open.")

with flashcard_tab:
    st.markdown('<div class="section-label">Study the important details</div>', unsafe_allow_html=True)
    if not st.session_state["chunks"]:
        st.info("Your flashcards will appear here after you process a library.", icon=":material/style:")
    else:
        names = get_document_names()
        selected_document = st.selectbox("Choose a document", names, key="flashcard_document")
        if selected_document not in st.session_state["flashcards"]:
            with st.status("Creating flashcards...", expanded=False) as status:
                try:
                    st.session_state["flashcards"][selected_document] = create_flashcards(selected_document)
                    status.update(label="Flashcards ready", state="complete")
                except (RuntimeError, ValueError, KeyError, json.JSONDecodeError) as error:
                    st.session_state["flashcards"][selected_document] = None
                    status.update(label="Flashcards unavailable", state="error")
                    st.warning(str(error), icon=":material/key_off:")
        flashcards = st.session_state["flashcards"][selected_document]
        if flashcards:
            st.caption(f"{len(flashcards)} cards generated from {selected_document}.")
            cards = []
            for number, card in enumerate(flashcards, start=1):
                source = (
                    f'<div class="flashcard-source">Source: {html.escape(card["source"])}</div>'
                    if card["source"] else ""
                )
                cards.append(
                    f'<article class="flashcard"><div class="flashcard-number">Card {number:02d}</div><div class="flashcard-question">{html.escape(card["question"])}</div><div class="flashcard-answer">{html.escape(card["answer"])}</div>{source}</article>'
                )
            st.markdown(f'<div class="flashcard-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
        st.caption("Flashcards are generated only from the selected document and cached while this workspace is open.")