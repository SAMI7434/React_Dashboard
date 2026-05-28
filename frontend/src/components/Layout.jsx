import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'

const getNavLinkClass = (isActive, isSection = false) =>
  `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition ${
    isActive
      ? isSection 
        ? 'bg-cyan-500/20 text-cyan-300 shadow-inner border border-cyan-500/30'
        : 'bg-slate-800 text-white shadow-inner'
      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
  }`

const Layout = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  
  // Determine current dashboard type
  const isSAPDashboard = location.pathname.startsWith('/sap')
  const currentDashboard = isSAPDashboard ? 'sap' : 'utility'

  return (
    <div className="min-h-screen text-slate-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <header className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">
              {isSAPDashboard ? 'SAP Procurement Intelligence' : 'Utility Intake Hub'}
            </p>
            <h1 className="text-3xl md:text-4xl font-semibold">
              {isSAPDashboard 
                ? 'Fuel & Procurement Analytics' 
                : 'Electricity Bill Review'}
            </h1>
            <p className="text-slate-400 max-w-2xl">
              {isSAPDashboard
                ? 'Monitor fuel procurement, detect anomalies, and manage approvals across all plants and vendors.'
                : 'Normalize, validate, and lock billing data with an audit-first review workflow.'}
            </p>
          </div>
          <div className="glass-panel rounded-2xl px-5 py-4 flex items-center gap-4">
            <div>
              <p className="text-xs text-slate-400">Signed in as</p>
              <p className="text-sm font-medium">{user?.username || 'Analyst'}</p>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-200 text-sm hover:bg-cyan-500/30 transition"
            >
              Sign out
            </button>
          </div>
        </header>

        {/* Dashboard Switcher */}
        <div className="mt-6 flex gap-2">
          <NavLink
            to="/utility"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              currentDashboard === 'utility'
                ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/25'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
            }`}
          >
            ⚡ Utility Dashboard
          </NavLink>
          <NavLink
            to="/sap"
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              currentDashboard === 'sap'
                ? 'bg-violet-500 text-white shadow-lg shadow-violet-500/25'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
            }`}
          >
            🛢️ SAP Procurement Dashboard
          </NavLink>
        </div>

        <div className="grid lg:grid-cols-[240px_1fr] gap-8 mt-8">
          {/* Sidebar Navigation */}
          <nav className="glass-panel rounded-2xl p-4 space-y-1">
            {/* Dashboard Section */}
            <div className="mb-4">
              <p className="text-xs uppercase tracking-wider text-slate-500 px-3 mb-2 font-medium">
                {isSAPDashboard ? 'SAP Analytics' : 'Utility Analytics'}
              </p>
              <NavLink
                to={isSAPDashboard ? '/sap' : '/utility'}
                className={({ isActive }) => getNavLinkClass(isActive, true)}
                end
              >
                <span>📊</span>
                Dashboard
              </NavLink>
            </div>

            {/* Data Management Section */}
            <div className="mb-4">
              <p className="text-xs uppercase tracking-wider text-slate-500 px-3 mb-2 font-medium">
                Data Management
              </p>
              <NavLink
                to={isSAPDashboard ? '/sap/upload' : '/utility/upload'}
                className={({ isActive }) => getNavLinkClass(isActive)}
              >
                <span>📤</span>
                Upload {isSAPDashboard ? 'SAP Data' : 'CSV'}
              </NavLink>
              <NavLink
                to={isSAPDashboard ? '/sap/records' : '/utility/records'}
                className={({ isActive }) => getNavLinkClass(isActive)}
              >
                <span>📋</span>
                Records Review
              </NavLink>
            </div>

            {/* Quality & Approval Section */}
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-500 px-3 mb-2 font-medium">
                Quality & Approval
              </p>
              <NavLink
                to={isSAPDashboard ? '/sap/issues' : '/utility/issues'}
                className={({ isActive }) => getNavLinkClass(isActive)}
              >
                <span>⚠️</span>
                Validation Issues
              </NavLink>
              {isSAPDashboard && (
                <NavLink
                  to="/sap/approvals"
                  className={({ isActive }) => getNavLinkClass(isActive)}
                >
                  <span>✓</span>
                  Approval Queue
                </NavLink>
              )}
            </div>
          </nav>

          {/* Main Content */}
          <main className="space-y-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}

export default Layout