import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { sapAPI } from '../api/sap'

const COLORS = ['#06B6D4', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#EC4899', '#6366F1']

const StatCard = ({ title, value, subtitle, icon, color = 'cyan' }) => (
  <div className="glass-panel rounded-2xl p-6">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm text-slate-400 mb-1">{title}</p>
        <h3 className="text-3xl font-semibold text-white">
          {typeof value === 'string' && value.includes('.') && !value.includes('e') 
            ? parseFloat(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
            : value}
        </h3>
        {subtitle && <p className="text-xs text-slate-500 mt-2">{subtitle}</p>}
      </div>
      <div className={`w-12 h-12 rounded-xl bg-${color}-500/20 flex items-center justify-center`}>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  </div>
)

const ChartCard = ({ title, children, className = '' }) => (
  <div className={`glass-panel rounded-2xl p-6 ${className}`}>
    <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
    {children}
  </div>
)

const InsightCard = ({ insights }) => (
  <div className="glass-panel rounded-2xl p-6">
    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
      <span>💡</span> Smart Insights
    </h3>
    <ul className="space-y-3">
      {insights.map((insight, idx) => (
        <li key={idx} className="flex items-start gap-3 text-sm text-slate-300">
          <span className="text-cyan-400 mt-0.5">▸</span>
          <span>{insight}</span>
        </li>
      ))}
    </ul>
  </div>
)

const SAPDashboardPage = () => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await sapAPI.getDashboard()
        setData(response.data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-slate-400">Loading SAP Procurement Analytics...</div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="glass-panel rounded-2xl p-8 text-center">
        <h2 className="text-xl text-white mb-4">No SAP Data Available</h2>
        <p className="text-slate-400 mb-6">
          Upload an SAP fuel procurement CSV file to get started with analytics.
        </p>
        <Link
          to="/sap/upload"
          className="inline-block px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition"
        >
          Upload SAP Data
        </Link>
      </div>
    )
  }

  const { summary, monthly_spend_trend, plant_costs, vendor_spend, fuel_type_distribution, country_distribution, error_breakdown, status_overview, insights } = data

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">SAP Procurement Intelligence</p>
        <h1 className="text-3xl md:text-4xl font-semibold text-white mt-1">Fuel & Procurement Analytics</h1>
        <p className="text-slate-400 max-w-2xl mt-2">
          Monitor fuel procurement, detect anomalies, and manage approvals across all plants and vendors.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Fuel Spend"
          value={`$${parseFloat(summary.total_fuel_spend || 0).toLocaleString('en-US', { minimumFractionDigits: 0 })}`}
          subtitle="All approved & pending records"
          icon="💰"
          color="cyan"
        />
        <StatCard
          title="Total Fuel Quantity"
          value={`${parseFloat(summary.total_fuel_quantity || 0).toLocaleString('en-US', { minimumFractionDigits: 0 })} L`}
          subtitle="Normalized to liters"
          icon="⛽"
          color="violet"
        />
        <StatCard
          title="Vendors"
          value={summary.total_vendors}
          subtitle={`Across ${summary.total_plants} plants`}
          icon="🏭"
          color="emerald"
        />
        <StatCard
          title="Pending Approvals"
          value={summary.pending_approvals}
          subtitle={`${summary.suspicious_records} suspicious, ${summary.failed_records} failed`}
          icon="⚠️"
          color="amber"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid lg:grid-cols-2 gap-6">
        <ChartCard title="Monthly Fuel Spend Trend">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthly_spend_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#F1F5F9' }}
                  formatter={(value) => [`$${parseFloat(value).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Spend']}
                />
                <Line type="monotone" dataKey="total_spend" stroke="#06B6D4" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Plant-wise Procurement Cost">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={plant_costs} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#64748B" fontSize={12} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="plant_code" stroke="#64748B" fontSize={12} width={80} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#F1F5F9' }}
                  formatter={(value) => [`$${parseFloat(value).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Cost']}
                />
                <Bar dataKey="total_cost" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Charts Row 2 */}
      <div className="grid lg:grid-cols-3 gap-6">
        <ChartCard title="Vendor Spend Ranking">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={vendor_spend} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#64748B" fontSize={12} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="vendor_name" stroke="#64748B" fontSize={11} width={100} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#F1F5F9' }}
                  formatter={(value, name) => [
                    `$${parseFloat(value).toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
                    name === 'total_spend' ? 'Spend' : 'Transactions'
                  ]}
                />
                <Bar dataKey="total_spend" fill="#10B981" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Fuel Type Distribution">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={fuel_type_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="total_quantity"
                  nameKey="fuel_type"
                  label={({ fuel_type, percent }) => `${fuel_type} ${(percent * 100).toFixed(0)}%`}
                  labelLine={{ stroke: '#64748B' }}
                >
                  {fuel_type_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#F1F5F9' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Approval Status">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={status_overview}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="count"
                  nameKey="status"
                  label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                  labelLine={{ stroke: '#64748B' }}
                >
                  {status_overview.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#F1F5F9' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Charts Row 3 */}
      <div className="grid lg:grid-cols-2 gap-6">
        <ChartCard title="Procurement by Country">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={country_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="country" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1E293B', border: '1px solid #334155', color: '#F1F5F9' }}
                  formatter={(value) => [`$${parseFloat(value).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Spend']}
                />
                <Bar dataKey="total_spend" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <InsightCard insights={insights} />
      </div>

      {/* Quick Actions */}
      <div className="glass-panel rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-4">
          <Link
            to="/sap/upload"
            className="px-5 py-2.5 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition text-sm font-medium"
          >
            ↑ Upload SAP Data
          </Link>
          <Link
            to="/sap/records"
            className="px-5 py-2.5 bg-violet-500 hover:bg-violet-600 text-white rounded-lg transition text-sm font-medium"
          >
            📋 View All Records
          </Link>
          <Link
            to="/sap/issues"
            className="px-5 py-2.5 bg-amber-500 hover:bg-amber-600 text-white rounded-lg transition text-sm font-medium"
          >
            ⚠️ Validation Issues
          </Link>
          <Link
            to="/sap/approvals"
            className="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition text-sm font-medium"
          >
            ✓ Approval Queue
          </Link>
        </div>
      </div>
    </div>
  )
}

export default SAPDashboardPage