import { useState, useEffect, useMemo } from 'react'
import { sapAPI } from '../api/sap'

const PAGE_SIZE = 25

const StatusBadge = ({ status }) => {
  const styles = {
    pending: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    approved: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    rejected: 'bg-red-500/20 text-red-300 border-red-500/30',
  }
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.pending}`}>
      {status}
    </span>
  )
}

const IssueBadge = ({ count }) => {
  if (!count || count === 0) return null
  return (
    <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-300 border border-red-500/30">
      {count} issue{count > 1 ? 's' : ''}
    </span>
  )
}

const SAPRecordsPage = () => {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({
    status: '',
    plant_code: '',
    vendor_id: '',
    fuel_type: '',
    has_issues: '',
    search: '',
  })
  const [expandedRow, setExpandedRow] = useState(null)
  const [actionLoading, setActionLoading] = useState(null)

  const fetchRecords = async () => {
    setLoading(true)
    try {
      const params = { limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE, ...filters }
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === undefined) delete params[key]
      })
      const response = await sapAPI.getRecords(params)
      setRecords(response.data.results || response.data || [])
      setTotal(response.data.count || (Array.isArray(response.data) ? response.data.length : 0))
    } catch (err) {
      console.error('Error fetching SAP records:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecords()
  }, [page, filters])

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1)
  }

  const handleApprove = async (id) => {
    setActionLoading(id)
    try {
      await sapAPI.approveRecord(id)
      fetchRecords()
    } catch (err) {
      alert('Failed to approve record')
    } finally {
      setActionLoading(null)
    }
  }

  const handleReject = async (id) => {
    setActionLoading(id)
    try {
      await sapAPI.rejectRecord(id)
      fetchRecords()
    } catch (err) {
      alert('Failed to reject record')
    } finally {
      setActionLoading(null)
    }
  }

  const handleExport = async () => {
    try {
      const response = await sapAPI.exportCSV()
      const blob = new Blob([response.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'sap_procurement_records.csv'
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white">Procurement Records</h2>
          <p className="text-slate-400 text-sm mt-1">
            {total} records found
          </p>
        </div>
        <button
          onClick={handleExport}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition text-sm"
        >
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="glass-panel rounded-2xl p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <input
            type="text"
            placeholder="Search..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500"
          />
          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <input
            type="text"
            placeholder="Plant Code"
            value={filters.plant_code}
            onChange={(e) => handleFilterChange('plant_code', e.target.value)}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500"
          />
          <input
            type="text"
            placeholder="Vendor ID"
            value={filters.vendor_id}
            onChange={(e) => handleFilterChange('vendor_id', e.target.value)}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500"
          />
          <select
            value={filters.has_issues}
            onChange={(e) => handleFilterChange('has_issues', e.target.value)}
            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Records</option>
            <option value="true">With Issues</option>
            <option value="false">No Issues</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-800/50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Material</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Plant</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Vendor</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Quantity</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Cost</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Issues</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan="10" className="px-4 py-8 text-center text-slate-400">
                    Loading records...
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan="10" className="px-4 py-8 text-center text-slate-400">
                    No records found
                  </td>
                </tr>
              ) : (
                records.map((record) => (
                  <tr key={record.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-4 py-3 text-sm text-slate-300">#{record.id}</td>
                    <td className="px-4 py-3 text-sm text-white font-mono">{record.material_number || '-'}</td>
                    <td className="px-4 py-3 text-sm text-white">{record.plant_code || '-'}</td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      <div>{record.vendor_name || record.vendor_id || '-'}</div>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300">{record.purchase_date || '-'}</td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {record.normalized_quantity ? `${parseFloat(record.normalized_quantity).toLocaleString()} ${record.normalized_unit}` : '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-white font-medium">
                      {record.total_cost ? `$${parseFloat(record.total_cost).toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={record.status} />
                    </td>
                    <td className="px-4 py-3">
                      <IssueBadge count={record.issues_count} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setExpandedRow(expandedRow === record.id ? null : record.id)}
                          className="px-2 py-1 text-xs bg-slate-700 hover:bg-slate-600 text-white rounded transition"
                        >
                          {expandedRow === record.id ? 'Hide' : 'Details'}
                        </button>
                        {record.status === 'pending' && !record.locked && (
                          <>
                            <button
                              onClick={() => handleApprove(record.id)}
                              disabled={actionLoading === record.id}
                              className="px-2 py-1 text-xs bg-emerald-500 hover:bg-emerald-600 text-white rounded transition disabled:opacity-50"
                            >
                              ✓
                            </button>
                            <button
                              onClick={() => handleReject(record.id)}
                              disabled={actionLoading === record.id}
                              className="px-2 py-1 text-xs bg-red-500 hover:bg-red-600 text-white rounded transition disabled:opacity-50"
                            >
                              ✗
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Expanded Row Details */}
        {expandedRow && (
          <div className="border-t border-slate-700 p-4 bg-slate-800/30">
            {records.find(r => r.id === expandedRow) && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(records.find(r => r.id === expandedRow)).map(([key, value]) => (
                  value !== null && value !== undefined && key !== 'sap_issues' && key !== 'approval_logs' && (
                    <div key={key}>
                      <p className="text-xs text-slate-500 uppercase">{key}</p>
                      <p className="text-sm text-white">{String(value)}</p>
                    </div>
                  )
                ))}
              </div>
            )}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-4 py-3 border-t border-slate-700 flex items-center justify-between">
            <p className="text-sm text-slate-400">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SAPRecordsPage