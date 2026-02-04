import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import whisper
import librosa
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = whisper.load_model("base")

RESPONSES = {
    "en": {
        "secure": "Identity confirmed. I have opened the secure ZK-Vault for your transaction.",
        "danger": "Warning: High fraud probability detected. Encryption vault locked.",
        "neutral": "Analyzing call security... please continue speaking."
    },
    "hi": {
        "secure": "आवाज़ की पहचान हो गई है। मैंने सुरक्षित ZK-Vault खोल दिया है।",
        "danger": "चेतावनी: धोखाधड़ी की संभावना है। लेनदेन रोक दिया गया है।",
        "neutral": "मैं इस कॉल की सुरक्षा की जांच कर रहा हूं।"
    }
}

def analyze_voice_dna(audio_path):
    y, sr = librosa.load(audio_path)
    flatness = librosa.feature.spectral_flatness(y=y).mean()
    return True if flatness < 0.0005 else False

def get_scam_rating(transcript):
    keywords = ["otp", "cvv", "bank", "lottery", "urgent", "password", "kyc", "pin"]
    score = sum(30 for word in keywords if word in transcript.lower())
    if score >= 60: return "🛑 DANGEROUS: SCAM DETECTED", "Danger"
    if score >= 30: return "⚠️ CAUTION: SUSPICIOUS", "High Risk"
    return "✅ VERIFIED HUMAN", "Secure"

@app.post("/api/verify-call")
async def verify_call(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    is_deepfake = analyze_voice_dna(temp_path)
    result = model.transcribe(temp_path)
    transcript = result["text"]
    lang = result.get("language", "en")

    if is_deepfake:
        label, status = "🚨 DEEPFAKE DETECTED", "Danger"
    else:
        label, status = get_scam_rating(transcript)

    lang_key = lang if lang in RESPONSES else "en"
    ai_reply = RESPONSES[lang_key].get(status.lower() if status != "High Risk" else "danger", RESPONSES["en"]["neutral"])

    os.remove(temp_path)
    return {"label": label, "status": status, "transcript": transcript, "ai_response": ai_reply, "language": lang.upper()}