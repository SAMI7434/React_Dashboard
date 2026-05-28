import { apiFetch } from './client.js'

export const login = (payload) => apiFetch('/auth/login/', { method: 'POST', body: payload, auth: false })
export const getMe = () => apiFetch('/auth/me/')

export const uploadCsv = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return apiFetch('/ingest/upload/', { method: 'POST', body: formData })
}

export const getDashboard = () => apiFetch('/ingest/dashboard/')
export const getUploads = () => apiFetch('/ingest/uploads/')
export const getRecords = (params = {}) => {
  const query = new URLSearchParams(params).toString()
  const suffix = query ? `?${query}` : ''
  return apiFetch(`/ingest/records/${suffix}`)
}
export const getIssues = () => apiFetch('/ingest/issues/')

export const approveRecord = (recordId) => apiFetch(`/ingest/records/${recordId}/approve/`, { method: 'POST' })
export const rejectRecord = (recordId) => apiFetch(`/ingest/records/${recordId}/reject/`, { method: 'POST' })
