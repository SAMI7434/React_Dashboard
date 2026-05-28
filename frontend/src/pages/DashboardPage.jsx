import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts'
import { useDashboard } from '../hooks/useDashboard.js'
import { useRecords } from '../hooks/useRecords.js'
import ChartCard from '../components/ChartCard.jsx'
import DataTable from '../components/DataTable.jsx'
import StatCard from '../components/StatCard.jsx'
import Badge from '../components/Badge.jsx'

const palette = ['#06b6d4', '#38bdf8', '#f97316', '#fbbf24', '#34d399']

const DashboardPage = () => {
  const { data, isLoading, error } = useDashboard()
  const { records } = useRecords()

  if (isLoading) {
    return <div className="text-slate-300">Loading dashboard...</div>
  }

  if (error) {
    return <div className="text-rose-300">{error}</div>
  }

  const summary = data?.summary || {}
  const quality = data?.normalization_quality || {}
  const insights = data?.normalization_insights || []
  const failedRows = records.filter((record) =>
    record.issues?.some((issue) => issue.severity === 'error')
  )
  const suspiciousRows = records.filter((record) =>
    record.issues?.some((issue) => issue.severity === 'warning')
  )
  const approvedRows = records.filter((record) => record.status === 'approved')

  return (
    <div className="space-y-8">
      <section className="grid md:grid-cols-2 xl:grid-cols-5 gap-4">
        <StatCard label="Total cost (k$)" value={`${summary.total_thousand_dollars || '0.00'}`} accent="text-cyan-200" />
        <StatCard label="Total MWh" value={`${summary.total_mwh || '0'} MWh`} accent="text-sky-200" />
        <StatCard label="Uploaded bills" value={summary.uploaded_bills || 0} />
        <StatCard label="Failed rows" value={summary.failed_records || 0} accent="text-rose-300" />
        <StatCard label="Suspicious" value={summary.suspicious_records || 0} accent="text-amber-300" />
      </section>

      <section className="grid lg:grid-cols-2 gap-6">
        <ChartCard title="Monthly electricity cost" subtitle="Thousand-dollar totals by billing end date">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data?.monthly_cost_trend || []}>
              <CartesianGrid strokeDasharray="4 4" stroke="#1f2937" />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Line type="monotone" dataKey="total_thousand_dollars" stroke="#06b6d4" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Monthly electricity usage" subtitle="MWh trend across billing cycles">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data?.monthly_usage_trend || []}>
              <CartesianGrid strokeDasharray="4 4" stroke="#1f2937" />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Bar dataKey="usage_mwh" fill="#38bdf8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </section>

      <section>
        <ChartCard title="Tariff mix" subtitle="Cost distribution by tariff type">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data?.tariff_breakdown || []}
                dataKey="total_thousand_dollars"
                nameKey="tariff_type"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={4}
              >
                {(data?.tariff_breakdown || []).map((entry, index) => (
                  <Cell key={entry.tariff_type} fill={palette[index % palette.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </section>

      <section className="space-y-4">
        <h3 className="text-lg font-semibold">Normalization quality</h3>
        <div className="grid md:grid-cols-5 gap-4">
          <StatCard label="Normalized rows" value={quality.normalized_rows || 0} />
          <StatCard label="Failed conversions" value={quality.failed_conversions || 0} accent="text-rose-300" />
          <StatCard label="Unknown units" value={quality.unknown_units || 0} accent="text-amber-300" />
          <StatCard label="Top unit" value={quality.most_common_unit || 'N/A'} />
          <StatCard label="Success rate" value={`${quality.success_rate || 0}%`} accent="text-emerald-200" />
        </div>
        <div className="glass-panel rounded-2xl p-5">
          <h4 className="text-sm uppercase tracking-[0.2em] text-slate-400">Insights</h4>
          <ul className="mt-3 space-y-2 text-sm text-slate-200">
            {insights.length === 0 ? (
              <li>No normalization insights yet.</li>
            ) : (
              insights.map((item, index) => <li key={index}>• {item}</li>)
            )}
          </ul>
        </div>
      </section>

      <section className="grid lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Recent uploads</h3>
          <DataTable
            columns={[
              { key: 'file_name', label: 'File' },
              { key: 'upload_time', label: 'Uploaded' },
              { key: 'status', label: 'Status' }
            ]}
            rows={data?.recent_uploads || []}
            emptyState="No uploads yet"
          />
        </div>
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Review queue highlights</h3>
          <DataTable
            columns={[
              { key: 'meter_id', label: 'Meter' },
              { key: 'facility_name', label: 'Facility' },
              {
                key: 'status',
                label: 'Status',
                render: (row) => <Badge variant={row.status}>{row.status}</Badge>
              }
            ]}
            rows={[...failedRows.slice(0, 2), ...suspiciousRows.slice(0, 2), ...approvedRows.slice(0, 2)]}
            emptyState="No records yet"
          />
        </div>
      </section>
    </div>
  )
}

export default DashboardPage
