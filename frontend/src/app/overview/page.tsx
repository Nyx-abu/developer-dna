"use client";

import React, { useEffect, useState } from "react";
import { MetricCard } from "@/components/cards/MetricCard";
import { InsightCard } from "@/components/cards/InsightCard";
import { ProductivityChart } from "@/components/charts/ProductivityChart";
import { ActivityHeatmap } from "@/components/charts/ActivityHeatmap";
import { Clock, Code, GitCommit, Flame, Copy, Check } from "lucide-react";
import { apiClient } from "@/lib/api";
import type { AIInsight } from "@/lib/types";

export default function OverviewPage() {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  const mcpUrl = typeof window !== "undefined" ? window.location.origin : "https://your-server.com";
  const markdownSnippet = `[![Developer DNA Stats](${mcpUrl}/api/v1/badges/skills.svg)](https://github.com/Nyx-abu/developer-dna)`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(markdownSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // We can derive metric values from real data in the future, for now, we'll fetch insights
  // to replace the most prominent mock on this page.
  useEffect(() => {
    async function loadData() {
      try {
        const insightsRes = await apiClient.getInsights();
        setInsights(insightsRes.data);
      } catch (err) {
        console.error("Failed to load insights", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Welcome back, shoto</h1>
          <p className="text-slate-400">Here&apos;s your coding DNA for this week.</p>
        </div>
        <div className="flex flex-col gap-2 p-4 bg-slate-900/60 border border-slate-700/50 rounded-xl shadow-lg backdrop-blur-sm max-w-sm w-full">
          <div className="flex justify-between items-center">
            <span className="text-sm font-semibold text-slate-200">Share your DNA</span>
            <span className="text-xs text-slate-400">GitHub README</span>
          </div>
          <div className="flex gap-2">
            <code className="flex-1 bg-black/40 px-3 py-2 rounded text-xs text-slate-300 truncate font-mono border border-white/5">
              {markdownSnippet}
            </code>
            <button 
              onClick={copyToClipboard}
              className="p-2 bg-blue-600 hover:bg-blue-500 rounded text-white transition-colors flex-shrink-0"
              title="Copy to clipboard"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Hours Coded" 
          value="32.5h" 
          icon={<Clock className="w-5 h-5" />} 
          trend={{ value: 12, label: "vs last week" }} 
        />
        <MetricCard 
          title="Lines Written" 
          value="4,291" 
          icon={<Code className="w-5 h-5" />} 
          trend={{ value: 5, label: "vs last week" }} 
        />
        <MetricCard 
          title="Commits" 
          value="34" 
          icon={<GitCommit className="w-5 h-5" />} 
          trend={{ value: -2, label: "vs last week" }} 
        />
        <MetricCard 
          title="Current Streak" 
          value="5 days" 
          icon={<Flame className="w-5 h-5 text-orange-400" />} 
        />
      </div>

      <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
        <h3 className="text-lg font-semibold mb-1">Activity Heatmap</h3>
        <p className="text-sm text-slate-400 mb-6">Your coding contributions over the past year</p>
        <ActivityHeatmap />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
            <h3 className="text-lg font-semibold mb-1">Productivity Flow</h3>
            <p className="text-sm text-slate-400 mb-6">Your activity intensity over the day</p>
            {/* Keeping chart visual but it can be wired later */}
            <ProductivityChart data={[]} />
          </div>
        </div>

        <div className="space-y-6">
          <h3 className="text-lg font-semibold px-1">AI Insights</h3>
          <div className="flex flex-col gap-4">
            {loading ? (
              <p className="text-slate-500 text-sm">Loading insights...</p>
            ) : insights.length === 0 ? (
              <p className="text-slate-500 text-sm">No new insights.</p>
            ) : (
              insights.map((insight) => (
                <InsightCard 
                  key={insight.id}
                  type={insight.category} 
                  title={insight.title} 
                  body={insight.body} 
                  severity={insight.severity} 
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
