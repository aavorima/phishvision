import React, { useState, useEffect } from 'react';
import { getCampaigns, createCampaign, deleteCampaign, getTemplates, getEmployees, getEmployeeDepartments, getLandingPages, getSmtpStatus } from '../api/api';
import { useNavigate, Link } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import ConfirmDialog from './ConfirmDialog';

function CampaignManager() {
  const [campaigns, setCampaigns] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [showErrorDialog, setShowErrorDialog] = useState(false);
  const [selectedCampaignId, setSelectedCampaignId] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [smtpConfigured, setSmtpConfigured] = useState(null);
  const [showSmtpWarning, setShowSmtpWarning] = useState(false);
  const [selectedCampaigns, setSelectedCampaigns] = useState([]);
  const [showBulkDeleteDialog, setShowBulkDeleteDialog] = useState(false);
  const navigate = useNavigate();
  const { isDark } = useTheme();

  useEffect(() => {
    loadCampaigns();
    checkSmtpStatus();
  }, []);

  const checkSmtpStatus = async () => {
    try {
      const response = await getSmtpStatus();
      setSmtpConfigured(response.data.configured);
    } catch (error) {
      console.error('Error checking SMTP status:', error);
      setSmtpConfigured(false);
    }
  };

  const handleNewCampaignClick = () => {
    if (!smtpConfigured) {
      setShowSmtpWarning(true);
    } else {
      setShowCreate(true);
    }
  };

  const loadCampaigns = async () => {
    try {
      setLoading(true);
      const response = await getCampaigns();
      setCampaigns(response.data);
    } catch (error) {
      console.error('Error loading campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (id) => {
    setSelectedCampaignId(id);
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteCampaign(selectedCampaignId);
      setShowDeleteDialog(false);
      setSelectedCampaignId(null);
      loadCampaigns();
      setShowSuccessDialog(true);
    } catch (error) {
      console.error('Error deleting campaign:', error);
      setShowDeleteDialog(false);
      setErrorMessage('Failed to delete campaign. Please try again.');
      setShowErrorDialog(true);
    }
  };

  const handleBulkDeleteClick = () => {
    if (selectedCampaigns.length === 0) {
      setErrorMessage('Please select at least one campaign to delete.');
      setShowErrorDialog(true);
      return;
    }
    setShowBulkDeleteDialog(true);
  };

  const handleBulkDeleteConfirm = async () => {
    try {
      await Promise.all(selectedCampaigns.map(id => deleteCampaign(id)));
      setShowBulkDeleteDialog(false);
      setSelectedCampaigns([]);
      loadCampaigns();
      setShowSuccessDialog(true);
    } catch (error) {
      console.error('Error deleting campaigns:', error);
      setShowBulkDeleteDialog(false);
      setErrorMessage('Failed to delete some campaigns. Please try again.');
      setShowErrorDialog(true);
    }
  };

  const toggleCampaignSelection = (campaignId) => {
    setSelectedCampaigns(prev => {
      if (prev.includes(campaignId)) {
        return prev.filter(id => id !== campaignId);
      } else {
        return [...prev, campaignId];
      }
    });
  };

  const toggleSelectAll = () => {
    if (selectedCampaigns.length === campaigns.length) {
      setSelectedCampaigns([]);
    } else {
      setSelectedCampaigns(campaigns.map(c => c.id));
    }
  };

  if (showCreate) {
    return (
      <div className={`min-h-screen p-6 ${isDark ? 'bg-surface-1' : 'bg-surface-light-1'}`}>
        <CreateCampaignForm
          onClose={() => setShowCreate(false)}
          onSuccess={() => {
            setShowCreate(false);
            loadCampaigns();
          }}
          isDark={isDark}
        />
      </div>
    );
  }

  return (
    <div className={`min-h-screen p-6 ${isDark ? 'bg-surface-1' : 'bg-surface-light-1'}`}>
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className={`absolute top-0 right-0 w-[600px] h-[600px] rounded-full blur-3xl ${isDark ? 'bg-primary/3' : 'bg-primary/5'}`} />
        <div className={`absolute bottom-0 left-0 w-[400px] h-[400px] rounded-full blur-3xl ${isDark ? 'bg-accent/3' : 'bg-accent/5'}`} />
      </div>

      <div className="relative z-10 max-w-[1600px] mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className={`text-3xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-1'}`}>
                Campaign Manager
              </h1>
              <p className={`mt-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                Manage phishing simulation campaigns
              </p>
            </div>
            <div className="flex gap-3">
              {campaigns.length > 0 && (
                <>
                  <button
                    onClick={toggleSelectAll}
                    className={`px-4 py-3 rounded-xl font-semibold transition-all duration-300 hover:scale-[1.02] ${
                      selectedCampaigns.length === campaigns.length
                        ? 'bg-primary text-surface-1'
                        : isDark
                          ? 'bg-surface-2 text-white border border-white/10'
                          : 'bg-white text-surface-1 border border-black/10'
                    }`}
                  >
                    {selectedCampaigns.length === campaigns.length ? 'Deselect All' : 'Select All'}
                  </button>
                  {selectedCampaigns.length > 0 && (
                    <button
                      onClick={handleBulkDeleteClick}
                      className="px-4 py-3 rounded-xl font-semibold bg-danger text-white transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                    >
                      Delete Selected ({selectedCampaigns.length})
                    </button>
                  )}
                </>
              )}
              <button
                onClick={handleNewCampaignClick}
                className="group relative px-6 py-3 rounded-xl font-semibold text-surface-1 overflow-hidden transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/25 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                <span className="relative flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  New Campaign
                </span>
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col justify-center items-center h-64">
            <div className="spinner" />
            <p className={`text-sm mt-4 font-medium ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>Loading campaigns...</p>
          </div>
        ) : campaigns.length === 0 ? (
          <div className={`rounded-2xl border p-16 text-center ${isDark ? 'bg-surface-2 border-white/5' : 'bg-white border-black/5 shadow-lg'}`}>
            <div className={`p-4 rounded-2xl inline-block mb-6 ${isDark ? 'bg-surface-3' : 'bg-surface-light-3'}`}>
              <svg className={`w-16 h-16 ${isDark ? 'text-white/20' : 'text-surface-1/20'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className={`text-xl font-semibold mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>No campaigns yet</h3>
            <p className={`text-sm mb-8 max-w-md mx-auto ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
              Create your first phishing simulation campaign to start testing your organization's security awareness
            </p>
            <button
              onClick={handleNewCampaignClick}
              className="group relative px-6 py-3 rounded-xl font-semibold text-surface-1 overflow-hidden transition-all duration-300 hover:scale-[1.02]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
              <span className="relative">Create Campaign</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {campaigns.map((campaign, index) => (
              <CampaignCard
                key={campaign.id}
                campaign={campaign}
                onView={() => navigate(`/campaigns/${campaign.id}`)}
                onViewReport={() => navigate(`/campaigns/${campaign.id}/report`)}
                onDelete={() => handleDeleteClick(campaign.id)}
                isSelected={selectedCampaigns.includes(campaign.id)}
                onToggleSelect={() => toggleCampaignSelection(campaign.id)}
                isDark={isDark}
                index={index}
              />
            ))}
          </div>
        )}
      </div>

      {/* Confirmation Dialogs */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        title="Delete Campaign"
        message="Are you sure you want to delete this campaign? This action cannot be undone and all campaign data will be permanently removed."
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setShowDeleteDialog(false);
          setSelectedCampaignId(null);
        }}
        confirmText="Delete Campaign"
        cancelText="Cancel"
        type="danger"
      />

      <ConfirmDialog
        isOpen={showSuccessDialog}
        title="Campaign Deleted"
        message="The campaign has been successfully deleted."
        onConfirm={() => setShowSuccessDialog(false)}
        onCancel={() => setShowSuccessDialog(false)}
        confirmText="OK"
        cancelText="Close"
        type="info"
      />

      <ConfirmDialog
        isOpen={showErrorDialog}
        title="Error"
        message={errorMessage}
        onConfirm={() => setShowErrorDialog(false)}
        onCancel={() => setShowErrorDialog(false)}
        confirmText="OK"
        cancelText="Close"
        type="danger"
      />

      <ConfirmDialog
        isOpen={showSmtpWarning}
        title="SMTP Not Configured"
        message="You need to configure SMTP settings before creating campaigns. Please go to Settings and set up your email server credentials first."
        onConfirm={() => {
          setShowSmtpWarning(false);
          navigate('/settings');
        }}
        onCancel={() => setShowSmtpWarning(false)}
        confirmText="Go to Settings"
        cancelText="Cancel"
        type="warning"
      />

      <ConfirmDialog
        isOpen={showBulkDeleteDialog}
        title="Delete Multiple Campaigns"
        message={`Are you sure you want to delete ${selectedCampaigns.length} campaign(s)? This action cannot be undone and all campaign data will be permanently removed.`}
        onConfirm={handleBulkDeleteConfirm}
        onCancel={() => setShowBulkDeleteDialog(false)}
        confirmText={`Delete ${selectedCampaigns.length} Campaign(s)`}
        cancelText="Cancel"
        type="danger"
      />
    </div>
  );
}

function CampaignCard({ campaign, onView, onViewReport, onDelete, isSelected, onToggleSelect, isDark, index }) {
  const getStatusConfig = (status) => {
    const configs = {
      active: { bg: 'bg-success/10', text: 'text-success', border: 'border-success/20', label: 'ACTIVE' },
      paused: { bg: 'bg-warning/10', text: 'text-warning', border: 'border-warning/20', label: 'PAUSED' },
      completed: { bg: 'bg-surface-4', text: isDark ? 'text-white/50' : 'text-surface-1/50', border: isDark ? 'border-white/10' : 'border-black/10', label: 'COMPLETED' }
    };
    return configs[status] || configs.completed;
  };

  const statusConfig = getStatusConfig(campaign.status);

  const openRate = campaign.total_targets > 0
    ? Math.round((campaign.opened_count / campaign.total_targets) * 100)
    : 0;
  const clickRate = campaign.total_targets > 0
    ? Math.round((campaign.clicked_count / campaign.total_targets) * 100)
    : 0;

  return (
    <div
      className={`group relative rounded-2xl border overflow-hidden transition-all duration-500 hover:scale-[1.02] ${
        isSelected
          ? isDark ? 'bg-primary/10 border-primary' : 'bg-primary/10 border-primary shadow-lg shadow-primary/20'
          : isDark ? 'bg-surface-2 border-white/5 hover:border-white/10' : 'bg-white border-black/5 hover:border-black/10 shadow-lg hover:shadow-xl'
      }`}
      style={{ animationDelay: `${index * 100}ms` }}
    >
      {/* Selection Checkbox */}
      <div className="absolute top-4 left-4 z-10">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleSelect();
          }}
          className={`w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all ${
            isSelected
              ? 'bg-primary border-primary'
              : isDark
                ? 'bg-surface-3 border-white/30 hover:border-primary'
                : 'bg-white border-black/30 hover:border-primary'
          }`}
        >
          {isSelected && (
            <svg className="w-4 h-4 text-surface-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>
      </div>

      {/* Header */}
      <div className={`p-5 border-b ${isDark ? 'border-white/5 bg-surface-3/50' : 'border-black/5 bg-surface-light-2'}`}>
        <div className="flex justify-between items-start">
          <h3 className={`text-base font-semibold truncate pr-4 pl-8 ${isDark ? 'text-white' : 'text-surface-1'}`}>
            {campaign.name}
          </h3>
          <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold border flex-shrink-0 ${statusConfig.bg} ${statusConfig.text} ${statusConfig.border}`}>
            {statusConfig.label}
          </span>
        </div>
      </div>

      {/* Stats */}
      <div className="p-5">
        <div className="grid grid-cols-2 gap-3 mb-5">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onView();
            }}
            className={`rounded-xl p-3 text-left transition-all hover:scale-[1.02] cursor-pointer ${isDark ? 'bg-surface-3/50 hover:bg-surface-3' : 'bg-surface-light-3 hover:bg-surface-light-4'}`}
          >
            <div className={`text-xs font-medium mb-1 ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>TARGETS</div>
            <div className={`text-2xl font-bold font-mono ${isDark ? 'text-white' : 'text-surface-1'}`}>{campaign.total_targets}</div>
          </button>
          <div className={`rounded-xl p-3 ${isDark ? 'bg-surface-3/50' : 'bg-surface-light-3'}`}>
            <div className={`text-xs font-medium mb-1 ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>OPENED</div>
            <div className="text-primary text-2xl font-bold font-mono">{campaign.opened_count}</div>
            <div className="text-primary/60 text-xs">{openRate}%</div>
          </div>
        </div>

        {/* Click Rate Progress */}
        <div className="mb-5">
          <div className="flex justify-between items-center mb-2">
            <span className={`text-xs font-medium ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>Click Rate</span>
            <span className="text-danger text-sm font-bold font-mono">{clickRate}%</span>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill progress-fill-danger"
              style={{ width: `${clickRate}%` }}
            />
          </div>
          <div className="text-danger/60 text-xs mt-1">{campaign.clicked_count} clicked</div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          <div className="flex gap-2">
            <button
              onClick={onView}
              className="flex-1 group/btn relative px-4 py-2.5 rounded-xl font-medium text-sm text-surface-1 overflow-hidden transition-all duration-300 hover:scale-[1.02]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
              <span className="relative">View Details</span>
            </button>
            <button
              onClick={onDelete}
              className={`px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-300 hover:scale-[1.02] ${
                isDark
                  ? 'bg-danger/10 text-danger hover:bg-danger hover:text-white border border-danger/20'
                  : 'bg-danger/10 text-danger hover:bg-danger hover:text-white border border-danger/20'
              }`}
            >
              Delete
            </button>
          </div>
          <button
            onClick={onViewReport}
            className={`w-full px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-300 hover:scale-[1.02] flex items-center justify-center gap-2 ${
              isDark
                ? 'bg-blue-900/20 text-blue-400 hover:bg-blue-900/30 border border-blue-900/40'
                : 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Awareness Report
          </button>
        </div>
      </div>
    </div>
  );
}

function CreateCampaignForm({ onClose, onSuccess, isDark }) {
  const [formData, setFormData] = useState({
    name: '',
    template_id: '',
    target_emails: '',
    landing_page_id: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [uploadMethod, setUploadMethod] = useState('employees');
  const [emailList, setEmailList] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loadingTemplates, setLoadingTemplates] = useState(true);
  const [landingPages, setLandingPages] = useState([]);
  const [loadingLandingPages, setLoadingLandingPages] = useState(true);

  // Employee selection state
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loadingEmployees, setLoadingEmployees] = useState(true);
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [employeeFilter, setEmployeeFilter] = useState({ department: '', search: '' });

  useEffect(() => {
    loadTemplates();
    loadEmployees();
    loadLandingPages();
  }, []);

  useEffect(() => {
    if (uploadMethod === 'employees') {
      const emails = selectedEmployees.map(emp => emp.email).join(', ');
      setFormData(prev => ({ ...prev, target_emails: emails }));
    }
  }, [selectedEmployees, uploadMethod]);

  const loadTemplates = async () => {
    try {
      setLoadingTemplates(true);
      const response = await getTemplates();
      setTemplates(response.data);
      if (response.data.length > 0) {
        setFormData(prev => ({ ...prev, template_id: response.data[0].id }));
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setLoadingTemplates(false);
    }
  };

  const loadEmployees = async () => {
    try {
      setLoadingEmployees(true);
      const [empResponse, deptResponse] = await Promise.all([
        getEmployees({ is_active: true }),
        getEmployeeDepartments()
      ]);
      setEmployees(empResponse.data);
      setDepartments(deptResponse.data);
    } catch (error) {
      console.error('Error loading employees:', error);
    } finally {
      setLoadingEmployees(false);
    }
  };

  const loadLandingPages = async () => {
    try {
      setLoadingLandingPages(true);
      const response = await getLandingPages();
      const activePages = response.data.filter(p => p.is_active);
      setLandingPages(activePages);
    } catch (error) {
      console.error('Error loading landing pages:', error);
    } finally {
      setLoadingLandingPages(false);
    }
  };

  const toggleEmployee = (employee) => {
    setSelectedEmployees(prev => {
      const exists = prev.find(e => e.id === employee.id);
      if (exists) {
        return prev.filter(e => e.id !== employee.id);
      } else {
        return [...prev, employee];
      }
    });
  };

  const selectAllFiltered = () => {
    const filtered = getFilteredEmployees();
    setSelectedEmployees(prev => {
      const newSelected = [...prev];
      filtered.forEach(emp => {
        if (!newSelected.find(e => e.id === emp.id)) {
          newSelected.push(emp);
        }
      });
      return newSelected;
    });
  };

  const deselectAll = () => {
    setSelectedEmployees([]);
  };

  const getFilteredEmployees = () => {
    return employees.filter(emp => {
      const matchesDept = !employeeFilter.department || emp.department === employeeFilter.department;
      const matchesSearch = !employeeFilter.search ||
        emp.email.toLowerCase().includes(employeeFilter.search.toLowerCase()) ||
        emp.full_name.toLowerCase().includes(employeeFilter.search.toLowerCase());
      return matchesDept && matchesSearch;
    });
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target.result;
        const emails = text.split(/[\n,]/)
          .map(email => email.trim())
          .filter(email => email && email.includes('@'));

        setEmailList(emails);
        setFormData({ ...formData, target_emails: emails.join(', ') });
      };
      reader.readAsText(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await createCampaign(formData);
      onSuccess();
    } catch (error) {
      console.error('Error creating campaign:', error);
      alert('Error creating campaign. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const inputClass = `w-full px-4 py-3 rounded-xl border transition-all duration-200 outline-none ${
    isDark
      ? 'bg-surface-3 border-white/10 text-white placeholder-white/30 focus:border-primary focus:ring-2 focus:ring-primary/20'
      : 'bg-white border-black/10 text-surface-1 placeholder-surface-1/30 focus:border-primary focus:ring-2 focus:ring-primary/20'
  }`;

  return (
    <div className="max-w-4xl mx-auto">
      <div className={`rounded-2xl border overflow-hidden ${isDark ? 'bg-surface-2 border-white/5' : 'bg-white border-black/5 shadow-xl'}`}>
        {/* Header */}
        <div className={`p-6 border-b ${isDark ? 'border-white/5 bg-surface-3/50' : 'border-black/5 bg-surface-light-2'}`}>
          <div className="flex justify-between items-center">
            <div>
              <h2 className={`text-xl font-bold ${isDark ? 'text-white' : 'text-surface-1'}`}>Create Campaign</h2>
              <p className={`text-sm mt-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>Configure phishing simulation parameters</p>
            </div>
            <button
              onClick={onClose}
              className={`p-2 rounded-xl transition-colors ${isDark ? 'hover:bg-white/5 text-white/50' : 'hover:bg-black/5 text-surface-1/50'}`}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
              Campaign Name
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className={inputClass}
              placeholder="e.g., Q1 2024 Security Training"
            />
          </div>

          <div>
            <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
              Template
            </label>
            {loadingTemplates ? (
              <div className={`rounded-xl p-4 text-center ${isDark ? 'bg-surface-3' : 'bg-surface-light-3'}`}>
                <span className={`text-sm ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>Loading templates...</span>
              </div>
            ) : templates.length === 0 ? (
              <div className={`rounded-xl p-4 text-center border ${isDark ? 'bg-warning/10 border-warning/20' : 'bg-warning/10 border-warning/20'}`}>
                <span className="text-warning text-sm">No templates found. Run the seed script or create templates first.</span>
              </div>
            ) : (
              <select
                value={formData.template_id}
                onChange={(e) => setFormData({ ...formData, template_id: e.target.value })}
                className={inputClass}
                required
              >
                {(() => {
                  const categories = [...new Set(templates.map(t => t.category))];
                  return categories.map(category => {
                    const categoryTemplates = templates.filter(t => t.category === category);
                    return (
                      <optgroup key={category} label={category}>
                        {categoryTemplates.map(template => (
                          <option key={template.id} value={template.id}>
                            {template.name} {template.language ? `(${template.language})` : ''} {template.is_builtin ? '' : '- Custom'}
                          </option>
                        ))}
                      </optgroup>
                    );
                  });
                })()}
              </select>
            )}
            {formData.template_id && templates.length > 0 && (
              <p className={`text-xs mt-2 ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>
                Subject: {templates.find(t => t.id === formData.template_id)?.subject}
              </p>
            )}
          </div>

          <div>
            <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
              Landing Page (Credential Harvest)
              <span className={`ml-2 text-xs font-normal ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>(Optional)</span>
            </label>
            {loadingLandingPages ? (
              <div className={`rounded-xl p-4 text-center ${isDark ? 'bg-surface-3' : 'bg-surface-light-3'}`}>
                <span className={`text-sm ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>Loading landing pages...</span>
              </div>
            ) : (
              <>
                <select
                  value={formData.landing_page_id}
                  onChange={(e) => setFormData({ ...formData, landing_page_id: e.target.value })}
                  className={inputClass}
                >
                  <option value="">No Landing Page (tracking only)</option>
                  {landingPages.map(page => (
                    <option key={page.id} value={page.id}>
                      {page.name} {page.page_type === 'cloned' ? '(Cloned)' : ''}
                    </option>
                  ))}
                </select>
                {landingPages.length === 0 && (
                  <p className={`text-xs mt-2 ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>
                    No landing pages available. <Link to="/landing-pages" className="text-primary hover:underline">Create one</Link> in Credential Harvest.
                  </p>
                )}
                {formData.landing_page_id && (
                  <p className="text-success text-xs mt-2">
                    Links in the email will redirect to this credential harvest page.
                  </p>
                )}
              </>
            )}
          </div>

          <div>
            <label className={`block text-sm font-medium mb-3 ${isDark ? 'text-white' : 'text-surface-1'}`}>
              Target Employees
            </label>

            {/* Upload Method Toggle */}
            <div className="grid grid-cols-3 gap-2 mb-4">
              {['employees', 'manual', 'csv'].map((method) => (
                <button
                  key={method}
                  type="button"
                  onClick={() => setUploadMethod(method)}
                  className={`py-2.5 px-4 rounded-xl font-medium text-sm transition-all duration-200 ${
                    uploadMethod === method
                      ? 'bg-primary text-surface-1'
                      : isDark
                        ? 'bg-surface-3 text-white/60 hover:bg-surface-4 border border-white/10'
                        : 'bg-surface-light-3 text-surface-1/60 hover:bg-surface-light-4 border border-black/10'
                  }`}
                >
                  {method === 'employees' ? 'Select Employees' : method === 'manual' ? 'Manual Entry' : 'Upload CSV'}
                </button>
              ))}
            </div>

            {uploadMethod === 'employees' ? (
              <>
                {loadingEmployees ? (
                  <div className={`rounded-xl p-8 text-center ${isDark ? 'bg-surface-3' : 'bg-surface-light-3'}`}>
                    <div className="spinner mx-auto" />
                    <p className={`text-sm mt-3 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>Loading employees...</p>
                  </div>
                ) : employees.length === 0 ? (
                  <div className={`rounded-xl p-8 text-center border ${isDark ? 'bg-surface-3 border-white/5' : 'bg-surface-light-3 border-black/5'}`}>
                    <svg className={`w-12 h-12 mx-auto mb-3 ${isDark ? 'text-white/20' : 'text-surface-1/20'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <p className={`font-medium ${isDark ? 'text-white' : 'text-surface-1'}`}>No employees found</p>
                    <p className={`text-sm mt-1 mb-4 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>Add employees first to select them for campaigns</p>
                    <Link
                      to="/employees"
                      className="inline-block bg-primary text-surface-1 px-4 py-2 rounded-xl font-medium text-sm"
                    >
                      Add Employees
                    </Link>
                  </div>
                ) : (
                  <>
                    {/* Filter and Actions */}
                    <div className="flex flex-col md:flex-row gap-2 mb-3">
                      <input
                        type="text"
                        placeholder="Search employees..."
                        value={employeeFilter.search}
                        onChange={(e) => setEmployeeFilter({ ...employeeFilter, search: e.target.value })}
                        className={`flex-1 ${inputClass}`}
                      />
                      <select
                        value={employeeFilter.department}
                        onChange={(e) => setEmployeeFilter({ ...employeeFilter, department: e.target.value })}
                        className={inputClass}
                        style={{ width: 'auto' }}
                      >
                        <option value="">All Departments</option>
                        {departments.map(dept => (
                          <option key={dept} value={dept}>{dept}</option>
                        ))}
                      </select>
                      <button
                        type="button"
                        onClick={selectAllFiltered}
                        className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                          isDark ? 'bg-surface-3 text-white/60 hover:bg-surface-4' : 'bg-surface-light-3 text-surface-1/60 hover:bg-surface-light-4'
                        }`}
                      >
                        Select All
                      </button>
                      {selectedEmployees.length > 0 && (
                        <button
                          type="button"
                          onClick={deselectAll}
                          className="px-4 py-2.5 rounded-xl text-sm font-medium bg-danger/10 text-danger hover:bg-danger/20 transition-colors"
                        >
                          Clear
                        </button>
                      )}
                    </div>

                    {/* Employee List */}
                    <div className={`border rounded-xl max-h-64 overflow-y-auto ${isDark ? 'border-white/10' : 'border-black/10'}`}>
                      {getFilteredEmployees().map(employee => {
                        const isSelected = selectedEmployees.find(e => e.id === employee.id);
                        return (
                          <div
                            key={employee.id}
                            onClick={() => toggleEmployee(employee)}
                            className={`flex items-center p-3 cursor-pointer transition-colors border-b last:border-b-0 ${
                              isDark ? 'border-white/5' : 'border-black/5'
                            } ${
                              isSelected
                                ? isDark ? 'bg-primary/10' : 'bg-primary/10'
                                : isDark ? 'hover:bg-white/5' : 'hover:bg-black/5'
                            }`}
                          >
                            <div className={`w-5 h-5 rounded border-2 mr-3 flex items-center justify-center transition-colors ${
                              isSelected
                                ? 'bg-primary border-primary'
                                : isDark ? 'border-white/30' : 'border-black/30'
                            }`}>
                              {isSelected && (
                                <svg className="w-3 h-3 text-surface-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className={`font-medium text-sm truncate ${isDark ? 'text-white' : 'text-surface-1'}`}>{employee.full_name}</p>
                              <p className={`text-xs truncate ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>{employee.email}</p>
                            </div>
                            {employee.department && (
                              <span className={`ml-2 px-2 py-0.5 rounded-lg text-xs ${isDark ? 'bg-surface-4 text-white/50' : 'bg-surface-light-4 text-surface-1/50'}`}>
                                {employee.department}
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {/* Selected Count */}
                    {selectedEmployees.length > 0 && (
                      <div className="mt-3 p-3 rounded-xl bg-primary/10 border border-primary/20">
                        <div className="text-primary text-sm font-medium">
                          {selectedEmployees.length} employee(s) selected
                        </div>
                      </div>
                    )}
                  </>
                )}
              </>
            ) : uploadMethod === 'manual' ? (
              <>
                <textarea
                  required
                  value={formData.target_emails}
                  onChange={(e) => setFormData({ ...formData, target_emails: e.target.value })}
                  className={`${inputClass} min-h-[120px]`}
                  placeholder="user1@example.com, user2@example.com, user3@example.com"
                />
                <p className={`text-xs mt-2 ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>
                  Enter email addresses separated by commas or new lines
                </p>
              </>
            ) : (
              <>
                <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                  isDark ? 'border-white/10 hover:border-primary/50 bg-surface-3/50' : 'border-black/10 hover:border-primary/50 bg-surface-light-2'
                }`}>
                  <input
                    type="file"
                    accept=".csv,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="csv-upload"
                  />
                  <label htmlFor="csv-upload" className="cursor-pointer">
                    <svg className={`w-12 h-12 mx-auto mb-3 ${isDark ? 'text-white/30' : 'text-surface-1/30'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <div className={`text-sm font-medium mb-1 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      Click to upload CSV or TXT file
                    </div>
                    <div className={`text-xs ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>
                      One email per line or comma-separated
                    </div>
                  </label>
                </div>

                {emailList.length > 0 && (
                  <div className="mt-3 p-3 rounded-xl bg-success/10 border border-success/20">
                    <div className="text-success text-sm font-medium mb-1">
                      {emailList.length} email(s) loaded
                    </div>
                    <div className="text-success/70 text-xs">
                      {emailList.slice(0, 5).join(', ')}
                      {emailList.length > 5 && ` ...and ${emailList.length - 5} more`}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 group relative px-6 py-3 rounded-xl font-semibold text-surface-1 overflow-hidden transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.01]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
              <span className="relative flex items-center justify-center">
                {submitting ? (
                  <>
                    <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Creating...
                  </>
                ) : 'Create Campaign'}
              </span>
            </button>
            <button
              type="button"
              onClick={onClose}
              className={`px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-200 ${
                isDark
                  ? 'bg-surface-3 text-white border border-white/10 hover:bg-surface-4'
                  : 'bg-surface-light-3 text-surface-1 border border-black/10 hover:bg-surface-light-4'
              }`}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CampaignManager;
