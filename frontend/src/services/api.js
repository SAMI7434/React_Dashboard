import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Travel Dashboard API services
export const travelDashboardAPI = {
  // Analytics
  getAnalytics: () => api.get('/travel/dashboard/analytics/'),
  getMonthlyTrend: () => api.get('/travel/dashboard/monthly-trend/'),
  getStatusDistribution: () => api.get('/travel/dashboard/status-distribution/'),
  getDepartmentSpend: () => api.get('/travel/dashboard/department-spend/'),
  getRegionBookings: () => api.get('/travel/dashboard/region-bookings/'),
  getBookingTypeComparison: () => api.get('/travel/dashboard/booking-type-comparison/'),
  getRecentImports: () => api.get('/travel/dashboard/recent-imports/'),

  // Bookings
  getBookings: (params) => api.get('/travel/bookings/', { params }),
  getBooking: (id) => api.get(`/travel/bookings/${id}/`),
  getBookingTypes: () => api.get('/travel/bookings/booking_types/'),
  getBookingRegions: () => api.get('/travel/bookings/regions/'),

  // Users
  getUsers: (params) => api.get('/travel/users/', { params }),
  getUser: (id) => api.get(`/travel/users/${id}/`),
  syncUsers: () => api.post('/travel/import/sync-users/'),
  getUserDepartments: () => api.get('/travel/users/departments/'),
  getUserRegions: () => api.get('/travel/users/regions/'),

  // Import Logs
  getImportLogs: (params) => api.get('/travel/import-logs/', { params }),
  getImportLog: (id) => api.get(`/travel/import-logs/${id}/`),
  importBookings: (data) => api.post('/travel/import/bookings/', data),
  runReconciliation: () => api.post('/travel/import/reconciliation/'),

  // API Config
  getApiConfig: () => api.get('/travel/api-config/'),
  updateApiConfig: (id, data) => api.put(`/travel/api-config/${id}/`, data),
};

// Auth API services
export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: () => api.post('/auth/logout/'),
  refreshToken: () => api.post('/auth/token/refresh/', {
    refresh: localStorage.getItem('refresh_token')
  }),
  getCurrentUser: () => api.get('/auth/me/'),
};

// Ingest API services (existing)
export const ingestAPI = {
  getFuelData: (params) => api.get('/ingest/fuel-data/', { params }),
  uploadFuelData: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/ingest/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getUploadHistory: (params) => api.get('/ingest/upload-history/', { params }),
};

export default api;