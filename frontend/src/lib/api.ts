import axios from 'axios';
import type { Incident, Source } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true // Extremely important for HttpOnly cookies
});

// Helper to read CSRF cookie
function getCookie(name: string) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift();
  return null;
}


// Request Interceptor: Attach Project ID
api.interceptors.request.use(config => {
  const projectId = localStorage.getItem('causely_project_id');
  if (projectId) {
    config.headers['X-Project-ID'] = projectId;
  }
  return config;
});

// Request Interceptor: Attach CSRF token

api.interceptors.request.use(config => {
  const csrf = getCookie('csrf_token');
  if (csrf && config.method && ['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
    config.headers['x-csrf-token'] = csrf;
  }
  return config;
});

// Response Interceptor: Handle 401s
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      if (!error.config.url.includes('/auth/me') && !error.config.url.includes('/auth/login')) {
         window.dispatchEvent(new Event('unauthorized'));
      }
    }
    return Promise.reject(error);
  }
);

export const loginUser = async (email: string, password: string) => {
  const res = await api.post('/auth/login', { email, password });
  return res.data;
};

export const signupUser = async (data: any) => {
  const res = await api.post('/auth/signup', data);
  return res.data;
};

export const getMe = async () => {
  const res = await api.get('/auth/me');
  return res.data;
};

export const logoutUser = async () => {
  const res = await api.post('/auth/logout');
  return res.data;
};

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getSettings = async () => {
  const response = await api.get('/settings');
  return response.data;
};

export const updateSettings = async (data: any) => {
  const response = await api.post('/settings', data);
  return response.data;
};

export const testLlmConnection = async () => {
  const response = await api.post('/settings/test-llm');
  return response.data;
};

export const clearTenantData = async (confirmation: string) => {
  const response = await api.post('/settings/clear-data', { confirmation });
  return response.data;
};

export const getUsage = async () => {
  const response = await api.get('/settings/usage');
  return response.data;
};

export const getDashboardStats = async () => {
  try {
    const response = await api.get('/incidents/stats');
    return response.data;
  } catch {
    return {
      total_incidents: 0,
      resolved: 0,
      active: 0,
      avg_confidence: 0,
      avg_confidence_level: 'None',
      sources_connected: 0
    };
  }
};

export const getIncidents = async (): Promise<Incident[]> => {
  try {
    const response = await api.get('/incidents');
    return response.data;
  } catch {
    return [];
  }
};

export const getIncident = async (id: string): Promise<Incident | null> => {
  try {
    const response = await api.get(`/incidents/${id}`);
    return response.data;
  } catch {
    return null;
  }
};

export const createIncident = async (data: Partial<Incident>): Promise<Incident> => {
  const response = await api.post('/incidents', data);
  return response.data;
};

export const getIncidentTrace = async (id: string) => {
  const response = await api.get(`/incidents/${id}/trace`);
  return response.data;
};

export const getSources = async (): Promise<Source[]> => {
  try {
    const response = await api.get('/sources');
    return response.data;
  } catch {
    return [];
  }
};

export const getReadiness = async () => {
  try {
    const response = await api.get('/sources/readiness');
    return response.data;
  } catch {
    return { score: 0, github: false, logs: false, database: false, history: false };
  }
};

export const createSource = async (type: string, data: any) => {
  if (type === 'github') return api.post('/sources/github', data);
  if (type === 'postgres') return api.post('/sources/postgres', data);
  if (type === 'mongodb') return api.post('/sources/mongodb', data);
  if (type === 'loki') return api.post('/sources/loki', data);
  if (type === 'static_log') {
    const formData = new FormData();
    formData.append('file', data.file);
    return api.post('/sources/static-log', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: data.onUploadProgress
    });
  }
  if (type === 'razorpay') return api.post('/sources/razorpay', data);
  if (type === 'generic_rest') return api.post('/sources/generic-rest', data);
  throw new Error('Unknown source type');
};

export const deleteSource = async (id: string) => {
  const response = await api.delete(`/sources/${id}`);
  return response.data;
};

export const testConnection = async (id: string) => {
  const response = await api.post(`/sources/${id}/test`);
  return response.data;
};

export const createApproval = async (data: { incident_id: string; action_type: string; action_payload: object }) => {
  const response = await api.post('/approvals', data);
  return response.data;
};

export const approveAction = async (id: string) => {
  const response = await api.post(`/approvals/${id}/approve`);
  return response.data;
};

export const executeAction = async (id: string) => {
  const response = await api.post(`/approvals/${id}/execute`);
  return response.data;
};


export const getProjects = async () => {
  const res = await api.get('/projects');
  return res.data;
};

export const createProject = async (data: any) => {
  const res = await api.post('/projects', data);
  return res.data;
};

export const getProject = async (id: string) => {
  const res = await api.get(`/projects/${id}`);
  return res.data;
};

export const updateProject = async (id: string, data: any) => {
  const res = await api.patch(`/projects/${id}`, data);
  return res.data;
};

export const deleteProject = async (id: string) => {
  const res = await api.delete(`/projects/${id}`);
  return res.data;
};

export const getProjectMembers = async (id: string) => {
  const res = await api.get(`/projects/${id}/members`);
  return res.data;
};

export const inviteProjectMember = async (id: string, email: string, role: string) => {
  const res = await api.post(`/projects/${id}/members/invite`, { email, role });
  return res.data;
};

export const updateProjectMember = async (id: string, memberId: string, role: string) => {
  const res = await api.patch(`/projects/${id}/members/${memberId}`, { role, email: '' });
  return res.data;
};

export const removeProjectMember = async (id: string, memberId: string) => {
  const res = await api.delete(`/projects/${id}/members/${memberId}`);
  return res.data;
};

export const getInvitation = async (token: string) => {
  const res = await api.get(`/projects/invitations/${token}`);
  return res.data;
};

export const acceptInvitation = async (token: string) => {
  const res = await api.post(`/projects/invitations/${token}/accept`);
  return res.data;
};
