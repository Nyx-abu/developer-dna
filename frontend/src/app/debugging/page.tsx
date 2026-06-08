"use client";

import React, { useEffect, useState } from "react";
import { ErrorDistributionChart } from "@/components/charts/ErrorDistributionChart";
import { apiClient } from "@/lib/api";
import type { ErrorEvent } from "@/lib/types";

export default function DebuggingPage() {
  const [errors, setErrors] = useState<ErrorEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadErrors() {
      try {
        const res = await apiClient.getErrors(1, 50);
        setErrors(res.data.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadErrors();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Debugging Analytics</h1>
        <p className="text-slate-400">Insights into error patterns and resolution efficiency.</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
          <h3 className="text-lg font-semibold mb-4">Error Distribution</h3>
          {loading ? (
            <div className="h-[300px] flex items-center justify-center text-slate-500">Loading Chart...</div>
          ) : (
            <ErrorDistributionChart errors={errors} />
          )}
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
          <h3 className="text-lg font-semibold mb-4">Recent Errors</h3>
          {loading ? (
            <p className="text-slate-500">Loading errors...</p>
          ) : errors.length === 0 ? (
            <p className="text-slate-500">No errors recorded yet.</p>
          ) : (
            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2">
              {errors.slice(0, 10).map((e) => (
                <div key={e.id} className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-sm">
                  <div className="flex justify-between mb-1">
                    <span className="font-semibold text-red-400">{e.errorType}</span>
                    <span className="text-slate-500">{new Date(e.timestamp).toLocaleDateString()}</span>
                  </div>
                  <div className="text-slate-300 font-mono text-xs mb-2 truncate" title={e.filePath}>
                    {e.filePath}:{e.lineNumber}
                  </div>
                  <div className="text-slate-400 truncate" title={e.message}>
                    {e.message}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
