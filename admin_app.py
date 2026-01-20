# import st_rerun # Nếu streamlit cũ hoặc dùng st.rerun()
import streamlit as st
import os
import glob
import shutil
import time
from admin_constants import DB_PATH, TEMP_FOLDER, HISTORY_FILE, CHAT_LOG_FILE, DEBUG_FOLDER, VALID_EXTENSIONS
from admin_core_logic import process_single_file

st.set_page_config(page_title="RAG Admin Console", layout="wide", page_icon="⚙️")
st.title("⚙️ Trang Quản Trị Dữ Liệu AI")

tab_import, tab_setting = st.tabs(["📂 Nạp Dữ Liệu", "🛠️ Cài đặt Hệ thống"])

with tab_import:
    mode = st.radio("Chế độ:", ["Upload File", "Quét Folder Local"], horizontal=True)
    if mode == "Upload File":
        uploaded_files = st.file_uploader("Chọn file:", type=["pdf", "txt", "docx", "xlsx"], accept_multiple_files=True)
        if st.button("Xử lý Upload", type="primary"):
            if uploaded_files:
                bar = st.progress(0)
                for i, file in enumerate(uploaded_files):
                    path = os.path.join(TEMP_FOLDER, file.name)
                    with open(path, "wb") as f: f.write(file.getbuffer())
                    c, msg = process_single_file(path)
                    bar.progress((i+1)/len(uploaded_files))
                    if c: st.success(f"✅ {file.name}")
                    elif "Skip" in msg: st.info(f"⏭️ {file.name}")
                    else: st.error(f"❌ {file.name}: {msg}")
                    if os.path.exists(path): os.remove(path)
    else:
        folder = st.text_input("Đường dẫn Folder:")
        if st.button("Quét Folder"):
            if os.path.isdir(folder):
                files = [os.path.join(r, f) for r, d, fs in os.walk(folder) for f in fs if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS]
                bar = st.progress(0)
                count = 0
                for i, fpath in enumerate(files):
                    c, m = process_single_file(fpath)
                    bar.progress((i+1)/len(files))
                    if c: count += 1
                st.success(f"Hoàn tất! Thêm mới: {count} file.")

with tab_setting:
    st.warning("⚠️ Vùng nguy hiểm")
    if st.button("🗑️ XÓA TOÀN BỘ DATA (RESET)"):
        try:
            if os.path.exists(DB_PATH):
                for f in glob.glob(f'{DB_PATH}/*'):
                    if os.path.isfile(f): os.remove(f)
                    elif os.path.isdir(f): shutil.rmtree(f, ignore_errors=True)
            for file_path in [HISTORY_FILE, CHAT_LOG_FILE]:
                if os.path.exists(file_path): os.remove(file_path)
            if os.path.exists(DEBUG_FOLDER):
                shutil.rmtree(DEBUG_FOLDER, ignore_errors=True)
            os.makedirs(DEBUG_FOLDER, exist_ok=True)
            st.cache_resource.clear()
            st.success("Đã reset hệ thống!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi reset: {e}")