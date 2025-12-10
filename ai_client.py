# backend/ai_client.py
import requests
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME, SYSTEM_PROMPT, HISTORY_MAX_TURNS

def build_messages(user_message: str, history: list):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    # history: list of {"role": "user"/"assistant", "content": "..."}
    trimmed = history[-HISTORY_MAX_TURNS*2:]
    msgs.extend(trimmed)
    msgs.append({"role": "user", "content": user_message})
    return msgs

def generate_reply(user_message: str, history: list) -> str:
    messages = build_messages(user_message, history)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
    }
    resp = requests.post(f"{OPENAI_BASE_URL}/chat/completions",
                         headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
