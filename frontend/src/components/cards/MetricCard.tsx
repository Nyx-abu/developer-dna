import React from "react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: { value: number; label: string };
  className?: string;
}

export function MetricCard({ title, value, icon, trend, className }: MetricCardProps) {
  return (
    <div className={cn("p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm transition-all hover:scale-[1.02] hover:bg-white/10", className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-400">{title}</h3>
        <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg">
          {icon}
        </div>
      </div>
      <div className="flex items-end justify-between">
        <div className="text-3xl font-bold text-white">{value}</div>
        {trend && (
          <div className={cn("text-sm font-medium", trend.value >= 0 ? "text-emerald-400" : "text-rose-400")}>
            {trend.value >= 0 ? "+" : ""}{trend.value}% {trend.label}
          </div>
        )}
      </div>
    </div>
  );
}
