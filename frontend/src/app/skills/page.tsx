"use client";

import React, { useEffect, useState } from "react";
import { SkillRadar } from "@/components/charts/SkillRadar";
import { apiClient } from "@/lib/api";
import type { SkillSnapshot } from "@/lib/types";

export default function SkillsPage() {
  const [skills, setSkills] = useState<SkillSnapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadSkills() {
      try {
        const res = await apiClient.getSkills();
        setSkills(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadSkills();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Skill Profile</h1>
        <p className="text-slate-400">Analysis of your language proficiency and framework knowledge.</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md min-h-[400px] flex flex-col justify-center">
          <h3 className="text-lg font-semibold mb-6 px-4">Core Competencies</h3>
          <SkillRadar data={skills} />
        </div>
        
        <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md min-h-[400px] flex flex-col justify-center">
          <h3 className="text-lg font-semibold mb-6">Language Breakdown</h3>
          <div className="space-y-6">
            {loading ? (
              <p className="text-slate-500">Loading skills...</p>
            ) : skills.length === 0 ? (
              <p className="text-slate-500">No skill data available yet.</p>
            ) : (
              skills.map(s => (
                <SkillProgressBar 
                  key={s.id} 
                  language={s.language} 
                  level={Math.round(s.proficiencyScore)} 
                  color="bg-blue-500" 
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SkillProgressBar({ language, level, color }: { language: string, level: number, color: string }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center text-sm">
        <span className="font-medium text-slate-200">{language}</span>
        <span className="text-slate-400">{level}/100</span>
      </div>
      <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full ${color} transition-all duration-1000 ease-out`} 
          style={{ width: `${level}%` }}
        />
      </div>
    </div>
  );
}
