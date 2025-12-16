import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import { getCampaignReport, exportCampaignReport } from '../api/api';

function CampaignReport() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [activeSection, setActiveSection] = useState('overview');

  const bgPrimary = isDark ? 'bg-slate-900' : 'bg-slate-50';
  const bgCard = isDark ? 'bg-slate-800' : 'bg-white';
  const borderColor = isDark ? 'border-slate-700' : 'border-slate-200';
  const textPrimary = isDark ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDark ? 'text-slate-400' : 'text-slate-600';

  useEffect(() => {
    loadReport();
  }, [id]);

  const loadReport = async () => {
    try {
      setLoading(true);
      const response = await getCampaignReport(id);
      setReport(response.data);
    } catch (error) {
      console.error('Error loading campaign report:', error);
      setError(error.response?.data?.error || 'Failed to load campaign report');
    } finally {
      setLoading(false);
    }
  };

  const handleExportJSON = async () => {
    try {
      const response = await exportCampaignReport(id, 'json');
      const dataStr = JSON.stringify(response.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `campaign-report-${id}-${Date.now()}.json`;
      link.click();
    } catch (error) {
      console.error('Error exporting JSON report:', error);
      alert('Failed to export JSON report');
    }
  };

  const handleExportPDF = async () => {
    try {
      // Call the API endpoint directly to get the file
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const url = `${API_BASE_URL}/api/campaigns/${id}/report/export?format=pdf`;

      // Download the file
      const link = document.createElement('a');
      link.href = url;
      link.download = `campaign-report-${id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error exporting PDF report:', error);
      alert('Failed to export PDF document');
    }
  };

  const getRiskLevelColor = (level) => {
    const colors = {
      critical: isDark ? 'bg-red-900/30 text-red-400 border-red-900/50' : 'bg-red-100 text-red-700 border-red-200',
      high: isDark ? 'bg-orange-900/30 text-orange-400 border-orange-900/50' : 'bg-orange-100 text-orange-700 border-orange-200',
      medium: isDark ? 'bg-yellow-900/30 text-yellow-400 border-yellow-900/50' : 'bg-yellow-100 text-yellow-700 border-yellow-200',
      low: isDark ? 'bg-green-900/30 text-green-400 border-green-900/50' : 'bg-green-100 text-green-700 border-green-200',
      positive: isDark ? 'bg-blue-900/30 text-blue-400 border-blue-900/50' : 'bg-blue-100 text-blue-700 border-blue-200'
    };
    return colors[level] || colors.medium;
  };

  const getAwarenessColor = (level) => {
    const colors = {
      'Excellent': isDark ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700',
      'Good': isDark ? 'bg-blue-900/30 text-blue-400' : 'bg-blue-100 text-blue-700',
      'Fair': isDark ? 'bg-yellow-900/30 text-yellow-400' : 'bg-yellow-100 text-yellow-700',
      'Poor': isDark ? 'bg-orange-900/30 text-orange-400' : 'bg-orange-100 text-orange-700',
      'Critical': isDark ? 'bg-red-900/30 text-red-400' : 'bg-red-100 text-red-700'
    };
    return colors[level] || colors.Fair;
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${bgPrimary} p-6 flex items-center justify-center`}>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className={`min-h-screen ${bgPrimary} p-6`}>
        <div className={`${bgCard} border ${borderColor} rounded-xl p-8 text-center max-w-2xl mx-auto`}>
          <svg className={`w-16 h-16 mx-auto mb-4 ${textSecondary}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className={`text-xl font-semibold mb-2 ${textPrimary}`}>Error Loading Report</h2>
          <p className={`mb-6 ${textSecondary}`}>{error}</p>
          <button
            onClick={() => navigate('/campaigns')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition"
          >
            Back to Campaigns
          </button>
        </div>
      </div>
    );
  }

  const sections = [
    { id: 'overview', label: 'Overview' },
    { id: 'awareness', label: 'Awareness Summary' },
    { id: 'employees', label: 'Employee Results' },
    { id: 'departments', label: 'Department Breakdown' },
    { id: 'gaps', label: 'Security Gaps' }
  ];

  return (
    <div className={`min-h-screen ${bgPrimary} p-6`}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/campaigns')}
              className={`p-2 rounded-lg ${isDark ? 'hover:bg-slate-700' : 'hover:bg-slate-100'} transition`}
            >
              <svg className={`w-5 h-5 ${textPrimary}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className={`text-2xl font-semibold ${textPrimary}`}>Campaign Awareness Report</h1>
              <p className={`text-sm mt-1 ${textSecondary}`}>{report.overview.campaign_name}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleExportPDF}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Export as PDF
            </button>
          </div>
        </div>
      </div>

      {/* Section Navigation */}
      <div className={`${bgCard} border ${borderColor} rounded-xl p-2 mb-6`}>
        <div className="flex gap-2 overflow-x-auto">
          {sections.map(section => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition ${
                activeSection === section.id
                  ? 'bg-blue-600 text-white'
                  : isDark
                    ? 'text-slate-400 hover:text-white hover:bg-slate-700'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              {section.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {/* 1. Campaign Overview */}
        {activeSection === 'overview' && (
          <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
            <h2 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Campaign Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <p className={`text-sm ${textSecondary} mb-1`}>Campaign Type</p>
                <p className={`font-medium ${textPrimary}`}>{report.overview.campaign_type}</p>
              </div>
              <div>
                <p className={`text-sm ${textSecondary} mb-1`}>Status</p>
                <span className={`px-2 py-1 rounded-md text-xs font-semibold ${
                  report.overview.status === 'completed'
                    ? (isDark ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700')
                    : (isDark ? 'bg-blue-900/30 text-blue-400' : 'bg-blue-100 text-blue-700')
                }`}>
                  {report.overview.status}
                </span>
              </div>
              <div>
                <p className={`text-sm ${textSecondary} mb-1`}>Total Targets</p>
                <p className={`font-medium ${textPrimary}`}>{report.overview.total_targets}</p>
              </div>
              <div>
                <p className={`text-sm ${textSecondary} mb-1`}>Email Opens</p>
                <p className={`font-medium ${textPrimary}`}>{report.overview.total_opened} ({report.overview.open_rate}%)</p>
              </div>
              <div>
                <p className={`text-sm ${textSecondary} mb-1`}>Link Clicks</p>
                <p className={`font-medium ${textPrimary}`}>{report.overview.total_clicked} ({report.overview.click_rate}%)</p>
              </div>
              {report.overview.duration && (
                <div>
                  <p className={`text-sm ${textSecondary} mb-1`}>Duration</p>
                  <p className={`font-medium ${textPrimary}`}>
                    {report.overview.duration.days}d {report.overview.duration.hours}h {report.overview.duration.minutes}m
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 2. Awareness Summary */}
        {activeSection === 'awareness' && (
          <div>
            {/* Awareness Score Card */}
            <div className={`${bgCard} border ${borderColor} rounded-xl p-6 mb-6`}>
              <div className="text-center">
                <h3 className={`text-sm font-medium mb-2 ${textSecondary}`}>Overall Awareness Score</h3>
                <div className="flex items-center justify-center gap-4 mb-4">
                  <div className={`text-6xl font-bold ${textPrimary}`}>{report.awareness_summary.awareness_score}</div>
                  <div className="text-left">
                    <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${getAwarenessColor(report.awareness_summary.awareness_level)}`}>
                      {report.awareness_summary.awareness_level}
                    </span>
                  </div>
                </div>
                <p className={`text-sm ${textSecondary} max-w-2xl mx-auto`}>{report.awareness_summary.score_explanation}</p>
              </div>
            </div>

            {/* Breakdown */}
            <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
              <h3 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Employee Behavior Breakdown</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className={`p-4 rounded-lg border ${isDark ? 'bg-green-900/10 border-green-900/30' : 'bg-green-50 border-green-200'}`}>
                  <p className={`text-sm ${textSecondary} mb-1`}>No Interaction</p>
                  <p className={`text-2xl font-bold ${isDark ? 'text-green-400' : 'text-green-700'}`}>
                    {report.awareness_summary.no_interaction_percent}%
                  </p>
                  <p className={`text-xs ${textSecondary}`}>{report.awareness_summary.no_interaction_count} employees</p>
                </div>

                <div className={`p-4 rounded-lg border ${isDark ? 'bg-yellow-900/10 border-yellow-900/30' : 'bg-yellow-50 border-yellow-200'}`}>
                  <p className={`text-sm ${textSecondary} mb-1`}>Opened Only</p>
                  <p className={`text-2xl font-bold ${isDark ? 'text-yellow-400' : 'text-yellow-700'}`}>
                    {report.awareness_summary.opened_only_percent}%
                  </p>
                  <p className={`text-xs ${textSecondary}`}>{report.awareness_summary.opened_only_count} employees</p>
                </div>

                <div className={`p-4 rounded-lg border ${isDark ? 'bg-orange-900/10 border-orange-900/30' : 'bg-orange-50 border-orange-200'}`}>
                  <p className={`text-sm ${textSecondary} mb-1`}>Clicked Link</p>
                  <p className={`text-2xl font-bold ${isDark ? 'text-orange-400' : 'text-orange-700'}`}>
                    {report.awareness_summary.clicked_percent}%
                  </p>
                  <p className={`text-xs ${textSecondary}`}>{report.awareness_summary.clicked_count} employees</p>
                </div>

                <div className={`p-4 rounded-lg border ${isDark ? 'bg-red-900/10 border-red-900/30' : 'bg-red-50 border-red-200'}`}>
                  <p className={`text-sm ${textSecondary} mb-1`}>Submitted Credentials</p>
                  <p className={`text-2xl font-bold ${isDark ? 'text-red-400' : 'text-red-700'}`}>
                    {report.awareness_summary.submitted_credentials_percent}%
                  </p>
                  <p className={`text-xs ${textSecondary}`}>{report.awareness_summary.submitted_credentials_count} employees</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 3. Employee Results */}
        {activeSection === 'employees' && (
          <div className={`${bgCard} border ${borderColor} rounded-xl overflow-hidden`}>
            <div className="p-6">
              <h2 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Individual Employee Results</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className={isDark ? 'bg-slate-700/50' : 'bg-slate-50'}>
                  <tr>
                    <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Employee</th>
                    <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Department</th>
                    <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Outcome</th>
                    <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Failed Technique</th>
                    <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>HVS Score</th>
                    <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Training</th>
                  </tr>
                </thead>
                <tbody className={`divide-y ${borderColor}`}>
                  {report.employee_results.map((employee, index) => (
                    <tr key={index} className={isDark ? 'hover:bg-slate-700/30' : 'hover:bg-slate-50'}>
                      <td className="px-6 py-4">
                        <div className={`font-medium ${textPrimary}`}>{employee.name}</div>
                        <div className={`text-sm ${textSecondary}`}>{employee.email}</div>
                      </td>
                      <td className={`px-6 py-4 ${textSecondary}`}>{employee.department}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-md text-xs font-semibold ${getRiskLevelColor(employee.risk_level)}`}>
                          {employee.outcome_label}
                        </span>
                      </td>
                      <td className={`px-6 py-4 text-sm ${textSecondary}`}>{employee.failed_technique || '-'}</td>
                      <td className="px-6 py-4">
                        {employee.current_hvs_score !== null && (
                          <span className={`px-2 py-1 rounded-md text-xs font-semibold ${
                            employee.hvs_level === 'critical'
                              ? (isDark ? 'bg-red-900/30 text-red-400' : 'bg-red-100 text-red-700')
                              : employee.hvs_level === 'high'
                              ? (isDark ? 'bg-orange-900/30 text-orange-400' : 'bg-orange-100 text-orange-700')
                              : employee.hvs_level === 'medium'
                              ? (isDark ? 'bg-yellow-900/30 text-yellow-400' : 'bg-yellow-100 text-yellow-700')
                              : (isDark ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700')
                          }`}>
                            {employee.current_hvs_score}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {employee.training_recommended ? (
                          <span className={`text-xs ${isDark ? 'text-orange-400' : 'text-orange-600'}`}>Recommended</span>
                        ) : (
                          <span className={`text-xs ${textSecondary}`}>-</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 4. Department Breakdown */}
        {activeSection === 'departments' && (
          <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
            <h2 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Department Risk Breakdown</h2>
            <div className="space-y-4">
              {report.department_breakdown.map((dept, index) => (
                <div key={index} className={`p-4 rounded-lg border ${borderColor}`}>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className={`font-semibold ${textPrimary}`}>{dept.department}</h3>
                    <span className={`px-3 py-1 rounded-lg text-xs font-semibold ${getRiskLevelColor(dept.risk_level)}`}>
                      {dept.risk_level.toUpperCase()} RISK
                    </span>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                    <div>
                      <p className={`text-xs ${textSecondary}`}>Employees</p>
                      <p className={`text-lg font-semibold ${textPrimary}`}>{dept.total_employees}</p>
                    </div>
                    <div>
                      <p className={`text-xs ${textSecondary}`}>Click Rate</p>
                      <p className={`text-lg font-semibold ${textPrimary}`}>{dept.click_rate}%</p>
                    </div>
                    <div>
                      <p className={`text-xs ${textSecondary}`}>Open Rate</p>
                      <p className={`text-lg font-semibold ${textPrimary}`}>{dept.open_rate}%</p>
                    </div>
                    <div>
                      <p className={`text-xs ${textSecondary}`}>Avg HVS</p>
                      <p className={`text-lg font-semibold ${textPrimary}`}>{dept.avg_hvs_score}</p>
                    </div>
                  </div>
                  <div className="w-full bg-slate-600/20 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        dept.risk_level === 'critical' ? 'bg-red-500' :
                        dept.risk_level === 'high' ? 'bg-orange-500' :
                        dept.risk_level === 'medium' ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${dept.click_rate}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 5. Security Gaps */}
        {activeSection === 'gaps' && (
          <div>
            {/* Summary */}
            <div className={`${bgCard} border ${borderColor} rounded-xl p-6 mb-6`}>
              <h2 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Executive Summary</h2>
              <div className={`p-4 rounded-lg ${isDark ? 'bg-slate-700/50' : 'bg-slate-50'}`}>
                <p className={textPrimary}>{report.security_gaps.summary}</p>
              </div>
            </div>

            {/* Gap Details */}
            <div className={`${bgCard} border ${borderColor} rounded-xl p-6`}>
              <h2 className={`text-lg font-semibold mb-4 ${textPrimary}`}>Identified Security Gaps</h2>
              <div className="space-y-4">
                {report.security_gaps.gaps.map((gap, index) => (
                  <div key={index} className={`p-4 rounded-lg border ${getRiskLevelColor(gap.severity)}`}>
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0">
                        {gap.severity === 'critical' && (
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                          </svg>
                        )}
                        {gap.severity === 'high' && (
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        )}
                        {gap.severity === 'positive' && (
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-semibold uppercase">{gap.category}</span>
                          <span className="text-xs opacity-75">•</span>
                          <span className="text-xs font-semibold uppercase">{gap.severity}</span>
                        </div>
                        <p className="font-medium mb-2">{gap.finding}</p>
                        <p className="text-sm opacity-90">{gap.recommendation}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CampaignReport;
