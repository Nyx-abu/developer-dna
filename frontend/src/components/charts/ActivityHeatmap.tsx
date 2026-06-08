"use client";

import React, { useMemo, useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api";
import type { CodingSession } from "@/lib/types";

const WEEKS = 52;
const DAYS_PER_WEEK = 7;

type DayActivity = { date: string, level: number, count: number };

export function ActivityHeatmap() {
  const [weeksData, setWeeksData] = useState<DayActivity[][]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await apiClient.getSessions(1, 100);
        const sessions = res.data.data || [];
        
        // Group by day
        const activityMap: Record<string, number> = {};
        sessions.forEach(s => {
          if (!s.startTime) return;
          const dateStr = new Date(s.startTime).toISOString().split('T')[0];
          activityMap[dateStr] = (activityMap[dateStr] || 0) + (s.durationMinutes * 60 || 0);
        });

        // Generate grid
        const data: DayActivity[][] = [];
        const today = new Date();
        
        for (let w = 0; w < WEEKS; w++) {
          const week: DayActivity[] = [];
          for (let d = 0; d < DAYS_PER_WEEK; d++) {
            const date = new Date(today);
            date.setDate(date.getDate() - ((WEEKS - 1 - w) * 7 + (6 - d)));
            const dateStr = date.toISOString().split('T')[0];
            const seconds = activityMap[dateStr] || 0;
            const hours = seconds / 3600;
            
            let level = 0;
            if (hours > 0) level = 1;
            if (hours > 2) level = 2;
            if (hours > 4) level = 3;
            if (hours > 6) level = 4;
            
            week.push({ date: dateStr, level, count: Math.round(hours) });
          }
          data.push(week);
        }
        setWeeksData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const getLevelColor = (level: number) => {
    switch (level) {
      case 1: return "bg-blue-900/50";
      case 2: return "bg-blue-600/70";
      case 3: return "bg-blue-500";
      case 4: return "bg-violet-500";
      default: return "bg-slate-800/50";
    }
  };

  if (loading) {
    return <div className="w-full overflow-x-auto pb-4 text-slate-500">Loading Heatmap...</div>;
  }

  return (
    <div className="w-full overflow-x-auto pb-4">
      <div className="flex gap-1 min-w-max">
        {weeksData.map((week, wIdx) => (
          <div key={wIdx} className="flex flex-col gap-1">
            {week.map((day, dIdx) => (
              <div
                key={`${wIdx}-${dIdx}`}
                title={`${day.count} hours on ${day.date}`}
                className={cn(
                  "w-3 h-3 rounded-[2px] transition-colors duration-200 hover:ring-2 hover:ring-white/50 cursor-pointer",
                  getLevelColor(day.level)
                )}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex items-center justify-end gap-2 mt-4 text-xs text-slate-500">
        <span>Less</span>
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded-[2px] bg-slate-800/50" />
          <div className="w-3 h-3 rounded-[2px] bg-blue-900/50" />
          <div className="w-3 h-3 rounded-[2px] bg-blue-600/70" />
          <div className="w-3 h-3 rounded-[2px] bg-blue-500" />
          <div className="w-3 h-3 rounded-[2px] bg-violet-500" />
        </div>
        <span>More</span>
      </div>
    </div>
  );
}
