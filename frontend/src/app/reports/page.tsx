"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import type { WeeklyReport } from "@/lib/types";

export default function ReportsPage() {
  const [reports, setReports] = useState<WeeklyReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadReports() {
      try {
        const res = await apiClient.getReports(1, 10);
        setReports(res.data.data || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }
    loadReports();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Developer DNA Reports</h1>
        <p className="text-slate-400">Your weekly and monthly coding narratives.</p>
      </div>
      
      {loading ? (
        <p className="text-slate-500 p-6">Loading reports...</p>
      ) : reports.length === 0 ? (
        <p className="text-slate-500 p-6 rounded-2xl bg-slate-900/50 border border-white/10">
          No reports generated yet.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {reports.map((report) => (
            <div key={report.id} className="p-6 rounded-2xl bg-gradient-to-br from-indigo-900/40 to-purple-900/40 border border-indigo-500/20 backdrop-blur-md transition-all hover:scale-[1.02] cursor-pointer">
              <div className="text-sm font-medium text-indigo-300 mb-2">
                {new Date(report.weekStart).toLocaleDateString()}
              </div>
              <h3 className="text-xl font-bold text-white mb-4">
                Weekly Report
              </h3>
              <p className="text-sm text-indigo-200/70">
                {report.summary || "A deep dive into your week."}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
