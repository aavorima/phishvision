import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import {
  getProgramScenarios,
  createScenario,
  updateScenario,
  deleteScenario,
  createScenarioAssignments,
  getCustomTemplates,
  getEmployees,
  getEmployeeDepartments
} from '../api/api';

const CHANNELS = [
  { id: 'email', name: 'Email', icon: '📧', description: 'Traditional email phishing' },
  { id: 'sms', name: 'SMS', icon: '💬', description: 'SMS phishing (smishing)' },
  { id: 'qr', name: 'QR Code', icon: '📱', description: 'QR code phishing (quishing)' }
];

const TECHNIQUES = [
  { id: 'urgency', name: 'Urgency', description: 'Act now! Limited time!' },
  { id: 'authority', name: 'Authority', description: 'CEO/Manager request' },
  { id: 'fear', name: 'Fear', description: 'Account suspended/locked' },
  { id: 'curiosity', name: 'Curiosity', description: 'You won\'t believe...' },
  { id: 'reward', name: 'Reward', description: 'You\'ve won a prize!' },
  { id: 'social_proof', name: 'Social Proof', description: 'Everyone is doing it' }
];

const SCHEDULE_TYPES = [
  { id: 'immediate', name: 'Immediate', description: 'Send as soon as program starts' },
  { id: 'specific_datetime', name: 'Specific Date/Time', description: 'Schedule for exact datetime' },
  { id: 'relative', name: 'Relative', description: 'Days after program start' }
];

const ASSIGNMENT_TYPES = [
  { id: 'employee', name: 'Specific Employees', icon: '👤', description: 'Select individual employees' },
  { id: 'department', name: 'Department', icon: '🏢', description: 'All employees in department' },
  { id: 'rule', name: 'Rule-Based', icon: '⚙️', description: 'Custom criteria (e.g., risk level)' }
];

const ScenarioAssignmentStep = ({ programId, onComplete, onBack }) => {
  const { isDarkMode } = useTheme();
  const [scenarios, setScenarios] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // UI State
  const [currentStep, setCurrentStep] = useState('list'); // list, create, assign
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [editingScenario, setEditingScenario] = useState(null);

  // Scenario Form State
  const [scenarioForm, setScenarioForm] = useState({
    name: '',
    channel: 'email',
    technique: 'urgency',
    template_id: '',
    schedule_type: 'immediate',
    scheduled_datetime: '',
    days_offset: 0
  });

  // Assignment Form State
  const [assignmentForm, setAssignmentForm] = useState({
    type: 'employee',
    employee_ids: [],
    department: '',
    rule_risk_level: '',
    rule_previous_clicks: ''
  });

  useEffect(() => {
    loadData();
  }, [programId]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [scenariosRes, templatesRes, employeesRes, deptsRes] = await Promise.all([
        getProgramScenarios(programId),
        getCustomTemplates(),
        getEmployees(),
        getEmployeeDepartments()
      ]);

      setScenarios(scenariosRes.data.scenarios || []);
      setTemplates(templatesRes.data.templates || []);
      setEmployees(employeesRes.data.employees || []);
      setDepartments(deptsRes.data.departments || []);
    } catch (err) {
      console.error('Error loading scenario data:', err);
      setError('Failed to load scenario data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScenario = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const data = { ...scenarioForm };

      // Clean up schedule data based on type
      if (data.schedule_type === 'immediate') {
        delete data.scheduled_datetime;
        delete data.days_offset;
      } else if (data.schedule_type === 'specific_datetime') {
        delete data.days_offset;
      } else if (data.schedule_type === 'relative') {
        delete data.scheduled_datetime;
      }

      await createScenario(programId, data);
      await loadData();
      resetScenarioForm();
      setCurrentStep('list');
    } catch (err) {
      console.error('Error creating scenario:', err);
      setError(err.response?.data?.error || 'Failed to create scenario');
    }
  };

  const handleUpdateScenario = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const data = { ...scenarioForm };

      if (data.schedule_type === 'immediate') {
        delete data.scheduled_datetime;
        delete data.days_offset;
      } else if (data.schedule_type === 'specific_datetime') {
        delete data.days_offset;
      } else if (data.schedule_type === 'relative') {
        delete data.scheduled_datetime;
      }

      await updateScenario(programId, editingScenario.id, data);
      await loadData();
      setEditingScenario(null);
      resetScenarioForm();
      setCurrentStep('list');
    } catch (err) {
      console.error('Error updating scenario:', err);
      setError(err.response?.data?.error || 'Failed to update scenario');
    }
  };

  const handleDeleteScenario = async (scenarioId) => {
    if (!window.confirm('Are you sure you want to delete this scenario and all its assignments?')) {
      return;
    }
    setError(null);
    try {
      await deleteScenario(programId, scenarioId);
      await loadData();
    } catch (err) {
      console.error('Error deleting scenario:', err);
      setError(err.response?.data?.error || 'Failed to delete scenario');
    }
  };

  const handleAssignScenario = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const data = {};

      if (assignmentForm.type === 'employee') {
        data.employee_ids = assignmentForm.employee_ids;
      } else if (assignmentForm.type === 'department') {
        data.department = assignmentForm.department;
      } else if (assignmentForm.type === 'rule') {
        const rule = {};
        if (assignmentForm.rule_risk_level) rule.risk_level = assignmentForm.rule_risk_level;
        if (assignmentForm.rule_previous_clicks) rule.previous_clicks_min = parseInt(assignmentForm.rule_previous_clicks);
        data.assignment_rule = rule;
      }

      await createScenarioAssignments(programId, selectedScenario.id, data);
      await loadData();
      resetAssignmentForm();
      setSelectedScenario(null);
      setCurrentStep('list');
    } catch (err) {
      console.error('Error creating assignments:', err);
      setError(err.response?.data?.error || 'Failed to create assignments');
    }
  };

  const resetScenarioForm = () => {
    setScenarioForm({
      name: '',
      channel: 'email',
      technique: 'urgency',
      template_id: '',
      schedule_type: 'immediate',
      scheduled_datetime: '',
      days_offset: 0
    });
  };

  const resetAssignmentForm = () => {
    setAssignmentForm({
      type: 'employee',
      employee_ids: [],
      department: '',
      rule_risk_level: '',
      rule_previous_clicks: ''
    });
  };

  const startEditScenario = (scenario) => {
    setEditingScenario(scenario);
    setScenarioForm({
      name: scenario.name,
      channel: scenario.channel,
      technique: scenario.technique,
      template_id: scenario.template_id,
      schedule_type: scenario.schedule_type || 'immediate',
      scheduled_datetime: scenario.scheduled_datetime || '',
      days_offset: scenario.days_offset || 0
    });
    setCurrentStep('create');
  };

  const getChannelIcon = (channelId) => {
    const channel = CHANNELS.find(c => c.id === channelId);
    return channel ? channel.icon : '📧';
  };

  const getTechniqueInfo = (techniqueId) => {
    const tech = TECHNIQUES.find(t => t.id === techniqueId);
    return tech || { name: techniqueId, description: '' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Scenario Assignment</h2>
          <p className="text-gray-500 dark:text-gray-400">
            Create scenarios and assign them to employees
          </p>
        </div>
        {currentStep === 'list' && (
          <button
            onClick={() => setCurrentStep('create')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + New Scenario
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg">
          {error}
          <button onClick={() => setError(null)} className="ml-4 underline">Dismiss</button>
        </div>
      )}

      {/* Scenario List View */}
      {currentStep === 'list' && (
        <div className="space-y-4">
          {scenarios.length === 0 ? (
            <div className={`p-8 text-center rounded-lg border-2 border-dashed ${isDarkMode ? 'border-gray-700' : 'border-gray-300'}`}>
              <p className="text-gray-500 mb-4">No scenarios created yet</p>
              <p className="text-sm text-gray-400 mb-4">
                Create at least 2 scenarios to assign different phishing types to different employees
              </p>
              <button
                onClick={() => setCurrentStep('create')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create First Scenario
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {scenarios.map((scenario) => (
                <div
                  key={scenario.id}
                  className={`p-4 rounded-lg border ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{getChannelIcon(scenario.channel)}</span>
                      <div>
                        <h3 className="font-semibold">{scenario.name}</h3>
                        <p className="text-sm text-gray-500 capitalize">{scenario.channel}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => startEditScenario(scenario)}
                        className="p-1 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900 rounded"
                        title="Edit"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => handleDeleteScenario(scenario.id)}
                        className="p-1 text-red-600 hover:bg-red-100 dark:hover:bg-red-900 rounded"
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-500">Technique:</span>
                      <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded text-xs capitalize">
                        {getTechniqueInfo(scenario.technique).name}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-500">Schedule:</span>
                      <span className="text-xs capitalize">{scenario.schedule_type || 'immediate'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-gray-500">Assignments:</span>
                      <span className="text-xs">{scenario.total_assignments || 0} employees</span>
                    </div>
                  </div>

                  <button
                    onClick={() => { setSelectedScenario(scenario); setCurrentStep('assign'); }}
                    className="w-full px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                  >
                    Assign to Employees
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Navigation */}
          <div className="flex gap-3 pt-4 border-t dark:border-gray-700">
            <button
              onClick={onBack}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Back
            </button>
            <button
              onClick={onComplete}
              disabled={scenarios.length < 2}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              title={scenarios.length < 2 ? 'Create at least 2 scenarios' : ''}
            >
              Continue to Review
            </button>
          </div>
        </div>
      )}

      {/* Create/Edit Scenario Form */}
      {currentStep === 'create' && (
        <form onSubmit={editingScenario ? handleUpdateScenario : handleCreateScenario} className="space-y-4">
          <div className={`p-6 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'} border ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
            <h3 className="text-lg font-semibold mb-4">
              {editingScenario ? 'Edit Scenario' : 'Create New Scenario'}
            </h3>

            {/* Scenario Name */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Scenario Name *</label>
              <input
                type="text"
                required
                value={scenarioForm.name}
                onChange={(e) => setScenarioForm({ ...scenarioForm, name: e.target.value })}
                className={`w-full px-3 py-2 rounded-lg border ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}
                placeholder="e.g., Finance Urgency SMS, IT Authority Email"
              />
            </div>

            {/* Channel Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Attack Channel *</label>
              <div className="grid grid-cols-3 gap-3">
                {CHANNELS.map((channel) => (
                  <button
                    key={channel.id}
                    type="button"
                    onClick={() => setScenarioForm({ ...scenarioForm, channel: channel.id })}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      scenarioForm.channel === channel.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  >
                    <div className="text-2xl mb-1">{channel.icon}</div>
                    <div className="font-medium text-sm">{channel.name}</div>
                    <div className="text-xs text-gray-500">{channel.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Technique Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Technique *</label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {TECHNIQUES.map((tech) => (
                  <button
                    key={tech.id}
                    type="button"
                    onClick={() => setScenarioForm({ ...scenarioForm, technique: tech.id })}
                    className={`p-2 rounded-lg border text-left transition-all ${
                      scenarioForm.technique === tech.id
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  >
                    <div className="font-medium text-sm">{tech.name}</div>
                    <div className="text-xs text-gray-500">{tech.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Template Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Template *</label>
              <select
                required
                value={scenarioForm.template_id}
                onChange={(e) => setScenarioForm({ ...scenarioForm, template_id: e.target.value })}
                className={`w-full px-3 py-2 rounded-lg border ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}
              >
                <option value="">Select a template...</option>
                {templates
                  .filter(t => t.template_type === scenarioForm.channel || t.template_type === 'email')
                  .map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name} ({template.template_type})
                    </option>
                  ))}
              </select>
            </div>

            {/* Schedule Type */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Schedule Type *</label>
              <div className="space-y-2">
                {SCHEDULE_TYPES.map((schedType) => (
                  <label
                    key={schedType.id}
                    className={`flex items-start p-3 rounded-lg border cursor-pointer ${
                      scenarioForm.schedule_type === schedType.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  >
                    <input
                      type="radio"
                      name="schedule_type"
                      value={schedType.id}
                      checked={scenarioForm.schedule_type === schedType.id}
                      onChange={(e) => setScenarioForm({ ...scenarioForm, schedule_type: e.target.value })}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <div className="font-medium">{schedType.name}</div>
                      <div className="text-xs text-gray-500">{schedType.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Schedule Details */}
            {scenarioForm.schedule_type === 'specific_datetime' && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Scheduled Date/Time *</label>
                <input
                  type="datetime-local"
                  required
                  value={scenarioForm.scheduled_datetime}
                  onChange={(e) => setScenarioForm({ ...scenarioForm, scheduled_datetime: e.target.value })}
                  className={`w-full px-3 py-2 rounded-lg border ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}
                />
              </div>
            )}

            {scenarioForm.schedule_type === 'relative' && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Days After Program Start *</label>
                <input
                  type="number"
                  min={0}
                  max={90}
                  required
                  value={scenarioForm.days_offset}
                  onChange={(e) => setScenarioForm({ ...scenarioForm, days_offset: parseInt(e.target.value) })}
                  className={`w-full px-3 py-2 rounded-lg border ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}
                />
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => {
                setCurrentStep('list');
                setEditingScenario(null);
                resetScenarioForm();
              }}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {editingScenario ? 'Update Scenario' : 'Create Scenario'}
            </button>
          </div>
        </form>
      )}

      {/* Assignment Form */}
      {currentStep === 'assign' && selectedScenario && (
        <form onSubmit={handleAssignScenario} className="space-y-4">
          <div className={`p-6 rounded-lg ${isDarkMode ? 'bg-gray-800' : 'bg-white'} border ${isDarkMode ? 'border-gray-700' : 'border-gray-200'}`}>
            <h3 className="text-lg font-semibold mb-2">Assign: {selectedScenario.name}</h3>
            <p className="text-sm text-gray-500 mb-4">
              {getChannelIcon(selectedScenario.channel)} {selectedScenario.channel} | {getTechniqueInfo(selectedScenario.technique).name}
            </p>

            {/* Assignment Type Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Assignment Type *</label>
              <div className="grid grid-cols-3 gap-3">
                {ASSIGNMENT_TYPES.map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setAssignmentForm({ ...assignmentForm, type: type.id })}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      assignmentForm.type === type.id
                        ? 'border-green-500 bg-green-50 dark:bg-green-900'
                        : 'border-gray-300 dark:border-gray-600'
                    }`}
                  >
                    <div className="text-2xl mb-1">{type.icon}</div>
                    <div className="font-medium text-sm">{type.name}</div>
                    <div className="text-xs text-gray-500">{type.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Specific Employees */}
            {assignmentForm.type === 'employee' && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Select Employees *</label>
                <div className={`max-h-64 overflow-y-auto border rounded-lg ${isDarkMode ? 'border-gray-600' : 'border-gray-300'}`}>
                  {employees.map((emp) => (
                    <label
                      key={emp.id}
                      className={`flex items-center p-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 ${
                        assignmentForm.employee_ids.includes(emp.id) ? 'bg-blue-50 dark:bg-blue-900' : ''
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={assignmentForm.employee_ids.includes(emp.id)}
                        onChange={(e) => {
                          const newIds = e.target.checked
                            ? [...assignmentForm.employee_ids, emp.id]
                            : assignmentForm.employee_ids.filter(id => id !== emp.id);
                          setAssignmentForm({ ...assignmentForm, employee_ids: newIds });
                        }}
                        className="mr-3"
                      />
                      <div>
                        <div className="font-medium text-sm">{emp.name}</div>
                        <div className="text-xs text-gray-500">{emp.email} | {emp.department}</div>
                      </div>
                    </label>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {assignmentForm.employee_ids.length} employee(s) selected
                </p>
              </div>
            )}

            {/* Department Selection */}
            {assignmentForm.type === 'department' && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Select Department *</label>
                <select
                  required
                  value={assignmentForm.department}
                  onChange={(e) => setAssignmentForm({ ...assignmentForm, department: e.target.value })}
                  className={`w-full px-3 py-2 rounded-lg border ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}
                >
                  <option value="">Choose department...</option>
                  {departments.map((dept) => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Rule-Based Assignment */}
            {assignmentForm.type === 'rule' && (
              <div className="space-y-3 mb-4">
                <p className="text-sm text-gray-500">Assign based on employee attributes:</p>

                <div>
                  <label className="block text-sm font-medium mb-1">Risk Level</label>
                  <select
                    value={assignmentForm.rule_risk_level}
                    onChange={(e) => setAssignmentForm({ ...assignmentForm, rule_risk_level: e.target.value })}
                    className={`w-full px-3 py-2 rounded-lg border ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}
                  >
                    <option value="">Any</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Minimum Previous Clicks</label>
                  <input
                    type="number"
                    min={0}
                    value={assignmentForm.rule_previous_clicks}
                    onChange={(e) => setAssignmentForm({ ...assignmentForm, rule_previous_clicks: e.target.value })}
                    className={`w-full px-3 py-2 rounded-lg border ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-300'}`}
                    placeholder="0"
                  />
                </div>

                <p className="text-xs text-gray-500">
                  Leave fields empty to match all employees
                </p>
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => {
                setCurrentStep('list');
                setSelectedScenario(null);
                resetAssignmentForm();
              }}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={
                (assignmentForm.type === 'employee' && assignmentForm.employee_ids.length === 0) ||
                (assignmentForm.type === 'department' && !assignmentForm.department)
              }
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              Create Assignments
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default ScenarioAssignmentStep;
