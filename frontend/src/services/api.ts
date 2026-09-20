import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to append JWT Bearer Token from localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('agentcare_token');
    if (token) {
      if (config.headers && typeof config.headers.set === 'function') {
        config.headers.set('Authorization', `Bearer ${token}`);
      } else {
        config.headers = config.headers || {};
        config.headers['Authorization'] = `Bearer ${token}`;
      }
    }
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data || '');
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor to catch and log API responses/errors
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response ${response.status}] ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error(`[API Response Error] ${error.config?.url}`, error.response?.status, error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Health check endpoint
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Auth Endpoints
export const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Patient & Multi-Agent Operations
export const getPatientRecords = async (patientId: number) => {
  const response = await api.get(`/patients/${patientId}/records`);
  return response.data;
};

export const uploadPatientRecord = async (patientId: number, rawText: string) => {
  const response = await api.post(`/patients/${patientId}/records/upload`, { raw_text: rawText });
  return response.data;
};

export const uploadPatientRecordFile = async (patientId: number, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/patients/${patientId}/records/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const getPatientSummary = async (patientId: number) => {
  const response = await api.get(`/patients/${patientId}/summary`);
  return response.data;
};

export const interpretPrescriptions = async (patientId: number) => {
  const response = await api.get(`/patients/${patientId}/prescriptions/interpret`);
  return response.data;
};

export const translateInstructions = async (patientId: number, language = 'en-IN', instructions?: string) => {
  const response = await api.get(`/patients/${patientId}/instructions/translate`, {
    params: { language, ...(instructions ? { instructions } : {}) },
  });
  return response.data;
};

export const getPatientReminders = async (patientId: number) => {
  const response = await api.get(`/patients/${patientId}/reminders`);
  return response.data;
};

export const generatePatientReminders = async (patientId: number) => {
  const response = await api.post(`/patients/${patientId}/reminders/generate`);
  return response.data;
};

export const completeReminder = async (reminderId: number) => {
  const response = await api.patch(`/reminders/${reminderId}/complete`);
  return response.data;
};

