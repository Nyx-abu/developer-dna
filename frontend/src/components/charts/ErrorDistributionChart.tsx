"use client";

import React, { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import type { ErrorEvent } from "@/lib/types";

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981'];

export function ErrorDistributionChart({ errors }: { errors: ErrorEvent[] }) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return <div className="h-[300px] w-full flex items-center justify-center text-slate-500">Loading Chart...</div>;
  }

  if (!errors || errors.length === 0) {
    return <div className="h-[300px] w-full flex items-center justify-center text-slate-500">No errors to display</div>;
  }

  // Count by errorType
  const counts: Record<string, number> = {};
  errors.forEach(e => {
    counts[e.errorType] = (counts[e.errorType] || 0) + 1;
  });

  const data = Object.keys(counts).map(key => ({
    name: key,
    value: counts[key]
  })).sort((a, b) => b.value - a.value);

  return (
    <div className="h-[300px] w-full animate-in fade-in zoom-in-95 duration-700">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={5}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
            itemStyle={{ color: '#e2e8f0' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
