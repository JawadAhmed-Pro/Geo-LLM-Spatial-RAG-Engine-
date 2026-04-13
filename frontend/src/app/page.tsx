"use client";

import { useState } from "react";
import ChatPanel from "@/components/ChatPanel";
import ResultsPanel from "@/components/ResultsPanel";
import dynamic from "next/dynamic";
import { LayoutDashboard,Layers, History, Settings, Database } from "lucide-react";

const MapCanvas = dynamic(() => import("@/components/MapCanvas"), { 
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center bg-neutral-900 text-neutral-500">Loading Map...</div>
});

export default function Home() {
  const [geoData, setGeoData] = useState<any | null>(null);
  const [stats, setStats] = useState<any | null>(null);

  const handleDataReceived = (data: any, stats: any) => {
    setGeoData(data);
    setStats(stats);
  };

  return (
    <main className="flex h-screen w-full bg-neutral-950 overflow-hidden">
      {/* 1. Global Navigation (Nav Sidebar) */}
      <nav className="w-16 h-full flex flex-col items-center py-6 bg-neutral-950 border-r border-neutral-900 space-y-8 z-20">
        <div className="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-900/40">
           <Database className="w-6 h-6 text-white" />
        </div>
        
        <div className="flex-1 flex flex-col space-y-4">
          <button className="p-3 text-emerald-400 bg-emerald-500/10 rounded-xl"><LayoutDashboard className="w-5 h-5" /></button>
          <button className="p-3 text-neutral-500 hover:text-neutral-200 transition-colors"><Layers className="w-5 h-5" /></button>
          <button className="p-3 text-neutral-500 hover:text-neutral-200 transition-colors"><History className="w-5 h-5" /></button>
        </div>

        <button className="p-3 text-neutral-500 hover:text-neutral-200 transition-colors"><Settings className="w-5 h-5" /></button>
      </nav>

      {/* 2. Control Center (Chat) */}
      <section className="w-1/4 min-w-[350px] h-full flex flex-col glass-container z-10 relative">
         <ChatPanel onDataReceived={handleDataReceived} />
      </section>

      {/* 3. Results Panel (Intelligence) */}
      <section className="h-full z-10">
         <ResultsPanel geojson={geoData} stats={stats} />
      </section>

      {/* 4. The Action Plane (Map Hero) */}
      <section className="flex-1 h-full relative">
         <MapCanvas geojson={geoData} />
         
         {/* Map Overlays */}
         <div className="absolute top-6 left-6 z-20 pointer-events-none">
            <div className="glass-container px-4 py-2 rounded-full flex items-center space-x-2 emerald-glow border border-emerald-500/30">
               <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
               <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-100">Regional Pulse: Swat Valley</span>
            </div>
         </div>
      </section>
    </main>
  );
}
