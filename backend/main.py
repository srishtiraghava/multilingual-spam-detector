from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
import librosa
import numpy as np
import os
import json
import subprocess
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, List, Any

app = FastAPI(
    title="VAULT.AI - Privacy-First AI Guardian",
    description="Protects against voice scams & deepfakes with ZK proofs",
    version="1.0.0"
)

# CORS - allow frontend (localhost:3000 or your domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000", "https://your-domain.com"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Whisper model (use "tiny" for faster demo, "base" for better accuracy)
model = whisper.load_model("base")

# ZK Verification Key (place verification_key.json next to main.py)
VERIFICATION_KEY = Path("verification_key.json")
if not VERIFICATION_KEY.exists():
    raise RuntimeError("Missing verification_key.json - run Circom/snarkjs setup first!")

# Multilingual responses (expand as needed)
RESPONSES = {
    "en": {
        "secure": "Identity confirmed. Secure ZK-Vault opened for transaction.",
        "danger": "Warning: High fraud risk detected. Vault locked. Do NOT proceed.",
        "deepfake": "🚨 Possible AI voice clone detected. Transaction blocked.",
        "neutral": "Analyzing voice & intent... please continue.",
        "honeypot": "Scammer detected → Honeypot mode activated (safe simulation running)."
    },
    "hi": {
        "secure": "पहचान पुष्टि हो गई। ZK-Vault सुरक्षित रूप से खुल गया है।",
        "danger": "चेतावनी: उच्च धोखाधड़ी जोखिम। वॉल्ट लॉक कर दिया गया। आगे न बढ़ें।",
        "deepfake": "🚨 AI वॉइस क्लोन संदिग्ध। लेन-देन रोका गया।",
        "neutral": "आवाज और इरादे की जांच हो रही है... बोलते रहें।",
        "honeypot": "धोखेबाज़ पकड़ा गया → Honeypot मोड चालू (सुरक्षित सिमुलेशन चल रहा है)।"
    }
    # Add more languages if Whisper detects them
}

def is_likely_deepfake(audio_path: str) -> bool:
    """Basic spectral flatness check (low = more natural voice)"""
    try:
        y, sr = librosa.load(audio_path, sr=None)
        flatness = librosa.feature.spectral_flatness(y=y).mean()
        return flatness < 0.0006  # Tune after testing real deepfakes vs humans
    except Exception:
        return False

def get_scam_risk(transcript: str) -> tuple[str, str]:
    """Keyword-based scam detection (very basic – upgrade to LLM later)"""
    keywords = ["otp", "cvv", "pin", "password", "kyc", "urgent", "bank", "lottery", "transfer", "send money"]
    score = sum(25 for kw in keywords if kw in transcript.lower())

    if score >= 75:
        return "🛑 HIGH RISK SCAM DETECTED", "Danger"
    if score >= 40:
        return "⚠️ SUSPICIOUS ACTIVITY", "High Risk"
    return "✅ SAFE", "Secure"

class ZKVerifyRequest(BaseModel):
    proof: Dict[str, Any]          # Groth16 proof object
    public: List[str]              # Public signals (e.g. ["expectedHash"])

@app.post("/api/verify-zk")
async def verify_zk_proof(req: ZKVerifyRequest):
    """ZK-Vault: Verify Groth16 proof without seeing private data"""
    try:
        temp_dir = Path("temp_zk")
        temp_dir.mkdir(exist_ok=True)

        proof_p = temp_dir / "proof.json"
        pub_p = temp_dir / "public.json"

        with open(proof_p, "w") as f:
            json.dump(req.proof, f)
        with open(pub_p, "w") as f:
            json.dump(req.public, f)

        cmd = [
            "snarkjs", "groth16", "verify",
            str(VERIFICATION_KEY),
            str(pub_p),
            str(proof_p)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=12)

        output = (result.stdout + result.stderr).lower()
        valid = result.returncode == 0 and ("ok" in output or "true" in output)

        return {
            "valid": valid,
            "message": "ZK Proof VALID → Identity verified privately" if valid else "Invalid proof",
            "details": output.strip()[:200]  # truncate for response
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(500, "ZK verification timeout")
    except Exception as e:
        raise HTTPException(500, f"ZK error: {str(e)}")
    finally:
        for p in [proof_p, pub_p]:
            if p.exists():
                p.unlink(missing_ok=True)

@app.post("/api/verify-call")
async def verify_voice_call(file: UploadFile = File(...)):
    """Main security endpoint: voice → transcription → analysis → AI response"""
    if not file.content_type.startswith("audio/"):
        raise HTTPException(400, "Audio file required")

    temp_audio = f"temp_{file.filename}"
    try:
        with open(temp_audio, "wb") as f:
            f.write(await file.read())

        # 1. Deepfake / acoustic check
        is_deepfake = is_likely_deepfake(temp_audio)

        # 2. Transcription + lang detection
        result = model.transcribe(temp_audio, language=None)  # auto-detect
        transcript = result["text"].strip()
        lang = result.get("language", "en")

        # 3. Scam/intent analysis
        if is_deepfake:
            label, status = "🚨 POSSIBLE DEEPFAKE", "Danger"
        else:
            label, status = get_scam_risk(transcript)

        # Honeypot mode simulation (for high risk)
        honeypot_active = status in ("Danger", "High Risk")

        # 4. Choose response
        lang_key = lang if lang in RESPONSES else "en"
        resp_key = "honeypot" if honeypot_active else (
            "deepfake" if is_deepfake else
            "danger" if status == "Danger" else
            "secure" if status == "Secure" else "neutral"
        )
        ai_reply = RESPONSES[lang_key].get(resp_key, RESPONSES["en"]["neutral"])

        return {
            "transcript": transcript,
            "language": lang.upper(),
            "deepfake_detected": is_deepfake,
            "security_label": label,
            "status": status,
            "ai_response": ai_reply,
            "honeypot_mode": honeypot_active,
            "security_score": 85 if status == "Secure" else 30 if status == "High Risk" else 10,  # fake score for UI
            "zk_proof_needed": status in ("Danger", "High Risk")  # frontend can trigger ZK input
        }

    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

@app.get("/api/health")
async def health_check():
    return {"status": "VAULT.AI online", "whisper": model.device}

# For frontend chat-like flow (optional websocket later)
@app.get("/")
async def root():
    return {
        "message": "VAULT.AI Backend Running",
        "endpoints": {
            "/api/verify-call": "POST audio file → get scam/deepfake analysis",
            "/api/verify-zk": "POST proof + public → verify identity privately",
            "/docs": "Swagger UI for testing"
        }
    }