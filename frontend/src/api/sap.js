import { apiFetch } from './client.js'

export const sapAPI = {
  // Dashboard
  getDashboard: () => apiFetch('/ingest/sap/dashboard/'),

  // Upload
  uploadCSV: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiFetch('/ingest/sap/upload/', {
      method: 'POST',
      headers: { },
      body: formData,
      auth: true
    })
  },

  // Records
  getRecords: (params) => {
    const queryString = new URLSearchParams(params).toString()
    return apiFetch(`/ingest/sap/records/?${queryString}`)
  },
  getRecord: (id) => apiFetch(`/ingest/sap/records/${id}/`),
  approveRecord: (id, notes = '') => apiFetch(`/ingest/sap/records/${id}/approve/`, {
    method: 'POST',
    body: { notes }
  }),
  rejectRecord: (id, notes = '') => apiFetch(`/ingest/sap/records/${id}/reject/`, {
    method: 'POST',
    body: { notes }
  }),
  addNote: (id, notes) => apiFetch(`/ingest/sap/records/${id}/add_note/`, {
    method: 'POST',
    body: { notes }
  }),
  exportCSV: () => apiFetch('/ingest/sap/records/export_csv/'),

  // Issues
  getIssues: (params) => {
    const queryString = new URLSearchParams(params).toString()
    return apiFetch(`/ingest/sap/issues/?${queryString}`)
  },

  // Approval Logs
  getApprovalLogs: (params) => {
    const queryString = new URLSearchParams(params).toString()
    return apiFetch(`/ingest/sap/approval-logs/?${queryString}`)
  },

  // Batches
  getBatches: () => apiFetch('/ingest/sap/batches/'),
}

export default sapAPI