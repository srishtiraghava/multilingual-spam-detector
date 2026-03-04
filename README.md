🛡️ VAULT.AI: Beyond Truecaller
A Privacy-First, Multilingual AI Guardian for Secure Voice Transactions.

🚀 The Vision
In an era of AI voice clones and sophisticated multilingual scams, traditional caller ID is no longer enough. VAULT.AI is a proactive security engine that uses Acoustic DNA, Real-time Intent Analysis, and Zero-Knowledge Proofs (ZK-Snarks) to protect users from financial fraud while keeping their data 100% private.

✨ Key Features
🎙️ Vocal DNA Check: Analyzes spectral flatness and frequency jitter to detect AI-generated deepfakes in real-time.

🌍 Multilingual Intent Analysis: Powered by OpenAI Whisper, detecting scams in English, Hindi, and beyond.

🤖 Agentic Security Brain: An autonomous AI agent that switches to "Honeypot Mode" when it detects a scammer, protecting the user.

🔒 ZK-Vault (Privacy Shield): Uses Groth16 ZK-Snarks to verify banking or identity details without the server ever seeing the raw digits.

📑 Audit Ledger: A live cryptographic console showing real-time security scores and proof hashes.

🛠️ Tech Stack
Frontend: Next.js 14, Tailwind CSS, Lucide Icons.

Backend: FastAPI (Python), Uvicorn.

AI/ML: OpenAI Whisper (Transcription/Language Detection), Librosa (Acoustic Feature Extraction).

Cryptography: Simulated Groth16 ZK-Protocol (Circom/SnarkJS Architecture).

🏗️ Architecture: How it Works
Audio Ingest: The user records a voice segment via the browser.

Security Gatekeeper: The FastAPI backend runs a dual check:

Acoustic: Is this a human or a bot?

Linguistic: Are they asking for an OTP, PIN, or urgent transfer?

Autonomous Response: The AI Agent generates a response in the user's detected language.

The Private Handshake: If a payment is requested, the ZK-Vault activates. The user inputs their ID, the browser generates a mathematical proof (Hash), and the server verifies it without storing the secret.

🚀 Getting Started
1. Backend Setup
Bash
cd backend
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload
2. Frontend Setup
Bash
cd frontend
npm install
npm run dev
Open http://localhost:3000 to view the dashboard.

🏆 Hackathon "Mouth-Opening" Demo Steps
Scam Detection: Say "Give me your bank OTP now" in English—watch the UI turn RED.

Multilingual: Say "मुझे पेमेंट करनी है" (I want to pay) in Hindi—watch the AI reply in Hindi.

The ZK-Proof: Enter an account number, click PROVE, and show the judges the ZK_Proof_Data panel on the right. Explain: "The math stayed in the browser; the server only saw the proof."

👨‍💻 Team
Sris
hti - Lead Developer & AI Architect
