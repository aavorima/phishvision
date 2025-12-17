import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Configure axios to send cookies with requests
axios.defaults.withCredentials = true;

// Campaigns
export const getCampaigns = () => axios.get(`${API_BASE_URL}/campaigns/`);
export const getCampaign = (id) => axios.get(`${API_BASE_URL}/campaigns/${id}`);
export const createCampaign = (data) => axios.post(`${API_BASE_URL}/campaigns/`, data);
export const updateCampaignStatus = (id, status) =>
  axios.put(`${API_BASE_URL}/campaigns/${id}/status`, { status });
export const deleteCampaign = (id) => axios.delete(`${API_BASE_URL}/campaigns/${id}`);
export const getCampaignReport = (id) => axios.get(`${API_BASE_URL}/campaigns/${id}/report`);
export const getCampaignReportSummary = (id) => axios.get(`${API_BASE_URL}/campaigns/${id}/report/summary`);
export const exportCampaignReport = (id, format = 'json') => axios.get(`${API_BASE_URL}/campaigns/${id}/report/export?format=${format}`);

// Email Analyzer
export const analyzeEmail = (data) => axios.post(`${API_BASE_URL}/analyzer/analyze`, data);
export const getAnalysisHistory = (limit = 50) =>
  axios.get(`${API_BASE_URL}/analyzer/history?limit=${limit}`);
export const getAnalysis = (id) => axios.get(`${API_BASE_URL}/analyzer/${id}`);
export const getAnalyzerStats = () => axios.get(`${API_BASE_URL}/analyzer/stats`);
export const clearAnalysisHistory = () => axios.delete(`${API_BASE_URL}/analyzer/history`);

// Dashboard
export const getDashboardStats = () => axios.get(`${API_BASE_URL}/dashboard/stats`);
export const getRecentActivity = () => axios.get(`${API_BASE_URL}/dashboard/recent-activity`);
export const getCampaignPerformance = () => axios.get(`${API_BASE_URL}/dashboard/campaign-performance`);
export const getThreatDistribution = () => axios.get(`${API_BASE_URL}/dashboard/threat-distribution`);

// Templates
export const getTemplates = (category) => {
  const url = category ? `${API_BASE_URL}/templates?category=${category}` : `${API_BASE_URL}/templates`;
  return axios.get(url);
};
export const getTemplate = (id) => axios.get(`${API_BASE_URL}/templates/${id}`);
export const createTemplate = (data) => axios.post(`${API_BASE_URL}/templates`, data);
export const updateTemplate = (id, data) => axios.put(`${API_BASE_URL}/templates/${id}`, data);
export const deleteTemplate = (id) => axios.delete(`${API_BASE_URL}/templates/${id}`);
export const previewTemplate = (id, data) => axios.post(`${API_BASE_URL}/templates/${id}/preview`, data);
export const duplicateTemplate = (id, data) => axios.post(`${API_BASE_URL}/templates/${id}/duplicate`, data);
export const generateAITemplate = (data) => axios.post(`${API_BASE_URL}/templates/generate-ai`, data);
export const improveTemplateAI = (id, data) => axios.post(`${API_BASE_URL}/templates/${id}/improve-ai`, data);

// SOC (Security Operations Center)
export const getSOCIncidents = (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.status) params.append('status', filters.status);
  if (filters.severity) params.append('severity', filters.severity);
  if (filters.days) params.append('days', filters.days);
  return axios.get(`${API_BASE_URL}/soc/incidents?${params}`);
};
export const getSOCIncident = (id) => axios.get(`${API_BASE_URL}/soc/incidents/${id}`);
export const createSOCIncident = (data) => axios.post(`${API_BASE_URL}/soc/incidents`, data);
export const updateSOCIncidentStatus = (id, data) => axios.put(`${API_BASE_URL}/soc/incidents/${id}/status`, data);
export const deleteSOCIncident = (id) => axios.delete(`${API_BASE_URL}/soc/incidents/${id}`);
export const getSOCTimeline = (days = 30) => axios.get(`${API_BASE_URL}/soc/timeline?days=${days}`);
export const getSOCMetrics = (days = 30) => axios.get(`${API_BASE_URL}/soc/metrics?days=${days}`);

// User Risk Scoring
export const getRiskUsers = (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.department) params.append('department', filters.department);
  if (filters.risk_level) params.append('risk_level', filters.risk_level);
  if (filters.sort_by) params.append('sort_by', filters.sort_by);
  return axios.get(`${API_BASE_URL}/risk/users?${params}`);
};
export const getRiskUser = (id) => axios.get(`${API_BASE_URL}/risk/users/${id}`);
export const getRiskUserByEmail = (email) => axios.get(`${API_BASE_URL}/risk/users/email/${email}`);
export const createOrUpdateRiskUser = (data) => axios.post(`${API_BASE_URL}/risk/users`, data);
export const updateRiskUser = (id, data) => axios.put(`${API_BASE_URL}/risk/users/${id}`, data);
export const deleteRiskUser = (id) => axios.delete(`${API_BASE_URL}/risk/users/${id}`);
export const recalculateRiskScores = () => axios.post(`${API_BASE_URL}/risk/recalculate-all`);
export const getRiskStats = () => axios.get(`${API_BASE_URL}/risk/stats`);
export const getRiskDepartments = () => axios.get(`${API_BASE_URL}/risk/departments`);
export const getRiskHeatmap = () => axios.get(`${API_BASE_URL}/risk/heatmap`);

// Landing Pages (Credential Harvesting)
export const getLandingPages = () => axios.get(`${API_BASE_URL}/landing/pages`);
export const getLandingPage = (id) => axios.get(`${API_BASE_URL}/landing/pages/${id}`);
export const createLandingPage = (data) => axios.post(`${API_BASE_URL}/landing/pages`, data);
export const updateLandingPage = (id, data) => axios.put(`${API_BASE_URL}/landing/pages/${id}`, data);
export const deleteLandingPage = (id) => axios.delete(`${API_BASE_URL}/landing/pages/${id}`);
export const cloneWebsite = (data) => axios.post(`${API_BASE_URL}/landing/clone`, data);
export const getLandingCaptures = (pageId) => axios.get(`${API_BASE_URL}/landing/pages/${pageId}/captures`);
export const getRepeatOffenders = () => axios.get(`${API_BASE_URL}/landing/repeat-offenders`);
export const getUsersRequiringTraining = () => axios.get(`${API_BASE_URL}/landing/requires-training`);

// QR Code Phishing (Quishing)
export const getQRCampaigns = () => axios.get(`${API_BASE_URL}/qr/campaigns`);
export const getQRCampaign = (id) => axios.get(`${API_BASE_URL}/qr/campaigns/${id}`);
export const createQRCampaign = (data) => axios.post(`${API_BASE_URL}/qr/campaigns`, data);
export const updateQRCampaign = (id, data) => axios.put(`${API_BASE_URL}/qr/campaigns/${id}`, data);
export const deleteQRCampaign = (id) => axios.delete(`${API_BASE_URL}/qr/campaigns/${id}`);
export const getQRStats = () => axios.get(`${API_BASE_URL}/qr/stats`);
export const generateQuickQR = (data) => axios.post(`${API_BASE_URL}/qr/generate`, data, { responseType: 'blob' });
export const sendQRPoster = (campaignId, data) => axios.post(`${API_BASE_URL}/qr/campaigns/${campaignId}/send-poster`, data);

// SMS Phishing (Smishing)
export const getSMSCampaigns = () => axios.get(`${API_BASE_URL}/sms/campaigns`);
export const getSMSCampaign = (id) => axios.get(`${API_BASE_URL}/sms/campaigns/${id}`);
export const createSMSCampaign = (data) => axios.post(`${API_BASE_URL}/sms/campaigns`, data);
export const updateSMSCampaign = (id, data) => axios.put(`${API_BASE_URL}/sms/campaigns/${id}`, data);
export const deleteSMSCampaign = (id) => axios.delete(`${API_BASE_URL}/sms/campaigns/${id}`);
export const addSMSTargets = (id, data) => axios.post(`${API_BASE_URL}/sms/campaigns/${id}/targets`, data);
export const sendSMSCampaign = (id, userId) => axios.post(`${API_BASE_URL}/sms/campaigns/${id}/send`, { user_id: userId });
export const getSMSTemplates = () => axios.get(`${API_BASE_URL}/sms/templates`);
export const getSMSStats = () => axios.get(`${API_BASE_URL}/sms/stats`);

// Employees
export const getEmployees = (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.department) params.append('department', filters.department);
  if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
  if (filters.search) params.append('search', filters.search);
  return axios.get(`${API_BASE_URL}/employees/?${params}`);
};
export const getEmployee = (id) => axios.get(`${API_BASE_URL}/employees/${id}`);
export const createEmployee = (data) => axios.post(`${API_BASE_URL}/employees/`, data);
export const createEmployeesBulk = (employees) => axios.post(`${API_BASE_URL}/employees/bulk`, { employees });
export const updateEmployee = (id, data) => axios.put(`${API_BASE_URL}/employees/${id}`, data);
export const deleteEmployee = (id) => axios.delete(`${API_BASE_URL}/employees/${id}`);
export const getEmployeeDepartments = () => axios.get(`${API_BASE_URL}/employees/departments`);
export const getEmployeeStats = () => axios.get(`${API_BASE_URL}/employees/stats`);

// HVS (Human Vulnerability Score)
export const getHVSEmployees = (params = {}) => {
  const query = new URLSearchParams();
  if (params.department) query.append('department', params.department);
  if (params.min_score !== undefined) query.append('min_score', params.min_score);
  if (params.max_score !== undefined) query.append('max_score', params.max_score);
  if (params.level) query.append('level', params.level);
  return axios.get(`${API_BASE_URL}/hvs/employees?${query}`);
};
export const getHVSEmployeeDetail = (employeeId) => axios.get(`${API_BASE_URL}/hvs/employees/${employeeId}`);
export const getHVSEmployeeEvents = (employeeId, params = {}) => {
  const query = new URLSearchParams();
  if (params.limit) query.append('limit', params.limit);
  if (params.offset) query.append('offset', params.offset);
  return axios.get(`${API_BASE_URL}/hvs/employees/${employeeId}/events?${query}`);
};
export const manualHVSUpdate = (employeeId, data) => axios.post(`${API_BASE_URL}/hvs/employees/${employeeId}/manual-update`, data);
export const getHVSDepartments = () => axios.get(`${API_BASE_URL}/hvs/departments`);
export const getHVSDepartmentDetail = (departmentName) => axios.get(`${API_BASE_URL}/hvs/departments/${encodeURIComponent(departmentName)}`);
export const getHVSStats = () => axios.get(`${API_BASE_URL}/hvs/stats`);
export const getHVSRecentEvents = (params = {}) => {
  const query = new URLSearchParams();
  if (params.limit) query.append('limit', params.limit);
  if (params.offset) query.append('offset', params.offset);
  if (params.event_type) query.append('event_type', params.event_type);
  return axios.get(`${API_BASE_URL}/hvs/events/recent?${query}`);
};

// Authentication
export const login = (data) => axios.post(`${API_BASE_URL}/auth/login`, data);
export const register = (data) => axios.post(`${API_BASE_URL}/auth/register`, data);
export const logout = () => axios.post(`${API_BASE_URL}/auth/logout`);
export const getCurrentUser = () => axios.get(`${API_BASE_URL}/auth/me`);
export const updateProfile = (data) => axios.put(`${API_BASE_URL}/auth/me`, data);
export const changePassword = (data) => axios.post(`${API_BASE_URL}/auth/change-password`, data);

// Settings
export const getSettings = () => axios.get(`${API_BASE_URL}/settings/`);
export const updateSettings = (data) => axios.put(`${API_BASE_URL}/settings/`, data);
export const testSmtpConnection = () => axios.post(`${API_BASE_URL}/settings/smtp/test`);
export const sendTestEmail = (data) => axios.post(`${API_BASE_URL}/settings/smtp/send-test`, data);
export const getSmtpStatus = () => axios.get(`${API_BASE_URL}/campaigns/smtp-status`);
export const testGeminiConnection = (data) => axios.post(`${API_BASE_URL}/settings/gemini/test`, data);

// Threat Intelligence Feed
export const getThreatFeed = (params = {}) => {
  const query = new URLSearchParams();
  if (params.page) query.append('page', params.page);
  if (params.per_page) query.append('per_page', params.per_page);
  if (params.classification) query.append('classification', params.classification);
  if (params.threat_type) query.append('threat_type', params.threat_type);
  if (params.days) query.append('days', params.days);
  return axios.get(`${API_BASE_URL}/threats/feed?${query}`);
};
export const getThreatEntry = (shortId) => axios.get(`${API_BASE_URL}/threats/entry/${shortId}`);
export const getThreatStats = () => axios.get(`${API_BASE_URL}/threats/stats`);
export const searchThreats = (query) => axios.get(`${API_BASE_URL}/threats/search?q=${encodeURIComponent(query)}`);
export const submitToThreatFeed = (data) => axios.post(`${API_BASE_URL}/threats/submit`, data);
export const voteOnThreat = (shortId, vote) => axios.post(`${API_BASE_URL}/threats/entry/${shortId}/vote`, { vote });
export const getMyThreatSubmissions = () => axios.get(`${API_BASE_URL}/threats/my-submissions`);

// Vulnerability Profiling
export const getVulnerabilityProfiles = (params = {}) => {
  const query = new URLSearchParams();
  if (params.department) query.append('department', params.department);
  if (params.risk_level) query.append('risk_level', params.risk_level);
  if (params.min_score) query.append('min_score', params.min_score);
  if (params.max_score) query.append('max_score', params.max_score);
  if (params.page) query.append('page', params.page);
  if (params.per_page) query.append('per_page', params.per_page);
  return axios.get(`${API_BASE_URL}/vulnerability/profiles?${query}`);
};
export const getVulnerabilityProfile = (employeeId) => axios.get(`${API_BASE_URL}/vulnerability/profile/${employeeId}`);
export const getVulnerabilitySummary = (employeeId) => axios.get(`${API_BASE_URL}/vulnerability/profile/${employeeId}/summary`);
export const recalculateProfile = (employeeId) => axios.post(`${API_BASE_URL}/vulnerability/profile/${employeeId}/calculate`);
export const getVulnerabilityDepartments = () => axios.get(`${API_BASE_URL}/vulnerability/departments`);
export const getVulnerabilityDepartment = (department) => axios.get(`${API_BASE_URL}/vulnerability/department/${encodeURIComponent(department)}`);
export const getVulnerabilityAgeGroups = () => axios.get(`${API_BASE_URL}/vulnerability/age-groups`);
export const getVulnerabilityAgeGroup = (ageGroup) => axios.get(`${API_BASE_URL}/vulnerability/age-group/${encodeURIComponent(ageGroup)}`);
export const getVulnerabilityTechniques = () => axios.get(`${API_BASE_URL}/vulnerability/techniques`);
export const getHighRiskEmployees = (threshold = 70, limit = 20) =>
  axios.get(`${API_BASE_URL}/vulnerability/high-risk?threshold=${threshold}&limit=${limit}`);
export const getRepeatOffendersVuln = () => axios.get(`${API_BASE_URL}/vulnerability/repeat-offenders`);
export const getVulnerabilityTrends = (days = 90) => axios.get(`${API_BASE_URL}/vulnerability/trends?days=${days}`);
export const getVulnerabilityOrgSummary = () => axios.get(`${API_BASE_URL}/vulnerability/summary`);
export const recalculateAllProfiles = () => axios.post(`${API_BASE_URL}/vulnerability/recalculate-all`);
export const initializeProfiles = () => axios.post(`${API_BASE_URL}/vulnerability/initialize-profiles`);

// Campaign Programs (Vulnerability Profiling Programs)
export const getPrograms = (status) => {
  const url = status ? `${API_BASE_URL}/programs/?status=${status}` : `${API_BASE_URL}/programs/`;
  return axios.get(url);
};
export const getProgram = (id) => axios.get(`${API_BASE_URL}/programs/${id}`);
export const createProgram = (data) => axios.post(`${API_BASE_URL}/programs/`, data);
export const updateProgram = (id, data) => axios.put(`${API_BASE_URL}/programs/${id}`, data);
export const deleteProgram = (id) => axios.delete(`${API_BASE_URL}/programs/${id}`);
export const scheduleProgram = (id) => axios.post(`${API_BASE_URL}/programs/${id}/schedule`);
export const startProgram = (id) => axios.post(`${API_BASE_URL}/programs/${id}/start`);
export const pauseProgram = (id) => axios.post(`${API_BASE_URL}/programs/${id}/pause`);
export const resumeProgram = (id) => axios.post(`${API_BASE_URL}/programs/${id}/resume`);
export const completeProgram = (id) => axios.post(`${API_BASE_URL}/programs/${id}/complete`);
export const getProgramStats = (id) => axios.get(`${API_BASE_URL}/programs/${id}/stats`);
export const getProgramEmployees = (id, page = 1, perPage = 20) =>
  axios.get(`${API_BASE_URL}/programs/${id}/employees?page=${page}&per_page=${perPage}`);
export const getProgramTimeline = (id) => axios.get(`${API_BASE_URL}/programs/${id}/timeline`);
export const getProgramPhases = (id) => axios.get(`${API_BASE_URL}/programs/${id}/phases`);
export const updateProgramPhase = (programId, phaseId, data) =>
  axios.put(`${API_BASE_URL}/programs/${programId}/phases/${phaseId}`, data);
export const getProgramCampaigns = (id, params = {}) => {
  const query = new URLSearchParams();
  if (params.status) query.append('status', params.status);
  if (params.employee_id) query.append('employee_id', params.employee_id);
  if (params.page) query.append('page', params.page);
  if (params.per_page) query.append('per_page', params.per_page);
  return axios.get(`${API_BASE_URL}/programs/${id}/campaigns?${query}`);
};
export const cancelScheduledCampaign = (campaignId) => axios.post(`${API_BASE_URL}/programs/campaigns/${campaignId}/cancel`);
export const processDueCampaigns = (batchSize = 50) => axios.post(`${API_BASE_URL}/programs/process-due?batch_size=${batchSize}`);
export const getEmployeeProgramHistory = (employeeId, programId) => {
  const url = programId
    ? `${API_BASE_URL}/programs/employee/${employeeId}/history?program_id=${programId}`
    : `${API_BASE_URL}/programs/employee/${employeeId}/history`;
  return axios.get(url);
};

// Program Scenarios
export const getProgramScenarios = (programId) => axios.get(`${API_BASE_URL}/programs/${programId}/scenarios`);
export const createScenario = (programId, data) => axios.post(`${API_BASE_URL}/programs/${programId}/scenarios`, data);
export const getScenario = (programId, scenarioId) => axios.get(`${API_BASE_URL}/programs/${programId}/scenarios/${scenarioId}`);
export const updateScenario = (programId, scenarioId, data) => axios.put(`${API_BASE_URL}/programs/${programId}/scenarios/${scenarioId}`, data);
export const deleteScenario = (programId, scenarioId) => axios.delete(`${API_BASE_URL}/programs/${programId}/scenarios/${scenarioId}`);
export const getScenarioStats = (programId, scenarioId) => axios.get(`${API_BASE_URL}/programs/${programId}/scenarios/${scenarioId}/stats`);

// Scenario Assignments
export const createScenarioAssignments = (programId, scenarioId, data) => axios.post(`${API_BASE_URL}/programs/${programId}/scenarios/${scenarioId}/assignments`, data);
export const deleteScenarioAssignment = (programId, scenarioId, assignmentId) => axios.delete(`${API_BASE_URL}/programs/${programId}/scenarios/${scenarioId}/assignments/${assignmentId}`);

// Program Awareness Reports
export const getProgramReport = (programId) => axios.get(`${API_BASE_URL}/programs/${programId}/report`);
export const exportProgramReport = (programId, format = 'pdf') => {
  return axios.get(`${API_BASE_URL}/programs/${programId}/report/export?format=${format}`, {
    responseType: format === 'pdf' ? 'blob' : 'json'
  });
};

// Default export object for convenience
const api = {
  // Campaigns
  getCampaigns,
  getCampaign,
  createCampaign,
  updateCampaignStatus,
  deleteCampaign,
  getCampaignReport,
  getCampaignReportSummary,
  exportCampaignReport,
  // Analyzer
  analyzeEmail,
  getAnalysisHistory,
  getAnalysis,
  getAnalyzerStats,
  // Dashboard
  getDashboardStats,
  getRecentActivity,
  getCampaignPerformance,
  getThreatDistribution,
  // Templates
  getTemplates,
  getTemplate,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  previewTemplate,
  duplicateTemplate,
  generateAITemplate,
  improveTemplateAI,
  // SOC
  getSOCIncidents,
  getSOCIncident,
  createSOCIncident,
  updateSOCIncidentStatus,
  deleteSOCIncident,
  getSOCTimeline,
  getSOCMetrics,
  // Risk
  getRiskUsers,
  getRiskUser,
  getRiskUserByEmail,
  createOrUpdateRiskUser,
  updateRiskUser,
  deleteRiskUser,
  recalculateRiskScores,
  getRiskStats,
  getRiskDepartments,
  getRiskHeatmap,
  // Landing Pages
  getLandingPages,
  getLandingPage,
  createLandingPage,
  updateLandingPage,
  deleteLandingPage,
  cloneWebsite,
  getLandingCaptures,
  getRepeatOffenders,
  getUsersRequiringTraining,
  // QR Phishing
  getQRCampaigns,
  getQRCampaign,
  createQRCampaign,
  updateQRCampaign,
  deleteQRCampaign,
  getQRStats,
  generateQuickQR,
  // SMS Phishing
  getSMSCampaigns,
  getSMSCampaign,
  createSMSCampaign,
  updateSMSCampaign,
  deleteSMSCampaign,
  addSMSTargets,
  sendSMSCampaign,
  getSMSTemplates,
  getSMSStats,
  // Employees
  getEmployees,
  getEmployee,
  createEmployee,
  createEmployeesBulk,
  updateEmployee,
  deleteEmployee,
  getEmployeeDepartments,
  getEmployeeStats,
  // HVS
  getHVSEmployees,
  getHVSEmployeeDetail,
  getHVSEmployeeEvents,
  manualHVSUpdate,
  getHVSDepartments,
  getHVSDepartmentDetail,
  getHVSStats,
  getHVSRecentEvents,
  // Authentication
  login,
  register,
  logout,
  getCurrentUser,
  updateProfile,
  changePassword,
  // Settings
  getSettings,
  updateSettings,
  testSmtpConnection,
  sendTestEmail,
  getSmtpStatus,
  // Threat Intelligence Feed
  getThreatFeed,
  getThreatEntry,
  getThreatStats,
  searchThreats,
  submitToThreatFeed,
  voteOnThreat,
  getMyThreatSubmissions,
  // Vulnerability Profiling
  getVulnerabilityProfiles,
  getVulnerabilityProfile,
  getVulnerabilitySummary,
  recalculateProfile,
  getVulnerabilityDepartments,
  getVulnerabilityDepartment,
  getVulnerabilityAgeGroups,
  getVulnerabilityAgeGroup,
  getVulnerabilityTechniques,
  getHighRiskEmployees,
  getRepeatOffendersVuln,
  getVulnerabilityTrends,
  getVulnerabilityOrgSummary,
  recalculateAllProfiles,
  initializeProfiles,
  // Campaign Programs
  getPrograms,
  getProgram,
  createProgram,
  updateProgram,
  deleteProgram,
  scheduleProgram,
  startProgram,
  pauseProgram,
  resumeProgram,
  completeProgram,
  getProgramStats,
  getProgramEmployees,
  getProgramTimeline,
  getProgramPhases,
  updateProgramPhase,
  getProgramCampaigns,
  cancelScheduledCampaign,
  processDueCampaigns,
  getEmployeeProgramHistory,
  // Program Scenarios
  getProgramScenarios,
  createScenario,
  getScenario,
  updateScenario,
  deleteScenario,
  getScenarioStats,
  createScenarioAssignments,
  deleteScenarioAssignment
};

export default api;
