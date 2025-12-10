# backend/memory.py
import json
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def history_path(user_id: str) -> Path:
    return DATA_DIR / f"{user_id}_history.json"

def load_history(user_id: str):
    p = history_path(user_id)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_history(user_id: str, history):
    p = history_path(user_id)
    p.write_text(json.dumps(history, ensure_ascii=False), encoding="utf-8")
