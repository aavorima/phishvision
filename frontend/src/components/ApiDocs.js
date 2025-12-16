import React, { useState } from 'react';
import { useTheme } from '../ThemeContext';

const apiEndpoints = [
  {
    category: 'Authentication',
    endpoints: [
      { method: 'POST', path: '/api/auth/register', description: 'Register a new user account' },
      { method: 'POST', path: '/api/auth/login', description: 'Login and create session' },
      { method: 'POST', path: '/api/auth/logout', description: 'Logout and destroy session' },
      { method: 'GET', path: '/api/auth/me', description: 'Get current logged in user' },
      { method: 'PUT', path: '/api/auth/me', description: 'Update user profile' },
      { method: 'POST', path: '/api/auth/change-password', description: 'Change user password' }
    ]
  },
  {
    category: 'Campaigns',
    endpoints: [
      { method: 'GET', path: '/api/campaigns/', description: 'List all email phishing campaigns' },
      { method: 'GET', path: '/api/campaigns/:id', description: 'Get campaign details by ID' },
      { method: 'POST', path: '/api/campaigns/', description: 'Create and launch a new campaign' },
      { method: 'PUT', path: '/api/campaigns/:id/status', description: 'Update campaign status' },
      { method: 'DELETE', path: '/api/campaigns/:id', description: 'Delete a campaign' }
    ]
  },
  {
    category: 'Email Analyzer',
    endpoints: [
      { method: 'POST', path: '/api/analyzer/analyze', description: 'Analyze email for phishing indicators' },
      { method: 'GET', path: '/api/analyzer/history', description: 'Get analysis history' },
      { method: 'GET', path: '/api/analyzer/:id', description: 'Get specific analysis result' },
      { method: 'GET', path: '/api/analyzer/stats', description: 'Get analyzer statistics' },
      { method: 'DELETE', path: '/api/analyzer/history', description: 'Clear analysis history' }
    ]
  },
  {
    category: 'Templates',
    endpoints: [
      { method: 'GET', path: '/api/templates', description: 'List all email templates' },
      { method: 'GET', path: '/api/templates/:id', description: 'Get template by ID' },
      { method: 'POST', path: '/api/templates', description: 'Create a new template' },
      { method: 'PUT', path: '/api/templates/:id', description: 'Update a template' },
      { method: 'DELETE', path: '/api/templates/:id', description: 'Delete a template' },
      { method: 'POST', path: '/api/templates/:id/preview', description: 'Preview template with variables' },
      { method: 'POST', path: '/api/templates/generate-ai', description: 'Generate template using AI' }
    ]
  },
  {
    category: 'Landing Pages',
    endpoints: [
      { method: 'GET', path: '/api/landing/pages', description: 'List all credential harvesting pages' },
      { method: 'GET', path: '/api/landing/pages/:id', description: 'Get landing page by ID' },
      { method: 'POST', path: '/api/landing/pages', description: 'Create a new landing page' },
      { method: 'PUT', path: '/api/landing/pages/:id', description: 'Update a landing page' },
      { method: 'DELETE', path: '/api/landing/pages/:id', description: 'Delete a landing page' },
      { method: 'POST', path: '/api/landing/clone', description: 'Clone a website' },
      { method: 'GET', path: '/api/landing/pages/:id/captures', description: 'Get credential capture events' }
    ]
  },
  {
    category: 'QR Phishing',
    endpoints: [
      { method: 'GET', path: '/api/qr/campaigns', description: 'List QR code campaigns' },
      { method: 'GET', path: '/api/qr/campaigns/:id', description: 'Get QR campaign details' },
      { method: 'POST', path: '/api/qr/campaigns', description: 'Create QR phishing campaign' },
      { method: 'PUT', path: '/api/qr/campaigns/:id', description: 'Update QR campaign' },
      { method: 'DELETE', path: '/api/qr/campaigns/:id', description: 'Delete QR campaign' },
      { method: 'POST', path: '/api/qr/generate', description: 'Generate QR code image' },
      { method: 'GET', path: '/api/qr/stats', description: 'Get QR phishing statistics' }
    ]
  },
  {
    category: 'SMS Phishing',
    endpoints: [
      { method: 'GET', path: '/api/sms/campaigns', description: 'List SMS campaigns' },
      { method: 'GET', path: '/api/sms/campaigns/:id', description: 'Get SMS campaign details' },
      { method: 'POST', path: '/api/sms/campaigns', description: 'Create SMS phishing campaign' },
      { method: 'PUT', path: '/api/sms/campaigns/:id', description: 'Update SMS campaign' },
      { method: 'DELETE', path: '/api/sms/campaigns/:id', description: 'Delete SMS campaign' },
      { method: 'POST', path: '/api/sms/campaigns/:id/send', description: 'Send SMS campaign' }
    ]
  },
  {
    category: 'Employees',
    endpoints: [
      { method: 'GET', path: '/api/employees/', description: 'List all employees' },
      { method: 'GET', path: '/api/employees/:id', description: 'Get employee by ID' },
      { method: 'POST', path: '/api/employees/', description: 'Create a new employee' },
      { method: 'POST', path: '/api/employees/bulk', description: 'Bulk create employees' },
      { method: 'PUT', path: '/api/employees/:id', description: 'Update an employee' },
      { method: 'DELETE', path: '/api/employees/:id', description: 'Delete an employee' }
    ]
  },
  {
    category: 'Risk Scoring',
    endpoints: [
      { method: 'GET', path: '/api/risk/users', description: 'Get users with risk scores' },
      { method: 'GET', path: '/api/risk/users/:id', description: 'Get user risk profile' },
      { method: 'POST', path: '/api/risk/users', description: 'Create/update risk profile' },
      { method: 'POST', path: '/api/risk/recalculate-all', description: 'Recalculate all risk scores' },
      { method: 'GET', path: '/api/risk/stats', description: 'Get risk statistics' },
      { method: 'GET', path: '/api/risk/heatmap', description: 'Get risk heatmap data' }
    ]
  },
  {
    category: 'SOC Incidents',
    endpoints: [
      { method: 'GET', path: '/api/soc/incidents', description: 'List security incidents' },
      { method: 'GET', path: '/api/soc/incidents/:id', description: 'Get incident details' },
      { method: 'POST', path: '/api/soc/incidents', description: 'Create a new incident' },
      { method: 'PUT', path: '/api/soc/incidents/:id/status', description: 'Update incident status' },
      { method: 'DELETE', path: '/api/soc/incidents/:id', description: 'Delete an incident' },
      { method: 'GET', path: '/api/soc/timeline', description: 'Get incident timeline' },
      { method: 'GET', path: '/api/soc/metrics', description: 'Get SOC metrics' }
    ]
  },
  {
    category: 'Settings',
    endpoints: [
      { method: 'GET', path: '/api/settings/', description: 'Get user settings' },
      { method: 'PUT', path: '/api/settings/', description: 'Update user settings' },
      { method: 'POST', path: '/api/settings/smtp/test', description: 'Test SMTP connection' },
      { method: 'POST', path: '/api/settings/smtp/send-test', description: 'Send test email' }
    ]
  }
];

function ApiDocs() {
  const { isDark } = useTheme();
  const [expandedCategory, setExpandedCategory] = useState('Authentication');

  const bgColor = isDark ? 'bg-slate-900' : 'bg-slate-50';
  const cardBg = isDark ? 'bg-slate-800' : 'bg-white';
  const borderColor = isDark ? 'border-slate-700' : 'border-slate-200';
  const textColor = isDark ? 'text-white' : 'text-slate-900';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';

  const methodColors = {
    GET: 'bg-green-500/20 text-green-500',
    POST: 'bg-blue-500/20 text-blue-500',
    PUT: 'bg-yellow-500/20 text-yellow-500',
    DELETE: 'bg-red-500/20 text-red-500'
  };

  return (
    <div className={`min-h-screen ${bgColor} p-6`}>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className={`text-2xl font-bold ${textColor}`}>API Documentation</h1>
          <p className={`${textMuted} mt-2`}>
            Complete reference for the PhishVision REST API. All endpoints are prefixed with the base URL.
          </p>
        </div>

        {/* Base URL */}
        <div className={`${cardBg} rounded-xl p-4 mb-6`}>
          <h3 className={`text-sm font-medium ${textMuted} mb-2`}>Base URL</h3>
          <code className={`text-sm ${textColor} bg-slate-700/50 px-3 py-1.5 rounded`}>
            http://localhost:5000/api
          </code>
        </div>

        {/* API Endpoints */}
        <div className="space-y-4">
          {apiEndpoints.map((category) => (
            <div key={category.category} className={`${cardBg} rounded-xl overflow-hidden`}>
              <button
                onClick={() => setExpandedCategory(
                  expandedCategory === category.category ? null : category.category
                )}
                className={`w-full flex items-center justify-between p-4 ${textColor} hover:bg-slate-700/30 transition-colors`}
              >
                <span className="font-semibold">{category.category}</span>
                <div className="flex items-center gap-3">
                  <span className={`text-sm ${textMuted}`}>{category.endpoints.length} endpoints</span>
                  <svg
                    className={`w-5 h-5 transition-transform ${expandedCategory === category.category ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {expandedCategory === category.category && (
                <div className={`border-t ${borderColor}`}>
                  {category.endpoints.map((endpoint, index) => (
                    <div
                      key={index}
                      className={`flex items-center gap-4 p-4 ${index > 0 ? `border-t ${borderColor}` : ''}`}
                    >
                      <span className={`px-2.5 py-1 text-xs font-bold rounded ${methodColors[endpoint.method]}`}>
                        {endpoint.method}
                      </span>
                      <code className={`flex-1 text-sm ${textColor}`}>{endpoint.path}</code>
                      <span className={`text-sm ${textMuted}`}>{endpoint.description}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Notes */}
        <div className={`${cardBg} rounded-xl p-6 mt-8`}>
          <h3 className={`text-lg font-semibold ${textColor} mb-4`}>Notes</h3>
          <ul className={`space-y-2 text-sm ${textMuted}`}>
            <li>All endpoints require authentication except /api/auth/login and /api/auth/register</li>
            <li>Session-based authentication is used with cookies</li>
            <li>All request/response bodies use JSON format</li>
            <li>Timestamps are returned in ISO 8601 format</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default ApiDocs;
