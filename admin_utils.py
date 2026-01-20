import os
import json
import hashlib
import pandas as pd
import mammoth
import fitz
from admin_constants import HISTORY_FILE

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_to_history(file_hash):
    history = load_history()
    history.add(file_hash)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history), f)

def transform_to_markdown(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, engine='openpyxl' if ext == ".xlsx" else None)
            if df.empty: return "File Excel rỗng."
            return f"Dữ liệu bảng từ file {os.path.basename(file_path)}:\n\n" + df.to_markdown(index=False, tablefmt="grid")
        
        elif ext in [".docx", ".doc"]:
            with open(file_path, "rb") as docx_file:
                return mammoth.convert_to_markdown(docx_file).value
        
        elif ext == ".pdf":
            doc = fitz.open(file_path)
            content = "\n\n".join([page.get_text("text") for page in doc])
            doc.close()
            return content
        
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Lỗi trích xuất: {e}")
        return None