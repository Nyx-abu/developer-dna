"use client";

import React, { useEffect, useState } from "react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from "recharts";
import type { SkillSnapshot } from "@/lib/types";

export function SkillRadar({ data }: { data?: SkillSnapshot[] }) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return <div className="w-full h-[300px] flex items-center justify-center text-slate-500">Loading Chart...</div>;
  }

  // Map real data if available, otherwise show empty radar
  const chartData = data && data.length > 0 
    ? data.map(s => ({ subject: s.language, score: s.proficiencyScore, fullMark: 100 }))
    : [];

  return (
    <div className="w-full h-[300px] animate-in fade-in zoom-in-95 duration-700">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 500 }} 
          />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
            itemStyle={{ color: '#60a5fa' }}
          />
          <Radar
            name="Proficiency"
            dataKey="score"
            stroke="#60a5fa"
            strokeWidth={2}
            fill="url(#colorUv)"
            fillOpacity={0.6}
            animationDuration={1500}
          />
          <defs>
            <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.2}/>
            </linearGradient>
          </defs>
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
