import React, { useState, useEffect } from 'react';
import { FileText, RefreshCw, AlertCircle, CheckCircle, Clock, XCircle, Play } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const ImportLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    import_type: '',
    status: ''
  });
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  });
  const [selectedLog, setSelectedLog] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, [pagination.page, pagination.pageSize, filters]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const params = {
        page: pagination.page,
        page_size: pagination.pageSize
      };

      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params[key] = filters[key];
        }
      });

      const response = await axios.get(`${API_BASE_URL}/travel/import-logs/`, { headers, params });
      
      setLogs(response.data.results || response.data);
      setPagination(prev => ({
        ...prev,
        total: response.data.count || response.data.length,
        totalPages: Math.ceil((response.data.count || response.data.length) / pagination.pageSize)
      }));
    } catch (err) {
      setError(err.message);
      console.error('Error fetching import logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const handleRetry = async (logId) => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Determine which endpoint to call based on import type
      const endpointMap = {
        'users': 'import/sync-users/',
        'bookings': 'import/bookings/',
        'trips': 'import/bookings/',
        'reconciliation': 'import/reconciliation/'
      };

      const endpoint = endpointMap[filters.import_type] || 'import/bookings/';
      
      await axios.post(`${API_BASE_URL}/travel/${endpoint}`, {}, { headers });
      
      fetchLogs();
    } catch (err) {
      console.error('Error retrying import:', err);
    }
  };

  const handleImport = async (type) => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const endpointMap = {
        'users': 'import/sync-users/',
        'bookings': 'import/bookings/',
        'reconciliation': 'import/reconciliation/'
      };

      const endpoint = endpointMap[type];
      if (!endpoint) return;
      
      await axios.post(`${API_BASE_URL}/travel/${endpoint}`, {}, { headers });
      
      fetchLogs();
    } catch (err) {
      console.error('Error triggering import:', err);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'partial':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'retry':
        return <Clock className="h-5 w-5 text-blue-500" />;
      default:
        return <FileText className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadgeClass = (status) => {
    const classes = {
      success: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      partial: 'bg-yellow-100 text-yellow-800',
      retry: 'bg-blue-100 text-blue-800'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  };

  const getImportTypeBadgeClass = (type) => {
    const classes = {
      users: 'bg-purple-100 text-purple-800',
      bookings: 'bg-blue-100 text-blue-800',
      trips: 'bg-green-100 text-green-800',
      reconciliation: 'bg-orange-100 text-orange-800'
    };
    return classes[type] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '-';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
  };

  const viewDetails = (log) => {
    setSelectedLog(log);
    setShowDetails(true);
  };

  // Summary statistics
  const stats = {
    total: pagination.total,
    success: logs.filter(l => l.status === 'success').length,
    failed: logs.filter(l => l.status === 'failed').length,
    partial: logs.filter(l => l.status === 'partial').length
  };

  if (loading && logs.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Import Logs</h1>
          <p className="text-sm text-gray-500 mt-1">Monitor data import operations from Navan TMC</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleImport('users')}
            className="flex items-center px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
          >
            <Play className="h-4 w-4 mr-1" />
            Sync Users
          </button>
          <button
            onClick={() => handleImport('bookings')}
            className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            <Play className="h-4 w-4 mr-1" />
            Import Bookings
          </button>
          <button
            onClick={() => handleImport('reconciliation')}
            className="flex items-center px-3 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm"
          >
            <Play className="h-4 w-4 mr-1" />
            Reconcile
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Imports</p>
              <p className="text-2xl font-bold">{stats.total}</p>
            </div>
            <FileText className="h-8 w-8 text-gray-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Successful</p>
              <p className="text-2xl font-bold text-green-600">{stats.success}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Failed</p>
              <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
            </div>
            <XCircle className="h-8 w-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Partial Success</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.partial}</p>
            </div>
            <AlertCircle className="h-8 w-8 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Import Type</label>
            <select
              value={filters.import_type}
              onChange={(e) => handleFilterChange('import_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="users">User Sync</option>
              <option value="bookings">Booking Import</option>
              <option value="trips">Trip Import</option>
              <option value="reconciliation">Reconciliation</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="partial">Partial Success</option>
              <option value="retry">Retry</option>
            </select>
          </div>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
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
                  Started
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => viewDetails(log)}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getImportTypeBadgeClass(log.import_type)}`}>
                      {log.import_type_display}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getStatusIcon(log.status)}
                      <span className={`ml-2 text-sm font-medium ${getStatusBadgeClass(log.status)}`}>
                        {log.status_display}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>Processed: {log.records_processed}</div>
                    <div className="text-xs text-gray-400">
                      Created: {log.records_created} | Updated: {log.records_updated} | Failed: {log.records_failed}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(log.started_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDuration(log.duration_seconds)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRetry(log.id);
                      }}
                      className="text-blue-600 hover:text-blue-800 flex items-center"
                    >
                      <RefreshCw className="h-4 w-4 mr-1" />
                      Retry
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
              disabled={pagination.page === 1}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-700">
              Page {pagination.page} of {pagination.totalPages || 1}
            </span>
            <button
              onClick={() => setPagination(prev => ({ ...prev, page: Math.min(pagination.totalPages, prev.page + 1) }))}
              disabled={pagination.page >= pagination.totalPages}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
          <select
            value={pagination.pageSize}
            onChange={(e) => setPagination(prev => ({ ...prev, pageSize: Number(e.target.value), page: 1 }))}
            className="border border-gray-300 rounded-md px-3 py-1 text-sm"
          >
            <option value={10}>10 per page</option>
            <option value={20}>20 per page</option>
            <option value={50}>50 per page</option>
            <option value={100}>100 per page</option>
          </select>
        </div>
      </div>

      {/* Details Modal */}
      {showDetails && selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Import Log Details</h2>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-500">Import Type</p>
                  <p className="font-medium">{selectedLog.import_type_display}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusBadgeClass(selectedLog.status)}`}>
                    {selectedLog.status_display}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Started At</p>
                  <p className="font-medium">{formatDate(selectedLog.started_at)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Completed At</p>
                  <p className="font-medium">
                    {selectedLog.completed_at ? formatDate(selectedLog.completed_at) : 'In Progress'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Duration</p>
                  <p className="font-medium">{formatDuration(selectedLog.duration_seconds)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Records Processed</p>
                  <p className="font-medium">{selectedLog.records_processed}</p>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-sm text-green-600">Created</p>
                  <p className="text-xl font-bold text-green-700">{selectedLog.records_created}</p>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-blue-600">Updated</p>
                  <p className="text-xl font-bold text-blue-700">{selectedLog.records_updated}</p>
                </div>
                <div className="bg-red-50 p-3 rounded-lg">
                  <p className="text-sm text-red-600">Failed</p>
                  <p className="text-xl font-bold text-red-700">{selectedLog.records_failed}</p>
                </div>
              </div>

              {selectedLog.error_message && (
                <div className="mb-6">
                  <p className="text-sm text-gray-500 mb-2">Error Message</p>
                  <div className="bg-red-50 border border-red-200 text-red-800 p-3 rounded-lg">
                    {selectedLog.error_message}
                  </div>
                </div>
              )}

              {selectedLog.validation_errors && selectedLog.validation_errors.length > 0 && (
                <div className="mb-6">
                  <p className="text-sm text-gray-500 mb-2">Validation Errors</p>
                  <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg max-h-48 overflow-y-auto">
                    <pre className="text-xs text-yellow-800">
                      {JSON.stringify(selectedLog.validation_errors, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => handleRetry(selectedLog.id)}
                  className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry Import
                </button>
                <button
                  onClick={() => setShowDetails(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImportLogs;