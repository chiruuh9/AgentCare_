import React, { useState, useEffect } from 'react';
import { checkHealth } from '../services/api';

export const Home: React.FC = () => {
  const [healthStatus, setHealthStatus] = useState<string>('Checking...');
  const [loading, setLoading] = useState<boolean>(false);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const data = await checkHealth();
      setHealthStatus(`${data.service} (${data.status})`);
    } catch (err) {
      setHealthStatus('Backend Offline / Unavailable');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
            AC
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight">AgentCare</h1>
            <p className="text-xs text-slate-400">Clinical Decision Support for Type-2 Diabetes</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-xs bg-slate-800/80 border border-slate-700/60 px-3 py-1.5 rounded-full">
            <span className={`h-2 w-2 rounded-full ${healthStatus.includes('ok') ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
            <span className="text-slate-300 font-mono">{healthStatus}</span>
          </div>
          <button
            onClick={fetchHealth}
            disabled={loading}
            className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3 py-1.5 rounded-lg transition-colors shadow-sm disabled:opacity-50 cursor-pointer"
          >
            {loading ? 'Testing...' : 'Ping API'}
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        {/* Banner Warning / Scope Notice */}
        <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-l-4 border-amber-500 p-4 rounded-r-xl border border-amber-500/20 text-amber-200 text-sm flex items-start space-x-3">
          <span className="text-lg">ℹ️</span>
          <div>
            <span className="font-semibold">Notice:</span> AgentCare is an interactive decision support tool. It does not diagnose or prescribe medications. All insights require clinician verification.
          </div>
        </div>

        {/* Hero Welcome */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 relative overflow-hidden">
          <div className="relative z-10 space-y-3">
            <span className="inline-block text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-950/60 border border-indigo-800/50 px-3 py-1 rounded-full">
              Full-Stack Skeleton Active
            </span>
            <h2 className="text-3xl font-extrabold text-white">Multi-Agent AI Clinical Assistant</h2>
            <p className="text-slate-400 max-w-2xl text-sm leading-relaxed">
              System architecture configured with FastAPI Backend and React + TypeScript + Tailwind CSS Frontend.
              Ready for agent implementations: record organization, history summarization, prescription interpretation, and translation.
            </p>
          </div>
          <div className="absolute -right-10 -bottom-10 w-72 h-72 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>
        </section>

        {/* Multi-Agent Modules Overview Grid */}
        <section className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-200">System Modules (Skeleton Readiness)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {agents.map((agent, i) => (
              <div
                key={i}
                className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-5 hover:border-slate-700 transition-all space-y-3"
              >
                <div className="text-2xl">{agent.icon}</div>
                <h4 className="font-medium text-slate-100">{agent.title}</h4>
                <p className="text-xs text-slate-400 leading-normal">{agent.description}</p>
                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-mono">Agent Status</span>
                  <span className="text-indigo-400 bg-indigo-950/80 px-2 py-0.5 rounded font-mono text-[10px]">
                    {agent.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500">
        AgentCare v0.1.0 — Type-2 Diabetes Management Support
      </footer>
    </div>
  );
};

const agents = [
  {
    icon: '📋',
    title: 'Records & Summarizer',
    description: 'Organizes patient records and synthesizes longitudinal Type-2 Diabetes medical history.',
    status: 'Skeleton Ready',
  },
  {
    icon: '💊',
    title: 'Prescription Interpreter',
    description: 'Interprets clinical dosage schedules and cross-checks regimen considerations.',
    status: 'Skeleton Ready',
  },
  {
    icon: '🌐',
    title: 'Instruction Translator',
    description: 'Translates complex medical directives into clear, patient-friendly guidance.',
    status: 'Skeleton Ready',
  },
  {
    icon: '⏰',
    title: 'Reminder Generator',
    description: 'Generates structured glucose monitoring and medication adherence schedules.',
    status: 'Skeleton Ready',
  },
];
