import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from user_constants import DB_PATH, EMBED_MODEL, LLM_MODEL

@st.cache_resource
def get_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL,model_kwargs={'device': 'cpu'})
    return Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)

def get_rag_chain():
    llm = ChatOllama(model=LLM_MODEL, temperature=0.3)
    
    qa_system_prompt = """Bạn là trợ lý AI chuyên nghiệp và súc tích. 
    Sử dụng các đoạn ngữ cảnh sau đây để trả lời câu hỏi.

    YÊU CẦU QUAN TRỌNG:
    1. Trả lời tối đa 3 câu, đi thẳng vào vấn đề.
    2. Nếu không có thông tin trong tài liệu, hãy nói "Tôi không tìm thấy thông tin này trong tài liệu".
    3. DỪNG trả lời ngay khi đã đủ ý. KHÔNG lặp lại các câu ghi chú, không lặp lại lời chào hoặc câu kết thúc nhiều lần.
    4. KHÔNG tự tạo ra các đoạn hội thoại giả lập.

    NGỮ CẢNH:
    {context}"""
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    return qa_prompt | llm