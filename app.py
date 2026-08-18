from pathlib import Path
import streamlit as st
from src.rag import RAGAssistant
from src.version import __version__

DOCUMENTS_DIR, DATABASE_DIR = Path("documents"), Path("database")
MAX_UPLOAD_BYTES = 1024 * 1024 * 1024  # 1 GB
st.set_page_config(page_title="Arşiv — Doküman Asistanı", page_icon="◼", layout="wide")
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
    st.markdown('<div class="brand">ARŞİV</div>', unsafe_allow_html=True)
    st.markdown("### Çalışma alanı")
    st.caption("Belgelerinizi hazırlayın, ardından konuşmaya başlayın.")
    st.divider()
    chat_model = st.text_input("Yanıt modeli", "llama3.2:3b")
    embedding_model = st.text_input("Arama modeli", "nomic-embed-text")
    ollama_host = st.text_input("Yerel servis", "http://localhost:11434")
    top_k = st.slider("Arama derinliği", 2, 10, 5, help="Her soruda incelenecek ilgili parça sayısı.")
    st.divider()
    st.markdown('<div class="privacy"><span class="status-dot"></span>Yerel ve gizli<br><br>Belgeleriniz bu bilgisayardan dışarı gönderilmez.</div>', unsafe_allow_html=True)
    st.caption(f"Sürüm {__version__}")

@st.cache_resource
def get_assistant(chat, embedding, host):
    return RAGAssistant(DATABASE_DIR, chat, embedding, host)

try:
    assistant = get_assistant(chat_model, embedding_model, ollama_host)
except Exception as exc:
    st.error(f"Çalışma alanı açılamadı: {exc}")
    st.stop()

if flash := st.session_state.pop("flash_message", None):
    kind, message = flash
    getattr(st, kind)(message)

st.markdown("""<div class="hero"><div class="eyebrow">Yerel doküman asistanı</div>
<h1>Belgelerinizle<br>konuşmanın sade yolu.</h1><p>Uzun raporları, araştırmaları ve notları tek bir yerde arayın.
Yanıtları doğrudan belgenizden, sayfa kaynağıyla birlikte alın.</p></div>""", unsafe_allow_html=True)

document_count = len([p for p in DOCUMENTS_DIR.glob("*.*") if p.name != ".gitkeep"]) if DOCUMENTS_DIR.exists() else 0
for column, label, value in zip(st.columns(3), ["Belgeler", "İndekslenen parçalar", "Sistem durumu"],
                                [document_count, assistant.store.count, "Hazır" if assistant.store.count else "Belge bekliyor"]):
    with column:
        dot = '<span class="status-dot"></span>' if label == "Sistem durumu" else ""
        size = "1.2rem" if label == "Sistem durumu" else "1.55rem"
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value" style="font-size:{size}">{dot}{value}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Belge kitaplığı</div><div class="section-copy">PDF, TXT veya Markdown ekleyin. Dosya başına en fazla 1 GB; sayfa sınırı yoktur.</div>', unsafe_allow_html=True)
uploaded = st.file_uploader("Belgeleri buraya bırakın", type=["pdf", "txt", "md"], accept_multiple_files=True, label_visibility="collapsed")
col1, col2, _ = st.columns([1.25, 1.25, 2])
with col1:
    index_uploaded = st.button("Belgeleri hazırla", type="primary", use_container_width=True,
                               key="prepare_documents", help="Seçtiğiniz belgeleri aranabilir hale getirir.")
with col2:
    scan_folder = st.button("Klasörü yeniden tara", use_container_width=True,
                            key="scan_documents", help="documents klasöründeki dosyaları yeniden işler.")

if index_uploaded:
    if not uploaded:
        st.warning("Önce yukarıdaki alandan en az bir belge seçin.")
    else:
        oversized = [file.name for file in uploaded if file.size > MAX_UPLOAD_BYTES]
        if oversized:
            st.error("Şu dosyalar 1 GB sınırını aşıyor: " + ", ".join(oversized))
        else:
            DOCUMENTS_DIR.mkdir(exist_ok=True)
            try:
                progress, total = st.progress(0, text="Belgeler hazırlanıyor…"), 0
                for index, file in enumerate(uploaded, start=1):
                    destination = DOCUMENTS_DIR / Path(file.name).name
                    # getbuffer(), 1 GB dosyada ikinci bir tam bellek kopyası oluşmasını önler.
                    destination.write_bytes(file.getbuffer())
                    total += assistant.index_file(destination)
                    progress.progress(index / len(uploaded), text=f"{destination.name} işlendi")
                st.session_state.flash_message = (
                    "success", f"{len(uploaded)} belge hazır. Toplam {total} metin parçası oluşturuldu."
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Belgeler hazırlanamadı: {exc}")

if scan_folder:
    try:
        result = assistant.index_directory(DOCUMENTS_DIR)
        if result:
            st.session_state.flash_message = ("success", f"{len(result)} belge yeniden hazırlandı.")
            st.rerun()
        else:
            st.info("Klasörde henüz desteklenen bir belge bulunmuyor.")
    except Exception as exc:
        st.error(f"Klasör taranamadı: {exc}")

st.divider()
st.markdown('<div class="section-title">Belgelere sorun</div><div class="section-copy">Özet isteyin, ayrıntı bulun veya bölümleri karşılaştırın.</div>', unsafe_allow_html=True)
if "messages" not in st.session_state:
    st.session_state.messages = []
if not st.session_state.messages:
    st.info("Başlamak için bir belge hazırlayın. Örneğin: “Bu raporun üç temel sonucu nedir?”")
for message in st.session_state.messages:
    avatar = "◼" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if question := st.chat_input("Belgeniz hakkında bir soru yazın…", disabled=assistant.store.count == 0):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant", avatar="◼"):
        try:
            with st.spinner("İlgili sayfalar inceleniyor…"):
                answer, sources = assistant.ask(question, top_k)
            st.markdown(answer)
            if sources:
                with st.expander(f"Kaynakları incele · {len(sources)} bölüm"):
                    for number, item in enumerate(sources, 1):
                        meta = item["metadata"]
                        st.markdown(f"**{number}. {meta['source']} · Sayfa {meta['page']}**")
                        st.caption(item["text"])
                        if number < len(sources): st.divider()
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as exc:
            st.error(f"Şu anda yanıt oluşturulamadı. Yerel servisi kontrol edin: {exc}")
