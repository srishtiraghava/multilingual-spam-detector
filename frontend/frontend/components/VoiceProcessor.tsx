"use client";
import { useState, useRef } from "react";

export default function VoiceProcessor() {
  const [status, setStatus] = useState<string>("Idle");
  const [transcript, setTranscript] = useState<string>("");
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const [lang, setLang] = useState<string>("hi");

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Note: Some browsers prefer audio/webm; Whisper can handle most formats
      mediaRecorder.current = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      mediaRecorder.current.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      mediaRecorder.current.onstop = async () => {
        setStatus("AI is thinking...");
        const audioBlob = new Blob(chunks, { type: "audio/wav" });
        
        const formData = new FormData();
        formData.append("file", audioBlob, "recording.wav");
        formData.append("language", lang);

        try {
          const response = await fetch("http://127.0.0.1:8000/api/process-speech", {
            method: "POST",
            body: formData,
          });
          const data = await response.json();
          setTranscript(data.dummy_transcript);
          setStatus("Done");
        } catch (error) {
          console.error("Backend Error:", error);
          setStatus("Check Backend Server");
        }
      };

      mediaRecorder.current.start();
      setStatus("Recording...");
    } catch (err) {
      console.error("Mic Error:", err);
      setStatus("Mic Access Denied");
    }
  };

  return (
    <div className="p-8 bg-white shadow-2xl rounded-3xl flex flex-col items-center gap-6 border border-gray-100">
      <div className="w-full">
        <label className="block text-sm font-semibold text-gray-600 mb-2 text-center italic">
          Select Your Regional Language
        </label>
        <select 
          value={lang} 
          onChange={(e) => setLang(e.target.value)}
          className="border border-gray-200 p-3 rounded-xl w-full text-center font-bold bg-gray-50"
        >
          <option value="hi">Hindi (हिन्दी)</option>
          <option value="ta">Tamil (தமிழ்)</option>
          <option value="te">Telugu (తెలుగు)</option>
          <option value="ml">Malayalam (മലയാളം)</option>
          <option value="en">English</option>
        </select>
      </div>

      <button 
        onClick={status === "Recording..." ? () => mediaRecorder.current?.stop() : startRecording}
        className={`w-32 h-32 rounded-full flex flex-col items-center justify-center transition-all duration-300 shadow-xl ${
          status === "Recording..." ? "bg-red-500 scale-110 animate-pulse" : "bg-blue-600 hover:bg-blue-700"
        } text-white`}
      >
        <span className="text-4xl">{status === "Recording..." ? "🛑" : "🎤"}</span>
        <span className="text-xs font-bold mt-1 uppercase">{status === "Recording..." ? "Stop" : "Speak"}</span>
      </button>

      <div className="text-center">
        <p className="text-sm font-bold text-gray-400 uppercase tracking-tighter">Status</p>
        <p className="text-blue-600 font-black">{status}</p>
      </div>

      <div className="w-full bg-gray-50 p-6 rounded-2xl border-2 border-dashed border-gray-200">
        <p className="text-gray-700 leading-relaxed font-medium italic">
          {transcript || "The AI will show your speech here..."}
        </p>
      </div>
    </div>
  );
}