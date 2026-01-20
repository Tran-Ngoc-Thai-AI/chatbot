import os
import streamlit as st
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from admin_constants import DB_PATH, DEBUG_FOLDER, EMBED_MODEL
from admin_utils import calculate_md5, load_history, transform_to_markdown, save_to_history

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL,model_kwargs={'device': 'cpu'})

def process_single_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        file_hash = calculate_md5(file_path)
        if file_hash in load_history(): 
            return 0, "Skip (Đã có)"

        clean_text = transform_to_markdown(file_path)
        if not clean_text: return None, "Lỗi trích xuất nội dung"

        # Debug lưu file MD
        debug_path = os.path.join(DEBUG_FOLDER, f"{file_name}.md")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        documents = [Document(page_content=clean_text, metadata={"source": file_name})]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000, 
            chunk_overlap=200,
            separators=["\n\n---", "\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        Chroma.from_documents(
            documents=chunks, 
            embedding=get_embedding_model(), 
            persist_directory=DB_PATH
        )
        
        save_to_history(file_hash)
        return len(chunks), "Thành công"
    except Exception as e:
        return None, str(e)