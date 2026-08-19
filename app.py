import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from src.rag import RAGAssistant
from src.llm import DEFAULT_MODELS, UI_PROVIDERS
from src.version import __version__

load_dotenv()

DOCUMENTS_DIR = Path(os.getenv("RAG_DOCUMENTS_DIR", "documents"))
DATABASE_DIR = Path(os.getenv("RAG_DATABASE_DIR", "database"))
MAX_UPLOAD_BYTES = 1024 * 1024 * 1024  # 1 GB
st.set_page_config(page_title="Archive — Document Assistant", page_icon="◼", layout="wide")
st.markdown("""
<style>
:root{--ink:#f4efe7;--muted:#b8afa5;--paper:#171311;--card:#211c19;--line:#3a312c;--accent:#31835e}
html,body,[class*="css"]{font-family:Inter,"Segoe UI",sans-serif}.stApp{background:#171311!important;background-image:none!important;color:var(--ink)}
[data-testid="stMain"] p,[data-testid="stMain"] label,[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3{color:var(--ink)}
[data-testid="stMain"] [data-testid="stCaptionContainer"] p{color:var(--muted)}
[data-testid="stHeader"]{background:transparent}[data-testid="stSidebar"]{background:#110e0d;border-right:1px solid #302824}
[data-testid="stSidebar"] *{color:#f3f1e9}[data-testid="stSidebar"] .stTextInput input{background:#243029;border:1px solid #3b4840;color:white}
[data-testid="stSidebar"] hr{border-color:#344139}.block-container{max-width:1120px;padding-top:2.2rem;padding-bottom:5rem}
.brand{letter-spacing:.18em;font-size:.74rem;font-weight:700;color:#a9b9ae}.hero{padding:1.4rem 0 1.8rem;border-bottom:1px solid var(--line);margin-bottom:1.5rem}
.hero h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(2.4rem,5vw,4.4rem);line-height:1.02;letter-spacing:-.035em;margin:0 0 .8rem;color:var(--ink)}
.hero p{max-width:650px;color:var(--muted);font-size:1.08rem;line-height:1.65;margin:0}.eyebrow{color:var(--accent);font-weight:700;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.8rem}
.section-title{font-size:1.05rem;font-weight:700;margin:1.6rem 0 .15rem}.section-copy{color:var(--muted);font-size:.9rem;margin-bottom:1rem}
.metric-card{background:#1b1e17;border:1px solid #363b2d;border-radius:14px;padding:1rem 1.15rem;min-height:92px;box-shadow:0 10px 30px rgba(0,0,0,.22),inset 0 1px 0 rgba(174,184,135,.04)}
.metric-label{color:var(--muted);font-size:.76rem;text-transform:uppercase;letter-spacing:.08em}.metric-value{font-size:1.55rem;font-weight:700;margin-top:.25rem}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#69c18a;margin-right:.45rem}.privacy{color:#a9b9ae;font-size:.78rem;line-height:1.5}
.stButton>button{border-radius:10px!important;font-weight:700!important;min-height:44px!important;border:1px solid #18221d!important;background:#18221d!important;color:#fff!important;transition:all .16s ease;box-shadow:0 5px 14px rgba(23,32,27,.14)!important}
.stButton>button p,.stButton>button span,.stButton>button div{color:#fff!important;opacity:1!important}
.stButton>button:hover{border-color:#285e46!important;background:#285e46!important;color:#fff!important;transform:translateY(-1px);box-shadow:0 8px 18px rgba(23,32,27,.18)!important}
.stButton>button:active{transform:translateY(0);box-shadow:0 2px 5px rgba(23,32,27,.12)!important}.stButton>button:focus{box-shadow:0 0 0 3px rgba(31,103,72,.22)!important}
.stButton>button[kind="primary"],[data-testid="stBaseButton-primary"]{background:#1f6748!important;border-color:#1f6748!important;color:#fff!important}
.stButton>button[kind="primary"] p,[data-testid="stBaseButton-primary"] p{color:#fff!important}.stButton>button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover{background:#18563b!important;color:#fff!important}
[data-testid="stFileUploader"]{background:#211c19;border:1px solid #3a312c;border-radius:14px;padding:.7rem;box-shadow:0 10px 30px rgba(0,0,0,.16)}[data-testid="stFileUploaderDropzone"]{background:#1b1715;border:1px dashed #67594f}
[data-testid="stFileUploaderDropzone"] button,[data-testid="stBaseButton-secondary"]{background:#18221d!important;border:1px solid #18221d!important;color:#fff!important}
[data-testid="stFileUploaderDropzone"] button p,[data-testid="stFileUploaderDropzone"] button span,[data-testid="stBaseButton-secondary"] p{color:#fff!important;opacity:1!important}
[data-testid="stFileUploaderDropzone"] button:hover,[data-testid="stBaseButton-secondary"]:hover{background:#285e46!important;border-color:#285e46!important;color:#fff!important}
[data-testid="stChatMessage"]{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:.35rem .7rem;margin:.6rem 0}
[data-testid="stChatInput"]{border-color:#c7ccc5;background:var(--card)}details{background:var(--card);border-color:var(--line)!important;border-radius:10px!important}#MainMenu,footer{visibility:hidden}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand">ARCHIVE</div>', unsafe_allow_html=True)
    st.markdown("### Workspace")
    st.caption("Prepare your documents, then start a conversation.")
    st.divider()
    configured_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    provider_index = next((i for i, name in enumerate(UI_PROVIDERS)
                           if name.lower() == configured_provider), 0)
    provider = st.selectbox("LLM provider", UI_PROVIDERS, index=provider_index,
                            help="Ollama is local, Gemini has a free tier, and OpenAI uses API credits.")
    provider_key = provider.lower()
    configured_model = os.getenv(f"{provider_key.upper()}_MODEL")
    if not configured_model and provider_key == configured_provider:
        configured_model = os.getenv("CHAT_MODEL")
    chat_model = st.text_input("Response model", configured_model or DEFAULT_MODELS[provider_key],
                               key=f"chat_model_{provider_key}")
    api_key = ""
    base_url = ""
    if provider_key != "ollama":
        api_key = st.text_input("API key", value=os.getenv(f"{provider_key.upper()}_API_KEY",
                                os.getenv("LLM_API_KEY", "")), type="password")
        base_url = st.text_input("API base URL (optional)", os.getenv("LLM_BASE_URL", ""))
        if provider_key == "gemini":
            st.caption("Use an API key from a Gemini AI Studio project without billing enabled. "
                       "When its free quota is exhausted, requests stop instead of falling back to a paid provider.")
        else:
            st.warning("OpenAI API usage is billed separately from ChatGPT subscriptions. "
                       "The app only uses credits already available on your API account.")
    embedding_model = st.text_input("Embedding model", os.getenv("EMBEDDING_MODEL", "nomic-embed-text"))
    ollama_host = st.text_input("Local service", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    default_top_k = max(2, min(10, int(os.getenv("RAG_TOP_K", "8"))))
    top_k = st.slider("Search depth", 2, 10, default_top_k,
                      help="All documents are searched semantically and by keyword; the most relevant sections are added to the answer.")
    st.divider()
    privacy_text = ("Local and private<br><br>Your documents never leave this computer."
                    if provider_key == "ollama" else
                    f"Local retrieval<br><br>Relevant document excerpts are sent to {provider} to generate an answer.")
    st.markdown(f'<div class="privacy"><span class="status-dot"></span>{privacy_text}</div>', unsafe_allow_html=True)
    st.caption(f"Version {__version__}")

@st.cache_resource
def get_assistant(chat, embedding, host, provider_name, key, api_base):
    return RAGAssistant(DATABASE_DIR, chat, embedding, host, provider_name, key, api_base or None)

try:
    assistant = get_assistant(chat_model, embedding_model, ollama_host, provider, api_key, base_url)
except Exception as exc:
    st.error(f"The workspace could not be opened: {exc}")
    st.stop()

if flash := st.session_state.pop("flash_message", None):
    kind, message = flash
    getattr(st, kind)(message)

st.markdown("""<div class="hero"><div class="eyebrow">Local document assistant</div>
<h1>A simpler way to<br>talk to your documents.</h1><p>Search long reports, research, and notes in one place.
Get answers directly from your documents, complete with page citations.</p></div>""", unsafe_allow_html=True)

document_count = len([p for p in DOCUMENTS_DIR.glob("*.*") if p.name != ".gitkeep"]) if DOCUMENTS_DIR.exists() else 0
for column, label, value in zip(st.columns(3), ["Documents", "Indexed chunks", "System status"],
                                [document_count, assistant.store.count, "Ready" if assistant.store.count else "Waiting for documents"]):
    with column:
        dot = '<span class="status-dot"></span>' if label == "System status" else ""
        size = "1.2rem" if label == "System status" else "1.55rem"
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value" style="font-size:{size}">{dot}{value}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Document library</div><div class="section-copy">Add PDF, TXT, or Markdown files. Up to 1 GB per file, with no page limit.</div>', unsafe_allow_html=True)
uploaded = st.file_uploader("Drop documents here", type=["pdf", "txt", "md"], accept_multiple_files=True, label_visibility="collapsed")
col1, col2, _ = st.columns([1.25, 1.25, 2])
with col1:
    index_uploaded = st.button("Prepare documents", type="primary", use_container_width=True,
                               key="prepare_documents", help="Makes the selected documents searchable.")
with col2:
    scan_folder = st.button("Rescan folder", use_container_width=True,
                            key="scan_documents", help="Reprocesses files in the documents folder.")

if index_uploaded:
    if not uploaded:
        st.warning("Select at least one document above first.")
    else:
        oversized = [file.name for file in uploaded if file.size > MAX_UPLOAD_BYTES]
        if oversized:
            st.error("These files exceed the 1 GB limit: " + ", ".join(oversized))
        else:
            DOCUMENTS_DIR.mkdir(exist_ok=True)
            try:
                progress, total = st.progress(0, text="Preparing documents…"), 0
                for index, file in enumerate(uploaded, start=1):
                    destination = DOCUMENTS_DIR / Path(file.name).name
                    # getbuffer() avoids a second full memory copy for a 1 GB file.
                    destination.write_bytes(file.getbuffer())
                    total += assistant.index_file(destination)
                    progress.progress(index / len(uploaded), text=f"Processed {destination.name}")
                st.session_state.flash_message = (
                    "success", f"{len(uploaded)} documents ready. Created {total} text chunks."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"The documents could not be prepared: {exc}")

if scan_folder:
    try:
        result = assistant.index_directory(DOCUMENTS_DIR)
        if result:
            st.session_state.flash_message = ("success", f"Reprocessed {len(result)} documents.")
            st.rerun()
        else:
            st.info("No supported documents were found in the folder.")
    except Exception as exc:
        st.error(f"The folder could not be scanned: {exc}")

st.divider()
st.markdown('<div class="section-title">Ask your documents</div><div class="section-copy">Request a summary, find details, or compare sections.</div>', unsafe_allow_html=True)
if "messages" not in st.session_state:
    st.session_state.messages = []
if not st.session_state.messages:
    st.info('Prepare a document to begin. For example: “What are the three key findings in this report?”')
for message in st.session_state.messages:
    avatar = "◼" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if question := st.chat_input("Ask a question about your document…", disabled=assistant.store.count == 0):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant", avatar="◼"):
        try:
            with st.spinner("Reviewing the relevant pages…"):
                answer, sources = assistant.ask(question, top_k)
            st.markdown(answer)
            if sources:
                with st.expander(f"Review sources · {len(sources)} sections"):
                    for number, item in enumerate(sources, 1):
                        meta = item["metadata"]
                        st.markdown(f"**{number}. {meta['source']} · Page {meta['page']}**")
                        st.caption(item["text"])
                        if number < len(sources): st.divider()
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as exc:
            st.error(f"A response could not be generated. Check the selected provider settings: {exc}")
