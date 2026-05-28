import { useMemo, useState } from 'react'
import DataTable from '../components/DataTable.jsx'
import Badge from '../components/Badge.jsx'
import { approveRecord, rejectRecord } from '../api/ingest.js'
import { useRecords } from '../hooks/useRecords.js'

const RecordsPage = () => {
  const [filters, setFilters] = useState({ status: '', meterId: '', originalUnit: '' })
  const { records, isLoading, error, refresh } = useRecords(filters)

  const sortedRecords = useMemo(() => {
    return [...records].sort((a, b) => (a.billing_start || '').localeCompare(b.billing_start || ''))
  }, [records])

  const handleAction = async (recordId, action) => {
    if (action === 'approve') {
      await approveRecord(recordId)
    } else {
      await rejectRecord(recordId)
    }
    refresh()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Records review</h2>
        <p className="text-slate-400">Approve or reject normalized rows before audit lock.</p>
      </div>

      <div className="glass-panel rounded-2xl p-4 flex flex-col md:flex-row gap-4">
        <input
          type="text"
          placeholder="Search meter_id"
          value={filters.meterId}
          onChange={(event) => setFilters({ ...filters, meterId: event.target.value })}
          className="flex-1 px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-sm"
        />
        <select
          value={filters.originalUnit}
          onChange={(event) => setFilters({ ...filters, originalUnit: event.target.value })}
          className="px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-sm"
        >
          <option value="">All energy units</option>
          <option value="Wh">Wh</option>
          <option value="kWh">kWh</option>
          <option value="MWh">MWh</option>
          <option value="GWh">GWh</option>
          <option value="BTU">BTU</option>
        </select>
        <select
          value={filters.status}
          onChange={(event) => setFilters({ ...filters, status: event.target.value })}
          className="px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-sm"
        >
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {isLoading ? <p className="text-slate-400">Loading records...</p> : null}
      {error ? <p className="text-rose-300">{error}</p> : null}

      <DataTable
        columns={[
          { key: 'meter_id', label: 'Meter' },
          { key: 'facility_name', label: 'Facility' },
          { key: 'billing_start', label: 'Start' },
          { key: 'billing_end', label: 'End' },
          { key: 'original_energy_value', label: 'Orig energy' },
          { key: 'original_energy_unit', label: 'Orig unit' },
          { key: 'normalized_mwh', label: 'MWh' },
          { key: 'original_cost_value', label: 'Orig cost' },
          { key: 'original_cost_unit', label: 'Cost unit' },
          { key: 'normalized_thousand_dollars', label: 'Cost (k$)' },
          {
            key: 'normalization_logs',
            label: 'Conversion',
            render: (row) =>
              row.normalization_logs?.length
                ? row.normalization_logs.map((log) => log.conversion_formula).join(' | ')
                : '—'
          },
          {
            key: 'status',
            label: 'Status',
            render: (row) => <Badge variant={row.status}>{row.status}</Badge>
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (row) => (
              <div className="flex gap-2">
                <button
                  onClick={() => handleAction(row.id, 'approve')}
                  disabled={row.locked}
                  className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-200 text-xs"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleAction(row.id, 'reject')}
                  disabled={row.locked}
                  className="px-3 py-1 rounded-full bg-rose-500/20 text-rose-200 text-xs"
                >
                  Reject
                </button>
              </div>
            )
          }
        ]}
        rows={sortedRecords}
        emptyState="No records match your filters"
      />
    </div>
  )
}

export default RecordsPage
