"use client";

import React, { useEffect, useState } from "react";
import { ActivityHeatmap } from "@/components/charts/ActivityHeatmap";
import { apiClient } from "@/lib/api";
import type { CodingSession } from "@/lib/types";

export default function ActivityPage() {
  const [sessions, setSessions] = useState<CodingSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSessions() {
      try {
        const res = await apiClient.getSessions(1, 20);
        setSessions(res.data.data || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    loadSessions();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Activity Timeline</h1>
        <p className="text-slate-400">Detailed breakdown of your coding sessions and events.</p>
      </div>
      
      <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
        <h3 className="text-lg font-semibold mb-4">Contribution Heatmap</h3>
        <ActivityHeatmap />
      </div>

      <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
        <h3 className="text-lg font-semibold mb-4">Recent Sessions</h3>
        {loading ? (
          <p className="text-slate-500">Loading sessions...</p>
        ) : sessions.length === 0 ? (
          <p className="text-slate-500">No activity recorded yet.</p>
        ) : (
          <div className="space-y-4">
            {sessions.map(s => (
              <div key={s.id} className="p-4 rounded-lg bg-slate-800/50 border border-slate-700/50 flex justify-between items-center">
                <div>
                  <div className="font-medium text-slate-200">
                    {new Date(s.startTime).toLocaleDateString()} at {new Date(s.startTime).toLocaleTimeString()}
                  </div>
                  <div className="text-sm text-slate-400">
                    {s.editor} • {Math.round(s.durationMinutes || 0)} minutes
                  </div>
                </div>
                {s.isActive && (
                  <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full border border-green-500/30">
                    Active
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
