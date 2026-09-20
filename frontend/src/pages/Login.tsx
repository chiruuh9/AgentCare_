import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

export const Login: React.FC = () => {
  const [username, setUsername] = useState<string>('dr_jenkins');
  const [password, setPassword] = useState<string>('clinician123');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(username, password);
      localStorage.setItem('agentcare_token', data.access_token);
      localStorage.setItem('agentcare_role', data.role);
      localStorage.setItem('agentcare_user', JSON.stringify(data));

      if (data.role === 'clinician') {
        navigate('/clinician');
      } else {
        navigate('/patient');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <DisclaimerBanner />

      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
          <div className="text-center space-y-2">
            <div className="h-12 w-12 bg-indigo-600 rounded-2xl flex items-center justify-center font-bold text-xl text-white mx-auto shadow-lg shadow-indigo-500/30">
              AC
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">AgentCare Portal</h1>
            <p className="text-xs text-slate-400">Type-2 Diabetes Clinical Decision Support</p>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                placeholder="Enter username"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
                placeholder="Enter password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg text-sm transition-colors shadow-lg shadow-indigo-600/25 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Authenticating...' : 'Sign In to AgentCare'}
            </button>
          </form>

          {/* Demo Login Quick Fill */}
          <div className="pt-4 border-t border-slate-800 space-y-2">
            <span className="text-[11px] text-slate-500 block text-center font-mono">Demo Credentials Quick Fill</span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => fillCredentials('dr_jenkins', 'clinician123')}
                className="bg-slate-800/80 hover:bg-slate-800 text-slate-300 text-xs py-1.5 px-2 rounded border border-slate-700/60 transition-colors cursor-pointer"
              >
                👨‍⚕️ Clinician Demo
              </button>
              <button
                type="button"
                onClick={() => fillCredentials('john_doe', 'patient123')}
                className="bg-slate-800/80 hover:bg-slate-800 text-slate-300 text-xs py-1.5 px-2 rounded border border-slate-700/60 transition-colors cursor-pointer"
              >
                👤 Patient Demo
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
