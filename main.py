from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import os, json
from datetime import datetime
import glob

# 🔐 Load .env vars
load_dotenv()

app = FastAPI()

# 🌐 Enable CORS — restrict to your site in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://desertforgedai.com",
        "https://www.desertforgedai.com",
        "http://localhost:5173",      # local dev
        "http://desertforgedai.local" # local WP dev
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# 🧠 Main chat route
@app.post("/client/update")
async def chat(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Match keys your WP plugin sends
    client_id = data.get("client_id") or "anonymous"
    message = data.get("message", "").strip()
    meta = data.get("meta", {})

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    # Map meta keys from WP → backend
    company = meta.get("companyName", "")
    values = meta.get("companyValues", "")
    tone = meta.get("botTone", "")

    system_prompt = f"""You are an AI assistant for {company}.
The company's values are: {values}.
Please answer with a {tone} tone, and help users as if you represent this business.
"""

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        import traceback
        traceback.print_exc()
        reply = f"⚠️ API Error: {str(e)}"

    # 📁 Save to user log
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/{client_id}.json"

    try:
        existing_logs = []
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                existing_logs = json.load(f)
    except Exception:
        existing_logs = []

    existing_logs.append({
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "reply": reply,
        "meta": meta
    })

    with open(log_path, "w") as f:
        json.dump(existing_logs, f, indent=2)

    return {"reply": reply}

# ✅ GET all logs from /logs
@app.get("/logs")
async def get_all_logs():
    logs = []
    for file in glob.glob("logs/*.json"):
        try:
            with open(file, "r") as f:
                logs.extend(json.load(f))
        except:
            continue
    return logs

# ✅ Health check
@app.get("/health")
async def health():
    return {"status": "ok"}
