import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './hooks/useAuth.js'
import Layout from './components/Layout.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import UploadPage from './pages/UploadPage.jsx'
import RecordsPage from './pages/RecordsPage.jsx'
import IssuesPage from './pages/IssuesPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import SAPDashboardPage from './pages/SAPDashboardPage.jsx'
import TravelDashboard from './pages/travel/Dashboard.jsx'
import TravelBookings from './pages/travel/Bookings.jsx'
import UserManagement from './pages/travel/Users.jsx'
import TravelImportLogs from './pages/travel/ImportLogs.jsx'

const RequireAuth = ({ children }) => {
  const { token, isLoading } = useAuth()
  if (isLoading) {
    return <div className="p-8 text-slate-200">Loading session...</div>
  }
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return children
}

const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        {/* Default redirects to Utility Dashboard */}
        <Route index element={<Navigate to="/utility" replace />} />
        
        {/* Utility Dashboard Routes */}
        <Route path="utility" element={<DashboardPage />} />
        <Route path="utility/upload" element={<UploadPage />} />
        <Route path="utility/records" element={<RecordsPage />} />
        <Route path="utility/issues" element={<IssuesPage />} />
        
        {/* SAP Procurement Dashboard Routes */}
        <Route path="sap" element={<SAPDashboardPage />} />
        <Route path="sap/upload" element={<UploadPage sap />} />
        <Route path="sap/records" element={<RecordsPage sap />} />
        <Route path="sap/issues" element={<IssuesPage sap />} />
        
        {/* Travel Management Dashboard Routes */}
        <Route path="travel" element={<TravelDashboard />} />
        <Route path="travel/bookings" element={<TravelBookings />} />
        <Route path="travel/users" element={<UserManagement />} />
        <Route path="travel/imports" element={<TravelImportLogs />} />
      </Route>
    </Routes>
  )
}

export default App