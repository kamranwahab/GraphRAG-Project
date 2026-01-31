import streamlit as st
import requests
import uuid

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="UET Enterprise RAG",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- GLOBAL STYLES ----------------
st.markdown("""
<style>
/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #ffffff;
}

/* Title */
.app-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00f5d4, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Chat bubbles */
.chat-bubble {
    padding: 14px 18px;
    border-radius: 14px;
    margin-bottom: 10px;
    animation: fadeIn 0.4s ease-in-out;
}

/* User */
.user-bubble {
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: black;
}

/* Assistant */
.assistant-bubble {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020024, #090979, #020024);
}

/* Animation */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(6px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='app-title'>🎓 UET Enterprise GraphRAG</div>", unsafe_allow_html=True)
st.caption("Hybrid Graph + Vector Retrieval • Intelligent Academic Assistant")

# ---------------- SESSION STATE ----------------
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.current_chat = chat_id
    st.session_state.chats[chat_id] = []

# ---------------- SIDEBAR (CHATGPT STYLE) ----------------
with st.sidebar:
    st.header("⚙️ Setup")

    api_url = st.text_input(
        "Colab API URL",
        value="https://5c156aaa92e8.ngrok-free.app/v1"
    )

    if st.button("📥 Ingest Data", use_container_width=True):
        with st.spinner("Building Knowledge Graph..."):
            requests.post("http://127.0.0.1:8000/ingest")
            st.success("Ingestion Complete!")

    st.divider()
    st.subheader("💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = []
        st.session_state.current_chat = new_id
        st.rerun()

    for cid in st.session_state.chats:
        label = f"Chat {cid[:6]}"
        if st.button(label, key=cid, use_container_width=True):
            st.session_state.current_chat = cid
            st.rerun()

# ---------------- CHAT WINDOW ----------------
for msg in st.session_state.chats[st.session_state.current_chat]:
    with st.chat_message(msg["role"]):
        css_class = "user-bubble" if msg["role"] == "user" else "assistant-bubble"
        st.markdown(
            f"<div class='chat-bubble {css_class}'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask about UET departments, admissions, programs...")

if prompt:
    st.session_state.chats[st.session_state.current_chat].append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(
            f"<div class='chat-bubble user-bubble'>{prompt}</div>",
            unsafe_allow_html=True
        )

    with st.spinner("🧠 Thinking with GraphRAG..."):
        res = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": prompt, "api_url": api_url}
        )
        reply = res.json().get("response", "No response from server.")

    st.session_state.chats[st.session_state.current_chat].append(
        {"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.markdown(
            f"<div class='chat-bubble assistant-bubble'>{reply}</div>",
            unsafe_allow_html=True
        )

