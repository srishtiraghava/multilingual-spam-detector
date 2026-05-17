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

# -----------------------------
# FastAPI App
# -----------------------------

app = FastAPI(
    title="VAULT.AI - Privacy-First AI Guardian",
    description="Protects against voice scams & deepfakes with ZK proofs",
    version="1.0.0"
)

# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Whisper Model
# -----------------------------
# Use tiny model for Render free tier

print("Loading Whisper model...")

model = whisper.load_model("tiny")

print("Whisper model loaded successfully.")

# -----------------------------
# ZK Verification Setup
# -----------------------------

VERIFICATION_KEY = Path("verification_key.json")

ZK_ENABLED = VERIFICATION_KEY.exists()

if not ZK_ENABLED:
    print("⚠️ verification_key.json not found → ZK mode disabled")

# -----------------------------
# Multilingual Responses
# -----------------------------

RESPONSES = {
    "en": {
        "secure": "Identity confirmed. Secure ZK-Vault opened for transaction.",
        "danger": "Warning: High fraud risk detected. Vault locked. Do NOT proceed.",
        "deepfake": "Possible AI voice clone detected. Transaction blocked.",
        "neutral": "Analyzing voice & intent... please continue.",
        "honeypot": "Scammer detected → Honeypot mode activated."
    },

    "hi": {
        "secure": "पहचान पुष्टि हो गई। ZK-Vault सुरक्षित रूप से खुल गया है।",

        "danger": "चेतावनी: उच्च धोखाधड़ी जोखिम। आगे न बढ़ें।",

        "deepfake": "AI वॉइस क्लोन संदिग्ध। लेन-देन रोका गया।",

        "neutral": "आवाज और इरादे की जांच हो रही है...",

        "honeypot": "धोखेबाज़ पकड़ा गया → Honeypot मोड चालू।"
    }
}

# -----------------------------
# Deepfake Detection
# -----------------------------

def is_likely_deepfake(audio_path: str) -> bool:
    try:
        y, sr = librosa.load(audio_path, sr=None)

        flatness = librosa.feature.spectral_flatness(y=y).mean()

        return flatness < 0.0006

    except Exception as e:
        print("Deepfake detection error:", e)
        return False

# -----------------------------
# Scam Detection
# -----------------------------

def get_scam_risk(transcript: str):

    keywords = [
        "otp",
        "cvv",
        "pin",
        "password",
        "kyc",
        "urgent",
        "bank",
        "lottery",
        "transfer",
        "send money"
    ]

    score = sum(
        25 for kw in keywords if kw in transcript.lower()
    )

    if score >= 75:
        return "HIGH RISK SCAM DETECTED", "Danger"

    if score >= 40:
        return "SUSPICIOUS ACTIVITY", "High Risk"

    return "SAFE", "Secure"

# -----------------------------
# ZK Request Model
# -----------------------------

class ZKVerifyRequest(BaseModel):
    proof: Dict[str, Any]
    public: List[str]

# -----------------------------
# ZK Verification API
# -----------------------------

@app.post("/api/verify-zk")
async def verify_zk_proof(req: ZKVerifyRequest):

    if not ZK_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="ZK verification temporarily disabled"
        )

    temp_dir = Path("temp_zk")
    temp_dir.mkdir(exist_ok=True)

    proof_p = temp_dir / "proof.json"
    pub_p = temp_dir / "public.json"

    try:

        with open(proof_p, "w") as f:
            json.dump(req.proof, f)

        with open(pub_p, "w") as f:
            json.dump(req.public, f)

        cmd = [
            "snarkjs",
            "groth16",
            "verify",
            str(VERIFICATION_KEY),
            str(pub_p),
            str(proof_p)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=12
        )

        output = (result.stdout + result.stderr).lower()

        valid = (
            result.returncode == 0 and
            ("ok" in output or "true" in output)
        )

        return {
            "valid": valid,
            "message": (
                "ZK Proof VALID → Identity verified privately"
                if valid
                else "Invalid proof"
            ),
            "details": output[:200]
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(500, "ZK verification timeout")

    except Exception as e:
        raise HTTPException(500, f"ZK error: {str(e)}")

    finally:

        if proof_p.exists():
            proof_p.unlink(missing_ok=True)

        if pub_p.exists():
            pub_p.unlink(missing_ok=True)

# -----------------------------
# Main Voice Verification API
# -----------------------------

@app.post("/api/verify-call")
async def verify_voice_call(
    file: UploadFile = File(...)
):

    if not file.content_type.startswith("audio/"):
        raise HTTPException(400, "Audio file required")

    temp_audio = f"temp_{file.filename}"

    try:

        with open(temp_audio, "wb") as f:
            f.write(await file.read())

        # -------------------------
        # Deepfake Detection
        # -------------------------

        is_deepfake = is_likely_deepfake(temp_audio)

        # -------------------------
        # Whisper Transcription
        # -------------------------

        result = model.transcribe(
            temp_audio,
            language=None
        )

        transcript = result["text"].strip()

        lang = result.get("language", "en")

        # -------------------------
        # Scam Detection
        # -------------------------

        if is_deepfake:
            label = "POSSIBLE DEEPFAKE"
            status = "Danger"

        else:
            label, status = get_scam_risk(transcript)

        # -------------------------
        # Honeypot Logic
        # -------------------------

        honeypot_active = status in [
            "Danger",
            "High Risk"
        ]

        # -------------------------
        # AI Response Selection
        # -------------------------

        lang_key = (
            lang if lang in RESPONSES else "en"
        )

        resp_key = (
            "honeypot"
            if honeypot_active
            else (
                "deepfake"
                if is_deepfake
                else (
                    "danger"
                    if status == "Danger"
                    else (
                        "secure"
                        if status == "Secure"
                        else "neutral"
                    )
                )
            )
        )

        ai_reply = RESPONSES[lang_key].get(
            resp_key,
            RESPONSES["en"]["neutral"]
        )

        # -------------------------
        # Final Response
        # -------------------------

        return {

            "transcript": transcript,

            "language": lang.upper(),

            "deepfake_detected": is_deepfake,

            "security_label": label,

            "status": status,

            "ai_response": ai_reply,

            "honeypot_mode": honeypot_active,

            "security_score": (
                85
                if status == "Secure"
                else 30
                if status == "High Risk"
                else 10
            ),

            "zk_proof_needed": (
                status in ["Danger", "High Risk"]
            )
        }

    except Exception as e:

        print("Verification error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(temp_audio):
            os.remove(temp_audio)

# -----------------------------
# Health Check
# -----------------------------

@app.get("/api/health")
async def health_check():

    return {
        "status": "VAULT.AI online",
        "whisper_model": "tiny",
        "zk_enabled": ZK_ENABLED
    }

# -----------------------------
# Root Endpoint
# -----------------------------

@app.get("/")
async def root():

    return {

        "message": "VAULT.AI Backend Running",

        "status": "online",

        "features": [
            "Deepfake Detection",
            "Multilingual Scam Detection",
            "Whisper AI",
            "Honeypot Mode",
            "ZK Verification"
        ],

        "endpoints": {

            "/api/verify-call":
            "POST audio file",

            "/api/verify-zk":
            "POST zk proof",

            "/api/health":
            "Health check",

            "/docs":
            "Swagger UI"
        }
    }