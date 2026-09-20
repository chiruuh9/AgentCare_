import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import {
  translateInstructions,
  getPatientReminders,
  completeReminder,
  uploadPatientRecord,
  uploadPatientRecordFile,
} from '../services/api';

export const PatientPortal: React.FC = () => {
  const navigate = useNavigate();

  // Determine patient ID from stored user info or fallback to 1
  const storedUserRaw = localStorage.getItem('agentcare_user');
  let patientId = 1;
  if (storedUserRaw) {
    try {
      const userObj = JSON.parse(storedUserRaw);
      if (userObj.patient_id) {
        patientId = userObj.patient_id;
      }
    } catch (e) {
      console.error('[PatientPortal] Error parsing stored user:', e);
    }
  }

  // State
  const [instructions, setInstructions] = useState<string>('');
  const [language, setLanguage] = useState<string>('en-IN');
  const [reminders, setReminders] = useState<any[]>([]);
  const [rawUploadText, setRawUploadText] = useState<string>('');
  const [uploadedRecords, setUploadedRecords] = useState<any[]>([]);
  
  const [loadingInstructions, setLoadingInstructions] = useState<boolean>(false);
  const [errorInstructions, setErrorInstructions] = useState<string>('');

  const [loadingReminders, setLoadingReminders] = useState<boolean>(false);
  const [errorReminders, setErrorReminders] = useState<string>('');

  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<string>('');
  const [uploadError, setUploadError] = useState<string>('');

  // Check auth on mount
  useEffect(() => {
    const token = localStorage.getItem('agentcare_token');
    if (!token) {
      console.warn('[PatientPortal] No JWT token found in localStorage, redirecting to login.');
      navigate('/login');
      return;
    }
    fetchReminders();
    fetchTranslatedInstructions();
  }, [navigate]);

  const fetchTranslatedInstructions = useCallback(async (requestedLanguage = language) => {
    setLoadingInstructions(true);
    setErrorInstructions('');
    console.log('[PatientPortal] Fetching translated instructions for patientId:', patientId);
    try {
      const data = await translateInstructions(patientId, requestedLanguage);
      console.log('[PatientPortal] Instructions response:', data);
      setInstructions(data.translated_instructions || '');
    } catch (err: any) {
      console.error('[PatientPortal] Error fetching translated instructions:', err);
      const errMsg = err.response?.data?.detail || err.message || 'Failed to fetch care instructions.';
      setErrorInstructions(errMsg);
    } finally {
      setLoadingInstructions(false);
    }
  }, [patientId, language]);

  const handleLanguageChange = async (nextLanguage: string) => {
    setLanguage(nextLanguage);
    await fetchTranslatedInstructions(nextLanguage);
  };

  const handlePlayInstructions = () => {
    if (!instructions || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(instructions);
    utterance.lang = language;
    window.speechSynthesis.speak(utterance);
  };

  const fetchReminders = useCallback(async () => {
    setLoadingReminders(true);
    setErrorReminders('');
    console.log('[PatientPortal] Fetching reminders for patientId:', patientId);
    try {
      const data = await getPatientReminders(patientId);
      console.log('[PatientPortal] Reminders response:', data);
      setReminders(data.reminders || []);
    } catch (err: any) {
      console.error('[PatientPortal] Error fetching reminders:', err);
      const errMsg = err.response?.data?.detail || err.message || 'Failed to fetch reminders.';
      setErrorReminders(errMsg);
    } finally {
      setLoadingReminders(false);
    }
  }, [patientId]);

  const handleToggleComplete = async (reminderId: number) => {
    console.log('[PatientPortal] Completing reminder ID:', reminderId);
    setErrorReminders('');
    try {
      await completeReminder(reminderId);
      console.log('[PatientPortal] Successfully completed reminder ID:', reminderId);
      // Re-fetch reminders after completing
      await fetchReminders();
    } catch (err: any) {
      console.error('[PatientPortal] Error completing reminder:', err);
      const errMsg = err.response?.data?.detail || err.message || 'Failed to complete reminder.';
      setErrorReminders(errMsg);
    }
  };

  const handleUploadRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawUploadText.trim()) return;

    setUploading(true);
    setUploadSuccess('');
    setUploadError('');
    console.log('[PatientPortal] Submitting raw record for extraction...');
    try {
      const data = await uploadPatientRecord(patientId, rawUploadText);
      console.log('[PatientPortal] Upload record response:', data);
      setUploadedRecords(data.records || []);
      setUploadSuccess(`Successfully extracted ${data.records?.length || 0} structured record(s)!`);
      setRawUploadText('');
      
      // Re-fetch reminders and instructions to ensure UI is updated after record upload
      await fetchReminders();
      await fetchTranslatedInstructions();
    } catch (err: any) {
      console.error('[PatientPortal] Error uploading record:', err);
      const errMsg = err.response?.data?.detail || err.message || 'Failed to process raw record.';
      setUploadError(errMsg);
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadSuccess('');
    setUploadError('');
    try {
      const data = await uploadPatientRecordFile(patientId, file);
      setUploadedRecords(data.records || []);
      setUploadSuccess(`Successfully extracted ${data.records?.length || 0} structured record(s)!`);
      await fetchReminders();
      await fetchTranslatedInstructions();
    } catch (err: any) {
      const errMsg = err.response?.data?.detail || err.message || 'Failed to process uploaded record.';
      setUploadError(errMsg);
    } finally {
      setUploading(false);
      e.target.value = '';
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

      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/30">
            AC
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">Patient Care Portal</h1>
            <p className="text-xs text-slate-400">Welcome, John Doe — Type-2 Diabetes Support (Patient ID: #{patientId})</p>
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
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 space-y-8">
        
        {/* Section 1: Simplified Care Instructions */}
        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🌐</span>
              <div>
                <h2 className="text-base font-bold text-white">Your Type-2 Diabetes Guidance</h2>
                <p className="text-xs text-slate-400">Translated into simple, everyday language by Communication Translator Agent</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <label htmlFor="instruction-language" className="text-xs text-slate-400">Language</label>
              <select
                id="instruction-language"
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="en-IN">English</option>
                <option value="hi-IN">Hindi</option>
                <option value="te-IN">Telugu</option>
              </select>
            </div>

            <button
              onClick={() => fetchTranslatedInstructions()}
              disabled={loadingInstructions}
              className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-3 py-1.5 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
            >
              {loadingInstructions ? 'Translating...' : 'Translate Instructions'}
            </button>
          </div>

          {errorInstructions && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg">
              ❌ <strong>Error:</strong> {errorInstructions}
            </div>
          )}

          <div className="bg-slate-950 border border-slate-800/80 rounded-xl p-5 text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
            {loadingInstructions ? (
              <span className="text-slate-400 animate-pulse">Communication Translator Agent is translating clinical directives...</span>
            ) : instructions ? (
              instructions
            ) : (
              <span className="text-slate-500">No instructions translated yet. Click "Translate Instructions" above.</span>
            )}
          </div>
          <div className="flex items-center justify-between gap-3">
            <p className="text-[11px] text-amber-300/80">AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only.</p>
            <button
              type="button"
              onClick={handlePlayInstructions}
              disabled={!instructions || loadingInstructions}
              className="shrink-0 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
            >
              Play
            </button>
          </div>
        </section>

        {/* Section 2: Reminders Checklist */}
        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">⏰</span>
              <div>
                <h2 className="text-base font-bold text-white">My Reminders Checklist</h2>
                <p className="text-xs text-slate-400">Track medication times and blood glucose checks</p>
              </div>
            </div>

            <button
              onClick={fetchReminders}
              disabled={loadingReminders}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
            >
              {loadingReminders ? 'Refreshing...' : 'Refresh List'}
            </button>
          </div>

          {errorReminders && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg">
              ❌ <strong>Error:</strong> {errorReminders}
            </div>
          )}

          <div className="space-y-3">
            {loadingReminders ? (
              <p className="text-xs text-slate-400 text-center py-4 animate-pulse">Fetching active reminders...</p>
            ) : reminders.length === 0 ? (
              <p className="text-xs text-slate-500 text-center py-4">No active reminders scheduled.</p>
            ) : (
              reminders.map((r) => (
                <div
                  key={r.id}
                  className={`p-4 rounded-xl border transition-all flex items-center justify-between ${
                    r.is_completed
                      ? 'bg-slate-950/40 border-slate-800/40 text-slate-500 line-through'
                      : 'bg-slate-950 border-slate-800 text-slate-200'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={r.is_completed}
                      onChange={() => handleToggleComplete(r.id)}
                      disabled={r.is_completed}
                      className="h-4 w-4 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                    />
                    <div>
                      <span className="text-xs font-mono font-semibold uppercase text-indigo-400 mr-2">{r.reminder_type}</span>
                      <p className="text-sm inline">{r.message}</p>
                    </div>
                  </div>

                  <span className="text-[11px] font-mono text-slate-500">
                    {new Date(r.scheduled_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Section 3: Record Upload */}
        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center space-x-3 border-b border-slate-800 pb-3">
            <span className="text-2xl">📤</span>
            <div>
              <h2 className="text-base font-bold text-white">Upload New Health Record</h2>
              <p className="text-xs text-slate-400">Paste raw lab results or blood glucose notes (Record Organizer Agent extracts data)</p>
            </div>
          </div>

          <form onSubmit={handleUploadRecord} className="space-y-3">
            <textarea
              rows={4}
              value={rawUploadText}
              onChange={(e) => setRawUploadText(e.target.value)}
              placeholder="Example: HbA1c: 7.5% on 2025-01-15. Blood glucose: 140 mg/dL on 2025-01-16. Metformin 500mg twice daily."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors font-mono"
            ></textarea>

            <button
              type="submit"
              disabled={uploading || !rawUploadText.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs px-5 py-2.5 rounded-lg transition-colors disabled:opacity-50 cursor-pointer shadow-lg shadow-indigo-600/20"
            >
              {uploading ? 'Record Organizer Agent Extracting...' : 'Submit & Process Record'}
            </button>

            <label className="inline-flex items-center bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-xs px-4 py-2.5 rounded-lg transition-colors cursor-pointer">
              <span>{uploading ? 'Processing record...' : 'Scan / Upload Record'}</span>
              <input
                type="file"
                accept="image/*,.pdf,application/pdf"
                capture="environment"
                onChange={handleFileUpload}
                disabled={uploading}
                className="sr-only"
              />
            </label>
            <p className="text-[11px] text-amber-300/80">AgentCare does not diagnose Type-2 Diabetes or prescribe treatment. It assists clinicians and patients only.</p>
          </form>

          {uploadError && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3 rounded-lg">
              ❌ <strong>Error:</strong> {uploadError}
            </div>
          )}

          {uploadSuccess && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs p-3 rounded-lg">
              ✅ {uploadSuccess}
            </div>
          )}

          {uploadedRecords.length > 0 && (
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2">
              <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Extracted Structured Records</h4>
              <div className="space-y-2">
                {uploadedRecords.map((rec, i) => (
                  <div key={i} className="bg-slate-900 p-2.5 rounded border border-slate-800 text-xs flex items-center justify-between">
                    <div>
                      <span className="font-semibold text-indigo-300 capitalize mr-2">{rec.record_type}:</span>
                      <span>{rec.value !== null ? `${rec.value} ${rec.unit || ''}` : rec.notes}</span>
                    </div>
                    <span className="text-[10px] text-slate-500">{new Date(rec.date).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

      </main>
    </div>
  );
};

