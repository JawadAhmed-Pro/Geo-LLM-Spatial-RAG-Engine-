"use client";

import { MapPin, Info, Navigation, Droplets } from "lucide-react";

interface Feature {
  id: string | number;
  properties: {
    name?: string;
    name_ur?: string;
    amenity?: string;
    [key: string]: any;
  };
}

interface ResultsPanelProps {
  geojson: any | null;
  stats: any | null;
}

export default function ResultsPanel({ geojson, stats }: ResultsPanelProps) {
  const features: Feature[] = geojson?.features || [];

  return (
    <div className="flex flex-col h-full bg-neutral-950 border-r border-neutral-800 w-[350px] shadow-2xl">
      {/* Header / Stats */}
      <div className="p-6 border-b border-neutral-800 bg-neutral-900/50">
        <h2 className="text-xs font-bold uppercase tracking-widest text-neutral-500 mb-4">Spatial Intelligence</h2>
        
        {stats ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-400">Total Found</span>
              <span className="text-xl font-bold text-emerald-400">{stats.count || 0}</span>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(stats.amenity_breakdown || {}).map(([type, count]: [string, any]) => (
                <div key={type} className="bg-neutral-800/50 p-2 rounded-lg border border-neutral-700/50">
                  <div className="text-[10px] uppercase text-neutral-500 font-bold leading-tight">{type}</div>
                  <div className="text-sm font-bold text-neutral-200">{count}</div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="py-8 text-center text-sm text-neutral-600 italic">
            Waiting for query...
          </div>
        )}
      </div>

      {/* Results List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
        {features.length > 0 ? (
          features.map((f, i) => (
            <div 
              key={i} 
              className="glass-card p-4 rounded-xl cursor-pointer group"
              onClick={() => {
                // Future: Add zoom logic here via event bus or prop
              }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse-slow"></span>
                    <h3 className="text-sm font-bold text-neutral-200 group-hover:text-emerald-400 transition-colors">
                      {f.properties.name || "Unnamed Location"}
                    </h3>
                  </div>
                  {f.properties.name_ur && (
                    <div className="text-xs text-emerald-500/80 mb-2 font-medium" dir="rtl">
                      {f.properties.name_ur}
                    </div>
                  )}
                  <div className="text-[10px] text-neutral-500 flex items-center space-x-3">
                    <span className="flex items-center"><MapPin className="w-3 h-3 mr-1" /> {f.properties.amenity || "Point"}</span>
                  </div>
                </div>
                <div className="bg-neutral-800 p-1.5 rounded-lg border border-neutral-700 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Navigation className="w-3 h-3 text-emerald-400" />
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-neutral-700 space-y-2 opacity-50">
             <Info className="w-8 h-8" />
             <p className="text-xs">No active results</p>
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-4 bg-neutral-900/80 border-t border-neutral-800 flex items-center justify-between text-[10px] font-bold text-neutral-500 uppercase tracking-tighter">
        <span>Region: Swat</span>
        <span className="flex items-center"><Droplets className="w-3 h-3 mr-1 text-blue-500" /> STABLE</span>
      </div>
    </div>
  );
}
