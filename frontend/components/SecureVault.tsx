"use client";
import { useState, useRef } from "react";

export default function SecureVault() {
  const [messages, setMessages] = useState<any[]>([]);
  const [security, setSecurity] = useState({ label: "SYSTEM IDLE", status: "Neutral" });
  const [recording, setRecording] = useState(false);
  const [showVault, setShowVault] = useState(false);
  const [accountNum, setAccountNum] = useState("");
  const [zkProof, setZkProof] = useState<any>(null);
  const [isProving, setIsProving] = useState(false);
  const [ledger, setLedger] = useState<string[]>(["[SYS]: Vault.AI Kernel v4.2 Loaded", "[SYS]: ZK-Circuit Verified"]);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);

  const startAnalysis = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    const chunks: any = [];
    mediaRecorder.current.ondataavailable = (e) => chunks.push(e.data);
    
    mediaRecorder.current.onstop = async () => {
      setLedger(prev => [`[AUDIO]: Decoding Vocal DNA...`, ...prev]);
      const blob = new Blob(chunks, { type: "audio/wav" });
      const fd = new FormData();
      fd.append("file", blob, "audio.wav");

      const res = await fetch("http://127.0.0.1:8000/api/verify-call", { method: "POST", body: fd });
      const data = await res.json();

      setMessages(prev => [...prev, { sender: "User", text: data.transcript }]);
      setLedger(prev => [`[ANALYSIS]: ${data.label}`, `[LANG]: ${data.language} Active`, ...prev]);
      
      setTimeout(() => {
        setMessages(prev => [...prev, { sender: "VAULT_AI", text: data.ai_response, risk: data.status }]);
        if (data.status === "Secure") setShowVault(true);
      }, 800);

      setSecurity({ label: data.label, status: data.status });
    };

    mediaRecorder.current.start();
    setRecording(true);
  };

  const executeZKPayment = async () => {
    setIsProving(true);
    setZkProof(null); // Clear old proof
    setLedger(prev => [`[ZK-GEN]: Computing Groth16 Proof...`, ...prev]);
    
    await new Promise(r => setTimeout(r, 2000)); // Simulate proving time
    
    const mockHash = "0x" + [...Array(32)].map(() => Math.floor(Math.random() * 16).toString(16)).join("");
    const proofData = {
      protocol: "groth16",
      proof_hash: mockHash,
      inputs: { public_signal: "1", commitment: "0x7a2...f81" },
      pi_a: ["0x127b...44a", "0x221c...99b"]
    };

    setZkProof(proofData);
    setIsProving(false);
    setLedger(prev => [`[VAULT]: Proof Validated. Hash: ${mockHash.substring(0,10)}...`, ...prev]);
    setMessages(prev => [...prev, { sender: "System", text: "Identity Verified via ZK-Proof." }]);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center p-6 font-mono">
      <div className="relative z-10 w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-6 h-[750px]">
        
        {/* LEFT: LEDGER */}
        <div className="lg:col-span-3 bg-zinc-900/40 border border-white/5 rounded-3xl p-6 flex flex-col overflow-hidden">
          <h2 className="text-[10px] font-black text-blue-500 mb-4 tracking-widest uppercase italic">Audit_Ledger</h2>
          <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-hide">
            {ledger.map((log, i) => (
              <div key={i} className="text-[9px] opacity-60 border-l border-white/10 pl-3">{log}</div>
            ))}
          </div>
        </div>

        {/* CENTER: CHAT */}
        <div className="lg:col-span-6 bg-zinc-900/60 border border-white/10 rounded-[2.5rem] p-8 flex flex-col shadow-2xl relative">
          <header className="flex justify-between items-start mb-10">
            <h1 className="text-xl font-black italic tracking-tighter text-white">VAULT_AI <span className="text-blue-500">v4.2</span></h1>
            <div className={`px-4 py-1.5 rounded-xl text-[10px] font-bold border ${security.status === 'Secure' ? 'bg-green-500/10 border-green-500/50 text-green-400' : 'bg-zinc-800 border-zinc-700 text-zinc-400'}`}>
                {security.label}
            </div>
          </header>

          <div className="flex-1 overflow-y-auto space-y-6 mb-8 pr-4 custom-scrollbar">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.sender === 'User' ? 'justify-end' : 'justify-start'}`}>
                <div className={`p-4 rounded-3xl border ${m.sender === 'System' ? 'bg-blue-900/20 border-blue-500/40' : 'bg-zinc-800/40 border-zinc-700'}`}>
                  <p className="text-[7px] uppercase font-black opacity-40 mb-1">{m.sender}</p>
                  <p className="text-sm">{m.text}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-auto">
            {showVault ? (
              <div className="w-full bg-blue-600/10 border border-blue-500/30 p-6 rounded-3xl animate-in zoom-in-95">
                <p className="text-[9px] font-black text-blue-400 mb-4 tracking-widest uppercase">ZK-Input Shield</p>
                <div className="flex gap-2">
                  <input type="password" placeholder="Enter Private ID" className="flex-1 bg-black/50 border border-zinc-800 rounded-2xl p-4 text-sm outline-none focus:border-blue-500" value={accountNum} onChange={(e) => setAccountNum(e.target.value)} />
                  <button onClick={executeZKPayment} className="bg-blue-600 hover:bg-blue-500 px-8 rounded-2xl text-[10px] font-black uppercase transition-all">
                    {isProving ? "PROVING..." : "PROVE"}
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <button onMouseDown={startAnalysis} onMouseUp={() => { mediaRecorder.current?.stop(); setRecording(false); }} className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${recording ? 'bg-red-600 scale-110' : 'bg-blue-600'}`}>
                  {recording ? <div className="w-6 h-6 bg-white animate-pulse" /> : <span className="text-xl">🎤</span>}
                </button>
                <p className="mt-4 text-[9px] text-zinc-500 uppercase tracking-widest font-bold">Hold to Analyze Call</p>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT: ZK PROOF DATA */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <div className="flex-1 bg-zinc-900/40 border border-white/5 rounded-3xl p-6 overflow-hidden flex flex-col relative">
            <h3 className="text-[10px] font-black text-blue-500 mb-4 tracking-widest uppercase italic">ZK_Proof_Data</h3>
            <div className="flex-1 bg-black/40 rounded-2xl p-4 font-mono text-[9px] text-green-400 overflow-y-auto">
              {isProving ? (
                <div className="space-y-2 animate-pulse">
                    <div className="h-2 w-full bg-zinc-800 rounded"></div>
                    <div className="h-2 w-2/3 bg-zinc-800 rounded"></div>
                    <div className="h-2 w-full bg-zinc-800 rounded"></div>
                    <p className="text-blue-500 text-center mt-4 uppercase">Generating Mathematical Proof...</p>
                </div>
              ) : zkProof ? (
                <pre>{JSON.stringify(zkProof, null, 2)}</pre>
              ) : (
                <p className="text-zinc-700 italic">Awaiting proof computation...</p>
              )}
            </div>
            <div className="mt-4 pt-4 border-t border-white/5 text-center">
                <p className="text-[10px] text-zinc-500 mb-1 uppercase font-bold tracking-tighter">Security Score</p>
                <p className="text-3xl font-black text-white">{security.status === 'Secure' ? '9.8' : '0.0'}</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}