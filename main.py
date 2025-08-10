from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from openai import OpenAI
import os, json, glob
from datetime import datetime

load_dotenv()

app = FastAPI()

# CORS (widen while testing; tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://desertforgedai.com",
        "https://www.desertforgedai.com",
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_credentials=False,
)

@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"ok": True, "has_openai_key": bool(os.getenv("OPENAI_API_KEY"))}

def get_openai():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is missing")
    return OpenAI(api_key=key)

# Support both /client/update and /api/client/update (with/without trailing slash)
@app.post("/client/update")
@app.post("/client/update/")
@app.post("/api/client/update")
@app.post("/api/client/update/")
async def chat(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Accept multiple aliases from the frontend
    message = (data.get("prompt") or data.get("message") or data.get("input") or data.get("text") or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required; send 'prompt' or 'message'.")

    client_id = data.get("client_id", "anonymous")
    meta = data.get("meta") or {}
    history = data.get("history") or []

    company = meta.get("companyName", "") or meta.get("company", "")
    values  = meta.get("companyValues", "") or meta.get("values", "")
    tone    = meta.get("botTone", "") or meta.get("tone", "")

    system_prompt = f"""You are an AI assistant for {company}.
The company's values are: {values}.
Please answer with a {tone} tone, and help users as if you represent this business.
"""

    client = get_openai()
    try:
        # Convert any simple history objects if needed
        msgs = [{"role": "system", "content": system_prompt}]
        # If your history is already OpenAI-format, you can just extend
        for h in history:
            if isinstance(h, dict) and "role" in h and "content" in h:
                msgs.append(h)
        msgs.append({"role": "user", "content": message})

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=msgs
        )
        reply = resp.choices[0].message.content
    except Exception as e:
        reply = f"⚠️ API Error: {str(e)}"

    # Log (ephemeral on Render unless you attach a disk)
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/{client_id}.json"
    try:
        existing = []
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                existing = json.load(f)
    except Exception:
        existing = []
    existing.append({
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "reply": reply,
        "meta": meta
    })
    with open(log_path, "w") as f:
        json.dump(existing, f, indent=2)

    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
