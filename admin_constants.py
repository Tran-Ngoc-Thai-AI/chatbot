import os

DB_PATH = "./chroma_db"
TEMP_FOLDER = "./temp_uploads"
HISTORY_FILE = "./processed_files.json"
CHAT_LOG_FILE = "./chat_history_logs.jsonl"
DEBUG_FOLDER = "./debug_markdown"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

VALID_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc", ".xlsx", ".xls"}

# Đặt ở đây để khởi tạo ngay khi ứng dụng load cấu hình
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(DEBUG_FOLDER, exist_ok=True)