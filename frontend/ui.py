import streamlit as st
import requests

st.title("🎓 UET Enterprise RAG")

with st.sidebar:
    st.header("Setup")
    api_url = st.text_input("Colab API URL", value="https://5c156aaa92e8.ngrok-free.app/v1")
    
    if st.button("Ingest Data"):
        with st.spinner("Building Graph..."):
            requests.post("http://127.0.0.1:8000/ingest")
            st.success("Ingestion Complete!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask about UET Departments..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("Thinking..."):
        res = requests.post("http://127.0.0.1:8000/chat", 
                            json={"message": prompt, "api_url": api_url})
        reply = res.json()["response"]
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)