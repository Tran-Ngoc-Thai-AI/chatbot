import streamlit as st
import os
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from user_constants import LOG_FILE
from user_utils import save_log
from user_core_logic import get_vectorstore, get_rag_chain

st.set_page_config(page_title="Chat AI Nội bộ", page_icon="🤖", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Quản lý")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "rb") as f:
            st.download_button(
                label="📥 Tải file Log",
                data=f,
                file_name=f"logs_{datetime.now().strftime('%d%m_%H%M')}.jsonl",
                mime="application/jsonl"
            )

# --- CHAT UI ---
st.title("🤖 Chat với Tài liệu Doanh Nghiệp")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

if user_input := st.chat_input("Nhập câu hỏi tại đây..."):
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                # Retrieval
                vectorstore = get_vectorstore()
                retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                docs = retriever.invoke(user_input)
                context_text = "\n\n".join(doc.page_content for doc in docs)

                # Chain
                chain = get_rag_chain()
                history = st.session_state.messages[-6:] 
                
                response = chain.invoke({
                    "input": user_input,
                    "chat_history": history,
                    "context": context_text
                })
                
                answer = response.content
                st.markdown(answer)
                
                # Lưu trữ
                st.session_state.messages.append(AIMessage(content=answer))
                save_log(user_input, context_text, answer)
                
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")