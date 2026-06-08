import React from "react";

export default function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Settings</h1>
        <p className="text-slate-400">Manage your account and telemetry preferences.</p>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900/50 border border-white/10 backdrop-blur-md">
        <h3 className="text-lg font-semibold mb-4">VS Code Integration</h3>
        <p className="text-sm text-slate-400 mb-6">
          Connect your VS Code editor to start sending telemetry data.
        </p>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">API Key</label>
            <div className="flex gap-2">
              <input 
                type="password" 
                value="dev_token_example_12345" 
                readOnly
                className="flex-1 bg-slate-800/50 border border-slate-700/50 rounded-lg px-4 py-2 text-sm text-slate-200"
              />
              <button className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors">
                Copy
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-2">Paste this into your VS Code extension settings.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
