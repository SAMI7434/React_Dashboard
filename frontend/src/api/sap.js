import { apiFetch } from './client.js'

export const sapAPI = {
  // Dashboard
  getDashboard: () => apiFetch('/sap/dashboard/'),
  
  // Upload
  uploadCSV: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiFetch('/sap/upload/', {
      method: 'POST',
      headers: { },
      body: formData,
      auth: true
    })
  },
  
  // Records
  getRecords: (params) => {
    const queryString = new URLSearchParams(params).toString()
    return apiFetch(`/sap/records/?${queryString}`)
  },
  getRecord: (id) => apiFetch(`/sap/records/${id}/`),
  approveRecord: (id, notes = '') => apiFetch(`/sap/records/${id}/approve/`, {
    method: 'POST',
    body: { notes }
  }),
  rejectRecord: (id, notes = '') => apiFetch(`/sap/records/${id}/reject/`, {
    method: 'POST',
    body: { notes }
  }),
  addNote: (id, notes) => apiFetch(`/sap/records/${id}/add_note/`, {
    method: 'POST',
    body: { notes }
  }),
  exportCSV: () => apiFetch('/sap/records/export_csv/'),
  
  // Issues
  getIssues: (params) => {
    const queryString = new URLSearchParams(params).toString()
    return apiFetch(`/sap/issues/?${queryString}`)
  },
  
  // Approval Logs
  getApprovalLogs: (params) => {
    const queryString = new URLSearchParams(params).toString()
    return apiFetch(`/sap/approval-logs/?${queryString}`)
  },
  
  // Batches
  getBatches: () => apiFetch('/sap/batches/'),
}

export default sapAPI