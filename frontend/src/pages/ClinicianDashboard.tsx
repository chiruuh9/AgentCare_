import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import {
  getPatientRecords,
  getPatientSummary,
  interpretPrescriptions,
  getPatientReminders,
  generatePatientReminders,
} from '../services/api';

export const ClinicianDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'records' | 'summary' | 'prescriptions' | 'reminders'>('records');

  const patientId = 1; // Demo patient John Doe
  const [records, setRecords] = useState<any[]>([]);
  const [summary, setSummary] = useState<string>('');
  const [prescriptionData, setPrescriptionData] = useState<any>(null);
  const [reminders, setReminders] = useState<any[]>([]);
  
  const [loadingRecords, setLoadingRecords] = useState<boolean>(false);
  const [errorRecords, setErrorRecords] = useState<string>('');

  const [loadingSummary, setLoadingSummary] = useState<boolean>(false);
  const [errorSummary, setErrorSummary] = useState<string>('');

  const [loadingPrescriptions, setLoadingPrescriptions] = useState<boolean>(false);
  const [errorPrescriptions, setErrorPrescriptions] = useState<string>('');

  const [loadingReminders, setLoadingReminders] = useState<boolean>(false);
  const [errorReminders, setErrorReminders] = useState<string>('');

  const [generatingReminders, setGeneratingReminders] = useState<boolean>(false);
  const [generateError, setGenerateError] = useState<string>('');

  // Auth check on mount
  useEffect(() => {
    const token = localStorage.getItem('agentcare_token');
    if (!token) {
      console.warn('[ClinicianDashboard] No JWT token found in localStorage, redirecting to login.');
      navigate('/login');
      return;
    }
    fetchRecords();
  }, [navigate]);

  const fetchRecords = useCallback(async () => {
    setLoadingRecords(true);
    setErrorRecords('');
    console.log('[ClinicianDashboard] Fetching patient records for patientId:', patientId);
    try {
      const data = await getPatientRecords(patientId);
      console.log('[ClinicianDashboard] Records response:', data);
      setRecords(data.records || []);
    } catch (err: any) {
      console.error('[ClinicianDashboard] Error fetching records:', err);
      setErrorRecords(err.response?.data?.detail || err.message || 'Failed to fetch patient records.');
    } finally {
      setLoadingRecords(false);
    }
  }, [patientId]);

  const handleFetchSummary = useCallback(async () => {
    setLoadingSummary(true);
    setErrorSummary('');
    console.log('[ClinicianDashboard] Fetching patient summary for patientId:', patientId);
    try {
      const data = await getPatientSummary(patientId);
      console.log('[ClinicianDashboard] Summary response:', data);
      setSummary(data.summary || '');
    } catch (err: any) {
      console.error('[ClinicianDashboard] Error fetching summary:', err);
      setErrorSummary(err.response?.data?.detail || err.message || 'Failed to synthesize summary.');
    } finally {
      setLoadingSummary(false);
    }
  }, [patientId]);

  const handleFetchPrescriptions = useCallback(async () => {
    setLoadingPrescriptions(true);
    setErrorPrescriptions('');
    console.log('[ClinicianDashboard] Fetching prescription interpretation for patientId:', patientId);
    try {
      const data = await interpretPrescriptions(patientId);
      console.log('[ClinicianDashboard] Prescriptions response:', data);
      setPrescriptionData(data);
    } catch (err: any) {
      console.error('[ClinicianDashboard] Error fetching prescriptions:', err);
      setErrorPrescriptions(err.response?.data?.detail || err.message || 'Failed to interpret prescriptions.');
    } finally {
      setLoadingPrescriptions(false);
    }
  }, [patientId]);

  const handleFetchReminders = useCallback(async () => {
    setLoadingReminders(true);
    setErrorReminders('');
    console.log('[ClinicianDashboard] Fetching reminders for patientId:', patientId);
    try {
      const data = await getPatientReminders(patientId);
      console.log('[ClinicianDashboard] Reminders response:', data);
      setReminders(data.reminders || []);
    } catch (err: any) {
      console.error('[ClinicianDashboard] Error fetching reminders:', err);
      setErrorReminders(err.response?.data?.detail || err.message || 'Failed to fetch reminders.');
    } finally {
      setLoadingReminders(false);
    }
  }, [patientId]);

  const handleGenerateReminders = async () => {
    setGeneratingReminders(true);
    setGenerateError('');
    console.log('[ClinicianDashboard] Generating reminders for patientId:', patientId);
    try {
      const data = await generatePatientReminders(patientId);
      console.log('[ClinicianDashboard] Generated reminders response:', data);
      setReminders(data.reminders || []);
      // Refetch reminders to ensure full sync
      await handleFetchReminders();
    } catch (err: any) {
      console.error('[ClinicianDashboard] Error generating reminders:', err);
      setGenerateError(err.response?.data?.detail || err.message || 'Failed to generate reminders.');
    } finally {
      setGeneratingReminders(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('agentcare_token');
    localStorage.removeItem('agentcare_role');
    localStorage.removeItem('agentcare_user');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <DisclaimerBanner />

      {/* Clinician Top Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
            AC
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">Clinician Workstation</h1>
            <p className="text-xs text-slate-400">Dr. Sarah Jenkins, MD — Type-2 Diabetes Decision Support</p>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors cursor-pointer"
        >
          Sign Out
        </button>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Selected Patient Banner */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="h-12 w-12 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xl">
              👤
            </div>
            <div>
              <h2 className="text-base font-bold text-white">John Doe (54yo Male)</h2>
              <div className="flex items-center space-x-3 text-xs text-slate-400 mt-0.5">
                <span>Type-2 Diabetes (4.5 yrs)</span>
                <span>•</span>
                <span>Target HbA1c: <strong className="text-indigo-400">7.0%</strong></span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400">Patient ID: <strong>#1</strong></span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => { setActiveTab('records'); fetchRecords(); }}
            className={`px-4 py-2 text-xs font-medium rounded-lg transition-colors cursor-pointer ${
              activeTab === 'records'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200'
            }`}
          >
            📋 Organized Records ({records.length})
          </button>
          <button
            onClick={() => { setActiveTab('summary'); handleFetchSummary(); }}
            className={`px-4 py-2 text-xs font-medium rounded-lg transition-colors cursor-pointer ${
              activeTab === 'summary'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200'
            }`}
          >
            🧠 AI History Summary
          </button>
          <button
            onClick={() => { setActiveTab('prescriptions'); handleFetchPrescriptions(); }}
            className={`px-4 py-2 text-xs font-medium rounded-lg transition-colors cursor-pointer ${
              activeTab === 'prescriptions'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200'
            }`}
          >
            💊 Prescription Interpreter
          </button>
          <button
            onClick={() => { setActiveTab('reminders'); handleFetchReminders(); }}
            className={`px-4 py-2 text-xs font-medium rounded-lg transition-colors cursor-pointer ${
              activeTab === 'reminders'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200'
            }`}
          >
            ⏰ Patient Reminders
          </button>
        </div>

        {/* Tab Content Panels */}
        {activeTab === 'records' && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Organized Patient Records</h3>
              <button
                onClick={fetchRecords}
                disabled={loadingRecords}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded transition-colors cursor-pointer disabled:opacity-50"
              >
                {loadingRecords ? 'Refreshing...' : 'Refresh Records'}
              </button>
            </div>

            {errorRecords && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg">
                ❌ <strong>Error:</strong> {errorRecords}
              </div>
            )}

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase text-[10px] tracking-wider">
                  <tr>
                    <th className="p-3">Type</th>
                    <th className="p-3">Value</th>
                    <th className="p-3">Date</th>
                    <th className="p-3">Notes & Context</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {records.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-800/40">
                      <td className="p-3 font-semibold text-indigo-300 capitalize">{r.record_type}</td>
                      <td className="p-3 font-mono text-white">
                        {r.value !== null ? `${r.value} ${r.unit || ''}` : '—'}
                      </td>
                      <td className="p-3 text-slate-400">{new Date(r.date).toLocaleDateString()}</td>
                      <td className="p-3 text-slate-300">{r.notes || r.raw_text || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-sm font-bold text-white">AI History Summarizer Agent</h3>
                <p className="text-xs text-slate-400">Synthesizes longitudinal Type-2 Diabetes trends, HbA1c logs, and adherence.</p>
              </div>
              <button
                onClick={handleFetchSummary}
                disabled={loadingSummary}
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
              >
                {loadingSummary ? 'Synthesizing...' : 'Generate New Summary'}
              </button>
            </div>

            {errorSummary && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg">
                ❌ <strong>Error:</strong> {errorSummary}
              </div>
            )}

            {loadingSummary ? (
              <div className="text-center py-12 text-slate-400 text-xs animate-pulse">
                History Summarizer Agent synthesizing clinical history...
              </div>
            ) : summary ? (
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">
                {summary}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs">
                Click "Generate New Summary" to invoke the History Summarizer Agent.
              </div>
            )}
          </div>
        )}

        {activeTab === 'prescriptions' && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-sm font-bold text-white">Prescription Interpreter Agent</h3>
                <p className="text-xs text-slate-400">Provides plain-language medication guides and usage explanations.</p>
              </div>
              <button
                onClick={handleFetchPrescriptions}
                disabled={loadingPrescriptions}
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
              >
                {loadingPrescriptions ? 'Interpreting...' : 'Run Interpreter Agent'}
              </button>
            </div>

            {errorPrescriptions && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg">
                ❌ <strong>Error:</strong> {errorPrescriptions}
              </div>
            )}

            {loadingPrescriptions ? (
              <div className="text-center py-12 text-slate-400 text-xs animate-pulse">
                Prescription Interpreter Agent parsing medication regimen...
              </div>
            ) : prescriptionData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {prescriptionData.medications?.map((m: any) => (
                    <div key={m.id} className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2">
                      <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Active Regimen</span>
                      <h4 className="text-base font-bold text-white">{m.name} {m.dosage}</h4>
                      <p className="text-xs text-slate-400">Frequency: <span className="text-slate-200">{m.frequency}</span></p>
                      <p className="text-xs text-slate-400">Prescriber: <span className="text-slate-200">{m.prescribing_doctor}</span></p>
                    </div>
                  ))}
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase mb-2">Agent Plain-Language Explanation</h4>
                  {prescriptionData.explanation}
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs">
                Click "Run Interpreter Agent" to generate patient-friendly medication guidance.
              </div>
            )}
          </div>
        )}

        {activeTab === 'reminders' && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-sm font-bold text-white">Reminder Generator Agent</h3>
                <p className="text-xs text-slate-400">Generates structured glucose check, medication, and lifestyle schedules.</p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleFetchReminders}
                  disabled={loadingReminders}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium px-3 py-2 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
                >
                  {loadingReminders ? 'Refreshing...' : '🔄 Refresh'}
                </button>
                <button
                  onClick={handleGenerateReminders}
                  disabled={generatingReminders}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
                >
                  {generatingReminders ? 'Generating Reminders...' : '➕ Generate Agent Reminders'}
                </button>
              </div>
            </div>

            {errorReminders && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg">
                ❌ <strong>Error:</strong> {errorReminders}
              </div>
            )}

            {generateError && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg">
                ❌ <strong>Error:</strong> {generateError}
              </div>
            )}

            <div className="space-y-3">
              {loadingReminders ? (
                <div className="text-center py-12 text-slate-400 text-xs animate-pulse">
                  Fetching patient reminders...
                </div>
              ) : reminders.map((r: any) => (
                <div key={r.id} className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-indigo-400 uppercase font-mono">{r.reminder_type}</span>
                      <span className="text-xs text-slate-500">•</span>
                      <span className="text-xs text-slate-400">{new Date(r.scheduled_time).toLocaleString()}</span>
                    </div>
                    <p className="text-sm text-slate-200">{r.message}</p>
                  </div>
                  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                    r.is_completed ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {r.is_completed ? 'Completed' : 'Pending'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

