import os
import whisper
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil

app = FastAPI()

# Enable CORS for your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the AI model once when the server starts
# 'base' is good for speed; use 'small' or 'medium' for better Hindi accuracy
print("Loading Indic-AI Model (Whisper)... Please wait.")
model = whisper.load_model("base")
print("Model Loaded Successfully!")

@app.post("/api/process-speech")
async def process_speech(file: UploadFile = File(...), language: str = Form(...)):
    # 1. Save the uploaded audio chunk to a temporary file
    temp_filename = f"temp_{file.filename}.wav"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Run Whisper Transcription
        # We tell it the language to improve accuracy
        print(f"Transcribing {language} audio...")
        result = model.transcribe(temp_filename, language=language)
        
        transcript = result["text"]
        print(f"Transcript: {transcript}")

        return {
            "status": "success",
            "dummy_transcript": transcript,
            "detected_language": language
        }

    except Exception as e:
        print(f"Error during transcription: {e}")
        return {"status": "error", "dummy_transcript": "Error processing audio locally."}
    
    finally:
        # 3. Clean up the temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)