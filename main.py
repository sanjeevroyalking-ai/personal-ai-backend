# backend/main.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

from memory import load_history, save_history
from ai_client import generate_reply

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict to your app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = load_history(req.user_id)
    reply = generate_reply(req.message, history)

    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})
    save_history(req.user_id, history)

    return ChatResponse(reply=reply)


# ---------- NEW: file upload + analysis ----------

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class UploadResponse(BaseModel):
    reply: str


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    content_bytes = await file.read()
    with open(file_path, "wb") as f:
        f.write(content_bytes)

    # Try to decode as text (fallback to bytes length)
    try:
        text_content = content_bytes.decode("utf-8", errors="ignore")
    except Exception:
        text_content = ""

    # Build a prompt for the AI to analyze the file
    user_id = "file_user"
    history = load_history(user_id)

    if text_content.strip():
        prompt = (
            f"The user uploaded a file named '{file.filename}'. "
            f"Here is the content:\n\n{text_content[:4000]}\n\n"
            "Please summarize the important points and mention anything useful for the user."
        )
    else:
        prompt = (
            f"The user uploaded a file named '{file.filename}', "
            "but the content could not be read as text. "
            "Reply politely and ask the user to upload a text/PDF file if they want analysis."
        )

    reply = generate_reply(prompt, history)

    history.append({"role": "user", "content": f"Uploaded file: {file.filename}"})
    history.append({"role": "assistant", "content": reply})
    save_history(user_id, history)

    return UploadResponse(reply=reply)
