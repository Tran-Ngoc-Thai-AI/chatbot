import json
from datetime import datetime
from user_constants import LOG_FILE

def save_log(user_input, context, ai_response):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_query": user_input,
        "retrieved_context": context,
        "ai_answer": ai_response
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")