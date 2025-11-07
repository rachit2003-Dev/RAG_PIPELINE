# ------------------------------------------------------------
# 🔹 Import dependencies and auto-install if missing
# ------------------------------------------------------------
import os, re, subprocess, requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

try:
    import fastapi
except ImportError:
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

# ------------------------------------------------------------
# 🔹 Load environment variables (.env)
# ------------------------------------------------------------
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8000))

# ------------------------------------------------------------
# 🔹 Initialize FastAPI app
# ------------------------------------------------------------
app = FastAPI(title="Smart Validation API", version="3.0.0")

# ------------------------------------------------------------
# 🔹 Data Models
# ------------------------------------------------------------
class GSTRequest(BaseModel):
    gst_number: str

class AddressRequest(BaseModel):
    address: str
    city: str
    state: str
    zipcode: str

# ------------------------------------------------------------
# 🔹 Core Logic Functions
# ------------------------------------------------------------
def validate_gst_number(gst_number: str) -> bool:
    """Regex check for GST format"""
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(pattern, gst_number))

def openai_verify(prompt: str) -> bool:
    """Uses OpenAI API for intelligent validation"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"{prompt}\nRespond only with True or False."
        )
        reply = str(response.output[0].content[0].text).strip().lower()
        return "true" in reply
    except Exception:
        return False

def validate_us_address(address: str, city: str, state: str, zipcode: str) -> bool:
    """Combined OpenAI + regex address validation"""
    base_check = bool(re.match(r'^\d{5}(-\d{4})?$', zipcode))
    ai_prompt = f"Is this a valid US address: {address}, {city}, {state}, {zipcode}?"
    ai_check = openai_verify(ai_prompt)
    return base_check or ai_check

# ------------------------------------------------------------
# 🔹 API Routes
# ------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "Welcome to Smart Validation API. Use /validate-gst or /validate-address."}

@app.post("/validate-gst")
def validate_gst(request: GSTRequest):
    if not validate_gst_number(request.gst_number):
        if not openai_verify(f"Check if this GST number looks valid: {request.gst_number}"):
            raise HTTPException(status_code=400, detail="Invalid GST Number.")
    return {"gst_number": request.gst_number, "valid": True, "message": "Valid GST ✅"}

@app.post("/validate-address")
def validate_address(request: AddressRequest):
    if not validate_us_address(request.address, request.city, request.state, request.zipcode):
        raise HTTPException(status_code=400, detail="Invalid or Unverifiable Address.")
    return {"address": request.address, "valid": True, "message": "Valid US Address ✅"}

# ------------------------------------------------------------
# 🔹 Run Application
# ------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
