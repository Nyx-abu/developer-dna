import React from "react";
import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle, Info, TrendingUp } from "lucide-react";

interface InsightCardProps {
  type: "skill" | "productivity" | "debug" | "career" | "anomaly";
  title: string;
  body: string;
  severity: "info" | "warning" | "critical";
  className?: string;
}

const icons = {
  skill: <CheckCircle className="w-5 h-5 text-emerald-400" />,
  productivity: <TrendingUp className="w-5 h-5 text-blue-400" />,
  debug: <AlertCircle className="w-5 h-5 text-rose-400" />,
  career: <TrendingUp className="w-5 h-5 text-violet-400" />,
  anomaly: <Info className="w-5 h-5 text-amber-400" />
};

export function InsightCard({ type, title, body, severity, className }: InsightCardProps) {
  return (
    <div className={cn("p-5 rounded-xl bg-slate-800/50 border border-slate-700/50 backdrop-blur-md flex gap-4 transition-all hover:bg-slate-800/80 hover:border-slate-600/50", className)}>
      <div className="shrink-0 pt-1">
        {icons[type]}
      </div>
      <div>
        <h4 className="text-base font-semibold text-slate-200 mb-1">{title}</h4>
        <p className="text-sm text-slate-400 leading-relaxed">{body}</p>
      </div>
    </div>
  );
}
