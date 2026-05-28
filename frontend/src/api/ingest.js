import { apiFetch } from './client.js'

export const login = (payload) => apiFetch('/auth/login/', { method: 'POST', body: payload, auth: false })
export const getMe = () => apiFetch('/auth/me/')

export const uploadCsv = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return apiFetch('/upload/', { method: 'POST', body: formData })
}

export const getDashboard = () => apiFetch('/dashboard/')
export const getUploads = () => apiFetch('/uploads/')
export const getRecords = (params = {}) => {
  const query = new URLSearchParams(params).toString()
  const suffix = query ? `?${query}` : ''
  return apiFetch(`/records/${suffix}`)
}
export const getIssues = () => apiFetch('/issues/')

export const approveRecord = (recordId) => apiFetch(`/records/${recordId}/approve/`, { method: 'POST' })
export const rejectRecord = (recordId) => apiFetch(`/records/${recordId}/reject/`, { method: 'POST' })
