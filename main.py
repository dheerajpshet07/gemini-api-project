import os
import time
import requests
from fastapi import FastAPI, Query
from dotenv import load_dotenv
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
# Load .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

# Get API key
API_KEY = os.getenv("GEMINI_API_KEY")

print("DEBUG KEY:", API_KEY)

# You can switch model if needed
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
# Alternative (less load sometimes):
# URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


@app.get("/")
def home():
    return {"message": "Gemini API Running 🚀"}


# 🔁 Retry function for handling 503 errors
def call_gemini(body):
    retries = 3

    for i in range(retries):
        try:
            response = requests.post(
                URL,
                params={"key": API_KEY},
                json=body,
                timeout=10
            )
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

        # ✅ Success
        if response.status_code == 200:
            return response.json()

        # 🔁 Retry if server busy
        if response.status_code == 503:
            time.sleep(2)
            continue

        # ❌ Other errors
        return {"error": response.text}

    return {"error": "Gemini API unavailable after retries"}


@app.post("/generate")
def generate(prompt: str, debug: bool = Query(False)):

    # Validate API key
    if not API_KEY:
        return {"error": "API key not loaded"}

    # Validate prompt
    if not prompt or not prompt.strip():
        return {"error": "Prompt cannot be empty"}

    # Request body
    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    data = call_gemini(body)

    if "error" in data:
        return data

    # Extract response safely
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        text = "No response generated"

    result = {
        "prompt": prompt,
        "response": text
    }

    # Debug mode
    if debug:
        result["raw"] = data

    return result