import os
import base64
import shutil
from typing import Dict, Any, Optional
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (needed for the API key check)
load_dotenv()

# --- Configuration ---
# Directory where inputs will be saved (create if it doesn't exist)
SAVE_DIR = os.path.join(os.path.dirname(__file__), 'received_inputs_json')
os.makedirs(SAVE_DIR, exist_ok=True)
print(f"Inputs will be saved to: {SAVE_DIR}")

# --- Security Configuration ---
def get_lovable_secret_key() -> str:
    """Retrieves the expected Bearer token from environment variables."""
    # Use your generated key (zwOq9ZzL9I9_8eK3BVvFNXtWduwq9CVV_1sJ2jAa3QE)
    return os.getenv("LOVABLE_SECRET_KEY", "zwOq9ZzL9I9_8eK3BVvFNXtWduwq9CVV_1sJ2jAa3QE") 

# --- Pydantic Model (Matches the Deno Script's ExportPayload) ---
class ResumeDetails(BaseModel):
    fileName: str
    fileSize: int
    content: str  # This holds the Base64 encoded PDF

class ExportPayload(BaseModel):
    resume: ResumeDetails
    jobDescription: str
    timestamp: Optional[str] = None

# --- Application Setup ---
app = FastAPI(title="Lovable JSON Receiver")

# --- Security Dependency ---
def verify_authorization_header(authorization: Optional[str] = Header(None)) -> bool:
    """Checks for 'Authorization: Bearer <KEY>' header."""
    ACTUAL_KEY = get_lovable_secret_key()
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header or Bearer token format.")
    
    token = authorization.split(" ")[1]
    if token != ACTUAL_KEY:
        raise HTTPException(status_code=401, detail="Invalid Bearer Token.")
    
    return True

# --- Main Endpoint ---

@app.post("/receive-inputs")
async def receive_inputs_test(
    payload: ExportPayload,  # Receives JSON body
    # FastAPI automatically runs this check, using the 'Authorization' header
    verified: bool = Depends(verify_authorization_header), 
) -> Dict[str, Any]:
    """
    Receives JSON payload with Base64 PDF, decodes, saves, and confirms success.
    """
    
    resume_file_name = payload.resume.fileName
    resume_content_b64 = payload.resume.content
    job_description_text = payload.jobDescription

    # 1. Base64 Decode the PDF Content
    try:
        pdf_bytes = base64.b64decode(resume_content_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode Base64 resume content.")

    # 2. Save Job Description to a .txt file
    jd_filename = os.path.join(SAVE_DIR, "job_description_received.txt")
    with open(jd_filename, 'w', encoding='utf-8') as f:
        f.write(job_description_text)

    # 3. Save Resume PDF file locally
    resume_filename = os.path.join(SAVE_DIR, resume_file_name)
    with open(resume_filename, "wb") as buffer:
        buffer.write(pdf_bytes)
    
    # 4. Success Confirmation
    return {
        "status": "success",
        "message": "Inputs received and saved successfully!",
        "saved_pdf": resume_filename,
        "saved_description": jd_filename
    }

@app.get("/health")
def healthcheck() -> Dict[str, str]:
    """Simple probe for uptime monitoring."""
    return {"status": "ok"}
