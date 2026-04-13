"use client";

import { useState, useRef, useEffect } from "react";
import { sendSpatialQuery, ChatResponse, getChatHistory, HistoryItem } from "@/lib/api";

interface Message {
  role: "user" | "ai";
  content: string;
  sql?: string | null;
  count?: number;
  highlights?: string[];
}

export default function ChatPanel({ onDataReceived }: { onDataReceived: (data: any, stats: any) => void }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load history on mount
  useEffect(() => {
    const loadHistory = async () => {
      const history = await getChatHistory();
      if (history.length > 0) {
        // Convert HistoryItem to internal Message format
        const formatted = history.map(h => {
          const count = h.geojson?.features?.length || 0;
          const highlights = h.geojson?.features?.slice(0, 3).map((f: any) => f.properties.name).filter(Boolean);
          return {
            role: h.role,
            content: h.content,
            sql: h.sql_query,
            count,
            highlights
          };
        });
        setMessages(formatted);

        const lastAiWithGeo = [...history].reverse().find(h => h.role === 'ai' && h.geojson);
        if (lastAiWithGeo) {
          // Re-calculate stats for history restoration
          const amenityCounts: any = {};
          lastAiWithGeo.geojson?.features?.forEach((f: any) => {
             const type = f.properties.amenity || "other";
             amenityCounts[type] = (amenityCounts[type] || 0) + 1;
          });
          onDataReceived(lastAiWithGeo.geojson, { 
            count: lastAiWithGeo.geojson?.features?.length || 0,
            amenity_breakdown: amenityCounts
          });
        }
      } else {
        setMessages([
          { role: "ai", content: "Welcome to the Geo-LLM Spatial engine. Ask me about hospitals in Swat! For example: 'Show me all hospitals in Swat'" }
        ]);
      }
    };
    loadHistory();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const response: ChatResponse = await sendSpatialQuery(userMessage);
      
      const count = response.geojson?.features?.length || 0;
      const highlights = response.geojson?.features?.slice(0, 3).map((f: any) => f.properties.name).filter(Boolean);

      setMessages(prev => [
        ...prev,
        { 
          role: "ai", 
          content: response.answer,
          sql: response.sql,
          count,
          highlights
        }
      ]);

      if (response.geojson) {
        onDataReceived(response.geojson, response.stats);
      }
    } catch (error: any) {
      setMessages(prev => [...prev, { role: "ai", content: `Error: ${error.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-neutral-950 text-neutral-200">
      <div className="p-4 border-b border-neutral-800 flex items-center justify-between">
        <h1 className="text-lg font-bold tracking-wide text-emerald-400">Spatial Engine</h1>
        <div className="flex space-x-1">
           <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        {messages.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[90%] p-4 rounded-2xl ${msg.role === 'user' ? 'bg-emerald-600/90 text-white rounded-br-none shadow-md' : 'bg-neutral-900 border border-neutral-800 text-neutral-200 rounded-bl-none shadow-2xl transition-all hover:border-emerald-500/30'}`}>
              <p className="text-sm leading-relaxed">{msg.content}</p>
              
              {msg.role === 'ai' && msg.count !== undefined && msg.count > 0 && (
                <div className="mt-3 pt-3 border-t border-neutral-800">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded-full uppercase tracking-tighter">
                      {msg.count} Locations Found
                    </span>
                  </div>
                  {msg.highlights && msg.highlights.length > 0 && (
                    <ul className="text-[11px] text-neutral-400 space-y-1">
                      {msg.highlights.map((name, idx) => (
                        <li key={idx} className="flex items-center">
                          <span className="w-1 h-1 bg-emerald-500 rounded-full mr-2"></span>
                          {name}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
            
            {msg.sql && (
              <details className="mt-2 w-full group px-2">
                <summary className="text-[10px] uppercase font-bold text-neutral-600 cursor-pointer hover:text-emerald-500 transition-colors list-none flex items-center">
                  <span className="mr-1 opacity-50 group-open:rotate-90 transition-transform">▶</span>
                  Technical Details
                </summary>
                <div className="mt-2 text-[11px] font-mono bg-black/40 text-emerald-500/70 p-3 rounded-xl border border-emerald-900/20 overflow-x-auto whitespace-pre-wrap">
                  {msg.sql}
                </div>
              </details>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex flex-col items-start">
            <div className="max-w-[80%] p-4 rounded-2xl bg-neutral-800/80 rounded-bl-none flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '300ms' }} />
              <span className="text-sm text-neutral-400 ml-2">Generating PostGIS SQL...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 bg-neutral-950 border-t border-neutral-800">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            className="flex-1 bg-neutral-900 border border-neutral-700 text-neutral-100 placeholder-neutral-500 text-sm rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-transparent transition-all"
            placeholder="Ask about spatial data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl px-4 py-2 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-900/20"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
