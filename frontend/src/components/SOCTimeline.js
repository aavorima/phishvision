import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import {
  getSOCIncidents,
  getSOCMetrics,
  getSOCTimeline,
  createSOCIncident,
  updateSOCIncidentStatus
} from '../api/api';

function SOCTimeline() {
  const { isDark } = useTheme();
  const [incidents, setIncidents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({ status: '', severity: '', days: 30 });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newIncident, setNewIncident] = useState({
    type: 'phishing_click',
    severity: 'medium',
    description: '',
    user_email: ''
  });

  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-white' : 'text-gray-900';
  const textMuted = isDark ? 'text-gray-400' : 'text-gray-500';
  const borderColor = isDark ? 'border-gray-700' : 'border-gray-200';
  const inputBg = isDark ? 'bg-gray-700 text-white' : 'bg-white text-gray-900';

  useEffect(() => {
    fetchData();
  }, [filter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [incidentsRes, metricsRes] = await Promise.all([
        getSOCIncidents(filter),
        getSOCMetrics(filter.days)
      ]);
      setIncidents(incidentsRes.data.incidents || []);
      setMetrics(metricsRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load SOC data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (incidentId, newStatus) => {
    try {
      await updateSOCIncidentStatus(incidentId, { status: newStatus });
      fetchData();
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleCreateIncident = async () => {
    try {
      await createSOCIncident(newIncident);
      setShowCreateModal(false);
      setNewIncident({ type: 'phishing_click', severity: 'medium', description: '', user_email: '' });
      fetchData();
    } catch (err) {
      console.error('Failed to create incident:', err);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-500',
      high: 'bg-orange-500',
      medium: 'bg-yellow-500',
      low: 'bg-green-500'
    };
    return colors[severity] || 'bg-gray-500';
  };

  const getStatusColor = (status) => {
    const colors = {
      detected: 'text-red-500',
      investigating: 'text-yellow-500',
      contained: 'text-blue-500',
      resolved: 'text-green-500'
    };
    return colors[status] || 'text-gray-500';
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString();
  };

  if (loading && !metrics) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className={`${bgColor} rounded-lg p-8 text-center`}>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className={`mt-4 ${textMuted}`}>Loading SOC data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className={`text-2xl font-bold ${textColor}`}>SOC Timeline</h1>
          <p className={textMuted}>Security Operations Center - Incident Management</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          + New Incident
        </button>
      </div>

      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
            <p className={textMuted + ' text-sm'}>Total Incidents</p>
            <p className={`text-3xl font-bold ${textColor}`}>{metrics.total_incidents}</p>
            <p className={`text-sm ${textMuted}`}>{metrics.active_incidents} active</p>
          </div>
          <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
            <p className={textMuted + ' text-sm'}>MTTR (Minutes)</p>
            <p className={`text-3xl font-bold ${textColor}`}>{metrics.mttr_minutes || 0}</p>
            <p className={`text-sm ${textMuted}`}>Mean Time to Resolve</p>
          </div>
          <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
            <p className={textMuted + ' text-sm'}>Resolution Rate</p>
            <p className={`text-3xl font-bold ${textColor}`}>{metrics.resolution_rate}%</p>
            <p className={`text-sm ${textMuted}`}>{metrics.resolved_incidents} resolved</p>
          </div>
          <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
            <p className={textMuted + ' text-sm'}>Security Posture</p>
            <p className={`text-3xl font-bold ${metrics.security_posture_score >= 70 ? 'text-green-500' : metrics.security_posture_score >= 40 ? 'text-yellow-500' : 'text-red-500'}`}>
              {metrics.security_posture_score}
            </p>
            <p className={`text-sm ${textMuted}`}>Score out of 100</p>
          </div>
        </div>
      )}

      {/* Severity Distribution */}
      {metrics && (
        <div className={`${bgColor} rounded-lg p-4 border ${borderColor} mb-6`}>
          <h3 className={`font-semibold ${textColor} mb-3`}>Severity Distribution</h3>
          <div className="flex space-x-4">
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-red-500 mr-2"></span>
              <span className={textMuted}>Critical: {metrics.severity_counts?.critical || 0}</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-orange-500 mr-2"></span>
              <span className={textMuted}>High: {metrics.severity_counts?.high || 0}</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></span>
              <span className={textMuted}>Medium: {metrics.severity_counts?.medium || 0}</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-green-500 mr-2"></span>
              <span className={textMuted}>Low: {metrics.severity_counts?.low || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className={`${bgColor} rounded-lg p-4 border ${borderColor} mb-6`}>
        <div className="flex flex-wrap gap-4">
          <select
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
            className={`px-3 py-2 rounded border ${borderColor} ${inputBg}`}
          >
            <option value="">All Statuses</option>
            <option value="detected">Detected</option>
            <option value="investigating">Investigating</option>
            <option value="contained">Contained</option>
            <option value="resolved">Resolved</option>
          </select>
          <select
            value={filter.severity}
            onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
            className={`px-3 py-2 rounded border ${borderColor} ${inputBg}`}
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            value={filter.days}
            onChange={(e) => setFilter({ ...filter, days: parseInt(e.target.value) })}
            className={`px-3 py-2 rounded border ${borderColor} ${inputBg}`}
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Timeline */}
      <div className={`${bgColor} rounded-lg border ${borderColor}`}>
        <div className={`p-4 border-b ${borderColor}`}>
          <h3 className={`font-semibold ${textColor}`}>Incident Timeline</h3>
        </div>

        {incidents.length === 0 ? (
          <div className="p-8 text-center">
            <p className={textMuted}>No incidents found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {incidents.map((incident) => (
              <div key={incident.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <span className={`w-3 h-3 rounded-full mt-1.5 ${getSeverityColor(incident.severity)}`}></span>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className={`font-medium ${textColor}`}>{incident.type.replace('_', ' ').toUpperCase()}</span>
                        <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(incident.status)} bg-opacity-20`}>
                          {incident.status}
                        </span>
                      </div>
                      <p className={`${textMuted} text-sm mt-1`}>{incident.description}</p>
                      {incident.user_email && (
                        <p className={`${textMuted} text-xs mt-1`}>User: {incident.user_email}</p>
                      )}
                      <div className={`${textMuted} text-xs mt-2 space-x-4`}>
                        <span>Detected: {formatDate(incident.detected_at)}</span>
                        {incident.acknowledged_at && <span>| Acknowledged: {formatDate(incident.acknowledged_at)}</span>}
                        {incident.resolved_at && <span>| Resolved: {formatDate(incident.resolved_at)}</span>}
                        {incident.response_time_minutes && (
                          <span className="text-green-500">| Response: {incident.response_time_minutes} min</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    {incident.status !== 'resolved' && (
                      <select
                        value={incident.status}
                        onChange={(e) => handleStatusUpdate(incident.id, e.target.value)}
                        className={`text-xs px-2 py-1 rounded border ${borderColor} ${inputBg}`}
                      >
                        <option value="detected">Detected</option>
                        <option value="investigating">Investigating</option>
                        <option value="contained">Contained</option>
                        <option value="resolved">Resolved</option>
                      </select>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Incident Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className={`${bgColor} rounded-lg p-6 w-full max-w-md`}>
            <h3 className={`text-lg font-semibold ${textColor} mb-4`}>Create New Incident</h3>
            <div className="space-y-4">
              <div>
                <label className={`block text-sm ${textMuted} mb-1`}>Type</label>
                <select
                  value={newIncident.type}
                  onChange={(e) => setNewIncident({ ...newIncident, type: e.target.value })}
                  className={`w-full px-3 py-2 rounded border ${borderColor} ${inputBg}`}
                >
                  <option value="phishing_click">Phishing Click</option>
                  <option value="credential_entered">Credential Entered</option>
                  <option value="malware_download">Malware Download</option>
                  <option value="reported_email">Reported Email</option>
                </select>
              </div>
              <div>
                <label className={`block text-sm ${textMuted} mb-1`}>Severity</label>
                <select
                  value={newIncident.severity}
                  onChange={(e) => setNewIncident({ ...newIncident, severity: e.target.value })}
                  className={`w-full px-3 py-2 rounded border ${borderColor} ${inputBg}`}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div>
                <label className={`block text-sm ${textMuted} mb-1`}>User Email (optional)</label>
                <input
                  type="email"
                  value={newIncident.user_email}
                  onChange={(e) => setNewIncident({ ...newIncident, user_email: e.target.value })}
                  className={`w-full px-3 py-2 rounded border ${borderColor} ${inputBg}`}
                  placeholder="user@example.com"
                />
              </div>
              <div>
                <label className={`block text-sm ${textMuted} mb-1`}>Description</label>
                <textarea
                  value={newIncident.description}
                  onChange={(e) => setNewIncident({ ...newIncident, description: e.target.value })}
                  className={`w-full px-3 py-2 rounded border ${borderColor} ${inputBg}`}
                  rows={3}
                  placeholder="Describe the incident..."
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className={`px-4 py-2 rounded border ${borderColor} ${textColor} hover:bg-gray-100 dark:hover:bg-gray-700 transition`}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateIncident}
                disabled={!newIncident.description}
                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition disabled:opacity-50"
              >
                Create Incident
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SOCTimeline;
