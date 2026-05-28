import React, { useState, useEffect } from 'react';
import { 
  Users, Plane, Hotel, Car, Train, Briefcase, 
  DollarSign, AlertTriangle, TrendingUp, Calendar 
} from 'lucide-react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell 
} from 'recharts';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [monthlyTrend, setMonthlyTrend] = useState([]);
  const [statusDistribution, setStatusDistribution] = useState([]);
  const [departmentSpend, setDepartmentSpend] = useState([]);
  const [regionBookings, setRegionBookings] = useState([]);
  const [bookingTypeComparison, setBookingTypeComparison] = useState([]);
  const [recentImports, setRecentImports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const [
        analyticsRes, 
        monthlyTrendRes, 
        statusDistRes, 
        deptSpendRes, 
        regionRes, 
        typeCompRes,
        recentImportsRes
      ] = await Promise.all([
        axios.get(`${API_BASE_URL}/travel/dashboard/analytics/`, { headers }),
        axios.get(`${API_BASE_URL}/travel/dashboard/monthly-trend/`, { headers }),
        axios.get(`${API_BASE_URL}/travel/dashboard/status-distribution/`, { headers }),
        axios.get(`${API_BASE_URL}/travel/dashboard/department-spend/`, { headers }),
        axios.get(`${API_BASE_URL}/travel/dashboard/region-bookings/`, { headers }),
        axios.get(`${API_BASE_URL}/travel/dashboard/booking-type-comparison/`, { headers }),
        axios.get(`${API_BASE_URL}/travel/dashboard/recent-imports/`, { headers })
      ]);

      setAnalytics(analyticsRes.data);
      setMonthlyTrend(monthlyTrendRes.data);
      setStatusDistribution(statusDistRes.data);
      setDepartmentSpend(deptSpendRes.data);
      setRegionBookings(regionRes.data);
      setBookingTypeComparison(typeCompRes.data);
      setRecentImports(recentImportsRes.data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      success: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      partial: 'bg-yellow-100 text-yellow-800',
      retry: 'bg-blue-100 text-blue-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <p>Error loading dashboard data: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Travel Management Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Navan TMC Integration</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh Data
        </button>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Synced Users</p>
                <p className="text-2xl font-bold">{analytics.total_synced_users}</p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active Users</p>
                <p className="text-2xl font-bold">{analytics.active_users}</p>
              </div>
              <Users className="h-8 w-8 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Trips</p>
                <p className="text-2xl font-bold">{analytics.total_trips}</p>
              </div>
              <Briefcase className="h-8 w-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Monthly Spend</p>
                <p className="text-2xl font-bold">{formatCurrency(analytics.monthly_travel_spend)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-yellow-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Out of Policy Trips</p>
                <p className="text-2xl font-bold">{analytics.out_of_policy_trips}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
          </div>
        </div>
      )}

      {/* Booking Type Cards */}
      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Flights</p>
                <p className="text-xl font-bold">{analytics.flights}</p>
              </div>
              <Plane className="h-6 w-6 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Hotels</p>
                <p className="text-xl font-bold">{analytics.hotels}</p>
              </div>
              <Hotel className="h-6 w-6 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Rental Cars</p>
                <p className="text-xl font-bold">{analytics.rental_cars}</p>
              </div>
              <Car className="h-6 w-6 text-orange-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Rail</p>
                <p className="text-xl font-bold">{analytics.rail_bookings}</p>
              </div>
              <Train className="h-6 w-6 text-red-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Black Car</p>
                <p className="text-xl font-bold">{analytics.black_car_bookings}</p>
              </div>
              <Briefcase className="h-6 w-6 text-purple-500" />
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Booking Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Monthly Booking Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value, name) => [
                name === 'booking_count' ? value : formatCurrency(value), 
                name === 'booking_count' ? 'Bookings' : 'Amount'
              ]} />
              <Legend />
              <Bar dataKey="booking_count" fill="#0088FE" name="Bookings" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Booking Status Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Booking Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ status, percentage }) => `${status}: ${percentage}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="count"
              >
                {statusDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Department-wise Spend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Department-wise Travel Spend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={departmentSpend} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={formatCurrency} />
              <YAxis type="category" dataKey="department" width={100} />
              <Tooltip formatter={(value) => formatCurrency(value)} />
              <Bar dataKey="total_spend" fill="#00C49F" name="Spend" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Region-wise Bookings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Region-wise Bookings</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={regionBookings}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip formatter={(value, name) => [
                name === 'booking_count' ? value : formatCurrency(value),
                name === 'booking_count' ? 'Bookings' : 'Amount'
              ]} />
              <Legend />
              <Bar dataKey="booking_count" fill="#FFBB28" name="Bookings" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Import Logs */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Import Activity</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Import Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Records
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Completed
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentImports.map((log) => (
                <tr key={log.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {log.import_type_display}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(log.status)}`}>
                      {log.status_display}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    Processed: {log.records_processed} | Created: {log.records_created} | Failed: {log.records_failed}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.completed_at ? formatDate(log.completed_at) : 'In Progress'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;