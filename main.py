from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()
app = FastAPI()

# Allow requests from anywhere (can restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory log storage
if not os.path.exists("logs"):
    os.makedirs("logs")

from utils.client_utils import get_client_config

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    client_id = data.get("client_id")
    message = data.get("prompt")

    client_config = get_client_config(client_id)
    if not client_config or not client_config.get("enabled"):
        return {"reply": "⚠️ Unknown or disabled client."}

    greeting = client_config.get("bot_greeting", "Hello!")

    reply = f"{greeting} You said: '{message}'"

    # Log conversation
    log_path = f"logs/{client_id}.log"
    with open(log_path, "a") as f:
        log = {
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "user_message": message,
            "bot_reply": reply
        }
        f.write(json.dumps(log) + "\n")

    return {"reply": reply}
