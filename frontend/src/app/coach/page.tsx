"use client";

import React, { useEffect, useState } from "react";
import { Bot, Lightbulb } from "lucide-react";
import { apiClient } from "@/lib/api";
import type { AIInsight } from "@/lib/types";

export default function CoachPage() {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await apiClient.getInsights();
        // Show all actionable insights here
        setInsights(res.data.filter(i => i.actionable));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
          <Bot className="w-7 h-7 text-blue-400" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Career Coach</h1>
          <p className="text-slate-400">Personalized actionable recommendations for your growth.</p>
        </div>
      </div>
      
      <div className="space-y-6">
        {loading ? (
          <p className="text-slate-500 p-6">Consulting the AI Coach...</p>
        ) : insights.length === 0 ? (
          <p className="text-slate-500 p-6 rounded-2xl bg-slate-900/50 border border-white/10">
            No actionable advice available right now. Keep coding!
          </p>
        ) : (
          insights.map(insight => (
            <div key={insight.id} className="p-6 rounded-2xl bg-slate-900/50 border border-blue-500/30 backdrop-blur-md flex gap-4">
              <div className="mt-1">
                <Lightbulb className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">{insight.title}</h3>
                <p className="text-slate-300 leading-relaxed mb-4">{insight.body}</p>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full border border-blue-500/30">
                    {insight.category}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
