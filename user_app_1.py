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

# 2. Phản hồi của Assistant
    with st.chat_message("assistant"):
        # Tạo placeholder để hiển thị nội dung đang stream
        response_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Đang tìm kiếm tài liệu..."):
            try:
                # Bước A: Retrieval (giữ nguyên logic của bạn)
                vectorstore = get_vectorstore()
                retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
                docs = retriever.invoke(user_input)
                context_text = "\n\n".join(doc.page_content for doc in docs)

                # Bước B: Gọi Chain với phương thức .stream()
                chain = get_rag_chain()
                history = st.session_state.messages[-6:] 
                
                # Sử dụng st.write_stream để hiển thị hiệu ứng gõ chữ
                def generate_responses():
                    seen_content = set() # Dùng để kiểm tra lặp từ/cụm từ cực ngắn nếu cần
                    full_text = ""
                    
                    for chunk in chain.stream({
                        "input": user_input,
                        "chat_history": history,
                        "context": context_text
                    }):
                        if chunk and hasattr(chunk, 'content'):
                            content = chunk.content
                            if content:
                                # Kiểm tra thủ công: Nếu đoạn text mới đã xuất hiện quá nhiều trong full_text
                                # Đây là "chốt chặn" cuối cùng nếu Model vẫn cố tình lặp
                                if full_text.count(content) > 3 and len(content) > 10:
                                    break
                                
                                full_text += content
                                yield content

                # Hiển thị stream trực tiếp lên giao diện
                full_response = st.write_stream(generate_responses())
                
                # Bước C: Lưu vào session và ghi log sau khi stream xong
                st.session_state.messages.append(AIMessage(content=full_response))
                save_log(user_input, context_text, full_response)
                
            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {str(e)}")