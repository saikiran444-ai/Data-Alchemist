# utils/chat_memory.py

import os
import json
import datetime

CHAT_FILE = "chat_history.json"

def init_chat():
    """Load chat history if file exists, else return empty list."""
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_chat(history):
    """Save chat history to file."""
    with open(CHAT_FILE, "w") as f:
        json.dump(history, f, indent=4)

def add_chat_entry(history, query, code, summary):
    """Add a new message to history and save it."""
    new_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "generated_code": code,
        "summary": summary
    }
    history.append(new_entry)
    save_chat(history)
    return history