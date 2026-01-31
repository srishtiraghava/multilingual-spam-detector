import VoiceProcessor from "@/components/VoiceProcessor";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <header className="text-center mb-10">
          <h1 className="text-4xl font-black text-gray-900 mb-2 tracking-tight">
            BHASHINI <span className="text-blue-600">AI</span>
          </h1>
          <p className="text-gray-500 font-medium">India AI Impact Buildathon Prototype</p>
        </header>
        
        <VoiceProcessor />
        
        <footer className="mt-8 text-center text-gray-400 text-xs">
          Built for MAIT Incubation Centre • February 2026
        </footer>
      </div>
    </div>
  );
}