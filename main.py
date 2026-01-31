import base64
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PASTE YOUR CREDENTIALS HERE ONCE APPROVED ---
USER_ID = "your_user_id_here"
API_KEY = "your_api_key_here"
PIPELINE_ID = "64392f96daac500b55c543cd" 
# ------------------------------------------------

@app.post("/api/process-speech")
async def process_speech(file: UploadFile = File(...), language: str = Form(...)):
    audio_bytes = await file.read()
    
    # 1. Convert audio to Base64 (Bhashini requires this)
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

    # 2. Setup the Bhashini Handshake (Config Phase)
    config_url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
    config_payload = {
        "pipelineTasks": [
            {"taskType": "asr", "config": {"language": {"sourceLanguage": language}}}
        ],
        "pipelineRequestConfig": {"pipelineId": PIPELINE_ID}
    }
    config_headers = {"userID": USER_ID, "ulcaApiKey": API_KEY}

    try:
        # Step A: Get the Inference URL and Key
        config_res = requests.post(config_url, json=config_payload, headers=config_headers).json()
        
        callback_url = config_res['pipelineInferenceAPIEndPoint']['callbackUrl']
        inf_key_name = config_res['pipelineInferenceAPIEndPoint']['inferenceApiKey']['name']
        inf_key_val = config_res['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value']

        # Step B: Send the actual Audio for Transcription
        compute_payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr", 
                    "config": config_res['pipelineResponseConfig'][0]['config'][0]
                }
            ],
            "inputData": {"audio": [{"audioContent": audio_b64}]}
        }
        
        compute_headers = {inf_key_name: inf_key_val}
        compute_res = requests.post(callback_url, json=compute_payload, headers=compute_headers).json()
        
        # Extract the text
        transcript = compute_res['pipelineResponseTimeline'][0]['output'][0]['source']
        
        return {"status": "success", "dummy_transcript": transcript}

    except Exception as e:
        print(f"Bhashini Error: {e}")
        return {"status": "error", "dummy_transcript": "Error contacting Bhashini. Check your keys!"}