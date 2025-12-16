import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import { getEmployees, createEmployee, createEmployeesBulk, updateEmployee, deleteEmployee, getEmployeeDepartments, getEmployeeStats, getHVSDepartments } from '../api/api';
import ConfirmDialog from './ConfirmDialog';

function EmployeeManager() {
  const { isDark } = useTheme();
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [stats, setStats] = useState(null);
  const [departmentHVS, setDepartmentHVS] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [employeeToDelete, setEmployeeToDelete] = useState(null);

  // Theme colors
  const bgPrimary = isDark ? 'bg-slate-900' : 'bg-slate-50';
  const bgCard = isDark ? 'bg-slate-800' : 'bg-white';
  const borderColor = isDark ? 'border-slate-700' : 'border-slate-200';
  const textPrimary = isDark ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDark ? 'text-slate-400' : 'text-slate-600';

  useEffect(() => {
    loadData();
  }, [searchQuery, filterDepartment]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [empResponse, deptResponse, statsResponse, hvsDeptsResponse] = await Promise.all([
        getEmployees({ search: searchQuery, department: filterDepartment }),
        getEmployeeDepartments(),
        getEmployeeStats(),
        getHVSDepartments()
      ]);
      setEmployees(empResponse.data);
      setDepartments(deptResponse.data);
      setStats(statsResponse.data);
      setDepartmentHVS(hvsDeptsResponse.data);
    } catch (error) {
      console.error('Error loading employees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteEmployee(employeeToDelete.id);
      setShowDeleteDialog(false);
      setEmployeeToDelete(null);
      loadData();
    } catch (error) {
      console.error('Error deleting employee:', error);
    }
  };

  return (
    <div className={`min-h-screen ${bgPrimary} p-6`}>
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className={`text-2xl font-semibold ${textPrimary}`}>Employee Directory</h1>
            <p className={`text-sm mt-1 ${textSecondary}`}>Manage your organization's employees for phishing campaigns</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowImportModal(true)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition border ${borderColor} ${textPrimary} ${isDark ? 'hover:bg-slate-700' : 'hover:bg-slate-100'}`}
            >
              Import CSV
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition"
            >
              Add Employee
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <StatCard title="Total Employees" value={stats.total} isDark={isDark} />
          <StatCard title="Active" value={stats.active} color="green" isDark={isDark} />
          <StatCard title="Inactive" value={stats.inactive} color="red" isDark={isDark} />
          <StatCard title="Departments" value={Object.keys(stats.by_department || {}).length} color="blue" isDark={isDark} />
        </div>
      )}

      {/* Department Vulnerability Ranking */}
      {departmentHVS.length > 0 && (
        <div className={`${bgCard} border ${borderColor} rounded-xl p-6 mb-6`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className={`text-lg font-semibold ${textPrimary}`}>Department Vulnerability Ranking</h2>
              <p className={`text-sm ${textSecondary}`}>Departments ranked by average Human Vulnerability Score (highest risk first)</p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-red-900/30' : 'bg-red-100'}`}></div>
                <span className={textSecondary}>Critical (75+)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-orange-900/30' : 'bg-orange-100'}`}></div>
                <span className={textSecondary}>High (50-74)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-yellow-900/30' : 'bg-yellow-100'}`}></div>
                <span className={textSecondary}>Medium (25-49)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${isDark ? 'bg-green-900/30' : 'bg-green-100'}`}></div>
                <span className={textSecondary}>Low (0-24)</span>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {departmentHVS.slice(0, 6).map((dept, index) => (
              <div key={dept.department} className={`${isDark ? 'bg-slate-700/30' : 'bg-slate-50'} rounded-lg p-4 border ${borderColor}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-lg font-bold ${textSecondary}`}>#{index + 1}</span>
                    <h3 className={`font-semibold ${textPrimary}`}>{dept.department}</h3>
                  </div>
                  <span className={`px-2 py-1 rounded-md text-xs font-semibold ${
                    dept.hvs_level === 'critical'
                      ? (isDark ? 'bg-red-900/30 text-red-400' : 'bg-red-100 text-red-700')
                      : dept.hvs_level === 'high'
                      ? (isDark ? 'bg-orange-900/30 text-orange-400' : 'bg-orange-100 text-orange-700')
                      : dept.hvs_level === 'medium'
                      ? (isDark ? 'bg-yellow-900/30 text-yellow-400' : 'bg-yellow-100 text-yellow-700')
                      : (isDark ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700')
                  }`}>
                    {dept.avg_hvs_score}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className={textSecondary}>{dept.employee_count} employees</span>
                  <span className={`text-xs ${textSecondary}`}>
                    Range: {dept.min_hvs_score} - {dept.max_hvs_score}
                  </span>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-slate-600/20 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        dept.hvs_level === 'critical' ? 'bg-red-500' :
                        dept.hvs_level === 'high' ? 'bg-orange-500' :
                        dept.hvs_level === 'medium' ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${dept.avg_hvs_score}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {departmentHVS.length > 6 && (
            <div className="mt-4 text-center">
              <button
                className={`text-sm ${isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700'} font-medium`}
                onClick={() => {/* Could expand to show all departments */}}
              >
                View all {departmentHVS.length} departments →
              </button>
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <div className={`${bgCard} border ${borderColor} rounded-xl p-4 mb-6`}>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by name, email, department..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={`w-full px-4 py-2 rounded-lg border ${borderColor} ${isDark ? 'bg-slate-700 text-slate-50' : 'bg-white text-slate-900'} focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
            />
          </div>
          <div className="w-full md:w-48">
            <select
              value={filterDepartment}
              onChange={(e) => setFilterDepartment(e.target.value)}
              className={`w-full px-4 py-2 rounded-lg border ${borderColor} ${isDark ? 'bg-slate-700 text-slate-50' : 'bg-white text-slate-900'}`}
            >
              <option value="">All Departments</option>
              {departments.map((dept) => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Employee Table */}
      <div className={`${bgCard} border ${borderColor} rounded-xl overflow-hidden`}>
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
          </div>
        ) : employees.length === 0 ? (
          <div className="text-center py-16">
            <svg className={`w-16 h-16 mx-auto mb-4 ${textSecondary}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <h3 className={`text-lg font-medium mb-2 ${textPrimary}`}>No employees yet</h3>
            <p className={`text-sm mb-6 ${textSecondary}`}>Add employees to start creating targeted phishing campaigns</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition"
            >
              Add First Employee
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className={isDark ? 'bg-slate-700/50' : 'bg-slate-50'}>
                <tr>
                  <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Employee</th>
                  <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Department</th>
                  <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Job Title</th>
                  <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>HVS Score</th>
                  <th className={`px-6 py-3 text-left text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Status</th>
                  <th className={`px-6 py-3 text-right text-xs font-semibold ${textSecondary} uppercase tracking-wider`}>Actions</th>
                </tr>
              </thead>
              <tbody className={`divide-y ${borderColor}`}>
                {employees.map((employee) => (
                  <tr key={employee.id} className={isDark ? 'hover:bg-slate-700/30' : 'hover:bg-slate-50'}>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-white ${getAvatarColor(employee.first_name)}`}>
                          {employee.first_name[0]}{employee.last_name[0]}
                        </div>
                        <div className="ml-4">
                          <div className={`font-medium ${textPrimary}`}>{employee.full_name}</div>
                          <div className={`text-sm ${textSecondary}`}>{employee.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className={`px-6 py-4 ${textSecondary}`}>{employee.department || '-'}</td>
                    <td className={`px-6 py-4 ${textSecondary}`}>{employee.job_title || '-'}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded-md text-xs font-semibold ${
                          employee.hvs_score >= 75
                            ? (isDark ? 'bg-red-900/30 text-red-400' : 'bg-red-100 text-red-700')
                            : employee.hvs_score >= 50
                            ? (isDark ? 'bg-orange-900/30 text-orange-400' : 'bg-orange-100 text-orange-700')
                            : employee.hvs_score >= 25
                            ? (isDark ? 'bg-yellow-900/30 text-yellow-400' : 'bg-yellow-100 text-yellow-700')
                            : (isDark ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700')
                        }`}>
                          {employee.hvs_score || 0}
                        </span>
                        <span className={`text-xs ${textSecondary}`}>
                          {employee.hvs_level === 'critical' ? 'Critical' : employee.hvs_level === 'high' ? 'High' : employee.hvs_level === 'medium' ? 'Medium' : 'Low'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                        employee.is_active
                          ? (isDark ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700')
                          : (isDark ? 'bg-red-900/30 text-red-400' : 'bg-red-100 text-red-700')
                      }`}>
                        {employee.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => setEditingEmployee(employee)}
                        className={`text-sm font-medium ${isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-800'} mr-4`}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => { setEmployeeToDelete(employee); setShowDeleteDialog(true); }}
                        className={`text-sm font-medium ${isDark ? 'text-red-400 hover:text-red-300' : 'text-red-600 hover:text-red-800'}`}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      {(showAddModal || editingEmployee) && (
        <EmployeeModal
          employee={editingEmployee}
          onClose={() => { setShowAddModal(false); setEditingEmployee(null); }}
          onSave={() => { setShowAddModal(false); setEditingEmployee(null); loadData(); }}
          isDark={isDark}
        />
      )}

      {/* Import Modal */}
      {showImportModal && (
        <ImportModal
          onClose={() => setShowImportModal(false)}
          onSuccess={() => { setShowImportModal(false); loadData(); }}
          isDark={isDark}
        />
      )}

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        title="Delete Employee"
        message={`Are you sure you want to delete ${employeeToDelete?.full_name}? This action cannot be undone.`}
        onConfirm={handleDelete}
        onCancel={() => { setShowDeleteDialog(false); setEmployeeToDelete(null); }}
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />
    </div>
  );
}

function StatCard({ title, value, color = 'default', isDark }) {
  const colors = {
    default: isDark ? 'text-slate-50' : 'text-slate-900',
    green: 'text-green-500',
    red: 'text-red-500',
    blue: 'text-blue-500',
  };

  return (
    <div className={`${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'} border rounded-xl p-4`}>
      <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>{title}</p>
      <p className={`text-3xl font-bold mt-1 ${colors[color]}`}>{value}</p>
    </div>
  );
}

function getAvatarColor(name) {
  const colors = [
    'bg-blue-600', 'bg-green-600', 'bg-purple-600', 'bg-orange-600',
    'bg-pink-600', 'bg-teal-600', 'bg-indigo-600', 'bg-red-600'
  ];
  const index = name.charCodeAt(0) % colors.length;
  return colors[index];
}

function EmployeeModal({ employee, onClose, onSave, isDark }) {
  const [formData, setFormData] = useState({
    email: employee?.email || '',
    first_name: employee?.first_name || '',
    last_name: employee?.last_name || '',
    department: employee?.department || '',
    job_title: employee?.job_title || '',
    phone: employee?.phone || '',
    manager_email: employee?.manager_email || '',
    employee_id: employee?.employee_id || '',
    is_active: employee?.is_active ?? true,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const bgCard = isDark ? 'bg-slate-800' : 'bg-white';
  const borderColor = isDark ? 'border-slate-700' : 'border-slate-200';
  const textPrimary = isDark ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDark ? 'text-slate-400' : 'text-slate-600';
  const inputBg = isDark ? 'bg-slate-700 border-slate-600 text-slate-50' : 'bg-white border-slate-300 text-slate-900';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (employee) {
        await updateEmployee(employee.id, formData);
      } else {
        await createEmployee(formData);
      }
      onSave();
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className={`${bgCard} border ${borderColor} rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto`}>
        <div className={`px-6 py-4 border-b ${borderColor} flex items-center justify-between`}>
          <h2 className={`text-lg font-semibold ${textPrimary}`}>
            {employee ? 'Edit Employee' : 'Add Employee'}
          </h2>
          <button onClick={onClose} className={`text-2xl ${textSecondary} hover:opacity-70`}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className={`p-3 rounded-lg text-sm ${isDark ? 'bg-red-900/30 text-red-400' : 'bg-red-100 text-red-700'}`}>
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>First Name *</label>
              <input
                type="text"
                required
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className={`w-full px-3 py-2 rounded-lg border ${inputBg} focus:ring-2 focus:ring-blue-500`}
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Last Name *</label>
              <input
                type="text"
                required
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className={`w-full px-3 py-2 rounded-lg border ${inputBg} focus:ring-2 focus:ring-blue-500`}
              />
            </div>
          </div>

          <div>
            <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Email *</label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className={`w-full px-3 py-2 rounded-lg border ${inputBg} focus:ring-2 focus:ring-blue-500`}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Department</label>
              <input
                type="text"
                value={formData.department}
                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                className={`w-full px-3 py-2 rounded-lg border ${inputBg} focus:ring-2 focus:ring-blue-500`}
                placeholder="e.g., Engineering"
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Job Title</label>
              <input
                type="text"
                value={formData.job_title}
                onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                className={`w-full px-3 py-2 rounded-lg border ${inputBg} focus:ring-2 focus:ring-blue-500`}
                placeholder="e.g., Software Engineer"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Phone</label>
              <input
                type="text"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className={`w-full px-3 py-2 rounded-lg border ${inputBg} focus:ring-2 focus:ring-blue-500`}
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Employee ID</label>
              <input
                type="text"
                value={formData.employee_id}
                onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                className={`w-full px-3 py-2 rounded-lg border ${inputBg} focus:ring-2 focus:ring-blue-500`}
              />
            </div>
          </div>

          <div>
            <label className={`block text-sm font-medium mb-1 ${textPrimary}`}>Manager Email</label>
            <input
              type="email"
              value={formData.manager_email}
              onChange={(e) => setFormData({ ...formData, manager_email: e.target.value })}
              className={`w-full px-3 py-2 rounded-lg border ${inputBg} focus:ring-2 focus:ring-blue-500`}
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="is_active" className={`ml-2 text-sm ${textPrimary}`}>Active Employee</label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 rounded-lg font-medium text-sm transition"
            >
              {submitting ? 'Saving...' : (employee ? 'Update Employee' : 'Add Employee')}
            </button>
            <button
              type="button"
              onClick={onClose}
              className={`px-6 py-2 rounded-lg font-medium text-sm transition border ${borderColor} ${textPrimary} ${isDark ? 'hover:bg-slate-700' : 'hover:bg-slate-100'}`}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ImportModal({ onClose, onSuccess, isDark }) {
  const [csvData, setCsvData] = useState('');
  const [parsedEmployees, setParsedEmployees] = useState([]);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);

  const bgCard = isDark ? 'bg-slate-800' : 'bg-white';
  const borderColor = isDark ? 'border-slate-700' : 'border-slate-200';
  const textPrimary = isDark ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDark ? 'text-slate-400' : 'text-slate-600';

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target.result;
        setCsvData(text);
        parseCSV(text);
      };
      reader.readAsText(file);
    }
  };

  const parseCSV = (text) => {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length < 2) return;

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    const employees = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const emp = {};

      headers.forEach((header, index) => {
        const value = values[index] || '';
        if (header === 'email') emp.email = value;
        else if (header === 'first_name' || header === 'firstname') emp.first_name = value;
        else if (header === 'last_name' || header === 'lastname') emp.last_name = value;
        else if (header === 'department') emp.department = value;
        else if (header === 'job_title' || header === 'jobtitle' || header === 'title') emp.job_title = value;
        else if (header === 'phone') emp.phone = value;
        else if (header === 'manager_email' || header === 'manager') emp.manager_email = value;
        else if (header === 'employee_id' || header === 'employeeid' || header === 'id') emp.employee_id = value;
      });

      if (emp.email && emp.first_name && emp.last_name) {
        employees.push(emp);
      }
    }

    setParsedEmployees(employees);
  };

  const handleImport = async () => {
    if (parsedEmployees.length === 0) return;

    setImporting(true);
    try {
      const response = await createEmployeesBulk(parsedEmployees);
      setResult(response.data);
    } catch (error) {
      console.error('Import error:', error);
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className={`${bgCard} border ${borderColor} rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto`}>
        <div className={`px-6 py-4 border-b ${borderColor} flex items-center justify-between`}>
          <h2 className={`text-lg font-semibold ${textPrimary}`}>Import Employees from CSV</h2>
          <button onClick={onClose} className={`text-2xl ${textSecondary} hover:opacity-70`}>×</button>
        </div>

        <div className="p-6 space-y-6">
          {!result ? (
            <>
              <div>
                <p className={`text-sm ${textSecondary} mb-4`}>
                  Upload a CSV file with the following columns: <br />
                  <code className={`text-xs ${isDark ? 'bg-slate-700' : 'bg-slate-100'} px-2 py-1 rounded`}>
                    email, first_name, last_name, department, job_title, phone, manager_email, employee_id
                  </code>
                </p>

                <div className={`border-2 border-dashed ${borderColor} rounded-lg p-8 text-center ${isDark ? 'hover:border-blue-500' : 'hover:border-blue-400'} transition cursor-pointer`}>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="csv-upload"
                  />
                  <label htmlFor="csv-upload" className="cursor-pointer">
                    <svg className={`w-12 h-12 mx-auto mb-3 ${textSecondary}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className={`font-medium ${textPrimary}`}>Click to upload CSV file</p>
                    <p className={`text-sm ${textSecondary} mt-1`}>or drag and drop</p>
                  </label>
                </div>
              </div>

              {parsedEmployees.length > 0 && (
                <div>
                  <h3 className={`font-medium ${textPrimary} mb-3`}>
                    Preview ({parsedEmployees.length} employees found)
                  </h3>
                  <div className={`max-h-48 overflow-y-auto border ${borderColor} rounded-lg`}>
                    <table className="w-full text-sm">
                      <thead className={isDark ? 'bg-slate-700' : 'bg-slate-50'}>
                        <tr>
                          <th className={`px-3 py-2 text-left ${textSecondary}`}>Name</th>
                          <th className={`px-3 py-2 text-left ${textSecondary}`}>Email</th>
                          <th className={`px-3 py-2 text-left ${textSecondary}`}>Department</th>
                        </tr>
                      </thead>
                      <tbody className={`divide-y ${borderColor}`}>
                        {parsedEmployees.slice(0, 10).map((emp, index) => (
                          <tr key={index}>
                            <td className={`px-3 py-2 ${textPrimary}`}>{emp.first_name} {emp.last_name}</td>
                            <td className={`px-3 py-2 ${textSecondary}`}>{emp.email}</td>
                            <td className={`px-3 py-2 ${textSecondary}`}>{emp.department || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {parsedEmployees.length > 10 && (
                      <p className={`text-center py-2 text-sm ${textSecondary}`}>
                        ...and {parsedEmployees.length - 10} more
                      </p>
                    )}
                  </div>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={handleImport}
                  disabled={importing || parsedEmployees.length === 0}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 rounded-lg font-medium text-sm transition"
                >
                  {importing ? 'Importing...' : `Import ${parsedEmployees.length} Employees`}
                </button>
                <button
                  onClick={onClose}
                  className={`px-6 py-2 rounded-lg font-medium text-sm transition border ${borderColor} ${textPrimary}`}
                >
                  Cancel
                </button>
              </div>
            </>
          ) : (
            <div className="text-center py-8">
              <svg className="w-16 h-16 mx-auto mb-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className={`text-xl font-semibold mb-2 ${textPrimary}`}>Import Complete!</h3>
              <div className={`text-sm ${textSecondary} space-y-1`}>
                <p className="text-green-500 font-medium">{result.created} employees created</p>
                {result.skipped > 0 && <p className="text-yellow-500">{result.skipped} skipped (already exist)</p>}
                {result.errors > 0 && <p className="text-red-500">{result.errors} errors</p>}
              </div>
              <button
                onClick={onSuccess}
                className="mt-6 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium text-sm transition"
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default EmployeeManager;
