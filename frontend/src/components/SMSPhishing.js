import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import { getSMSCampaigns, createSMSCampaign, deleteSMSCampaign, addSMSTargets, sendSMSCampaign, getSMSTemplates, getSMSStats } from '../api/api';

function SMSPhishing() {
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTargetsModal, setShowTargetsModal] = useState(null);
  const [activeTab, setActiveTab] = useState('campaigns');
  const { isDark } = useTheme();

  // Theme classes
  const cardBg = isDark ? 'bg-slate-800' : 'bg-white';
  const cardBorder = isDark ? 'border-slate-700' : 'border-slate-200';
  const textPrimary = isDark ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDark ? 'text-slate-400' : 'text-slate-500';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [campaignsRes, templatesRes, statsRes] = await Promise.all([
        getSMSCampaigns(),
        getSMSTemplates(),
        getSMSStats()
      ]);
      setCampaigns(campaignsRes.data);
      setTemplates(templatesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this SMS campaign?')) {
      try {
        await deleteSMSCampaign(id);
        loadData();
      } catch (error) {
        console.error('Error deleting:', error);
      }
    }
  };

  const handleSend = async (id) => {
    if (window.confirm('Send this SMS campaign? (Mock mode - no real SMS will be sent)')) {
      try {
        const result = await sendSMSCampaign(id);
        alert(`Campaign sent! ${result.data.results.sent} messages delivered (Mock mode: ${result.data.mock_mode})`);
        loadData();
      } catch (error) {
        console.error('Error sending:', error);
        alert('Failed to send campaign');
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'sent': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className={`h-8 ${isDark ? 'bg-slate-700' : 'bg-slate-200'} rounded w-64`}></div>
          <div className={`h-64 ${isDark ? 'bg-slate-700' : 'bg-slate-200'} rounded`}></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-2xl font-bold ${textPrimary}`}>SMS Phishing (Smishing)</h1>
          <p className={textSecondary}>Create and manage SMS phishing campaigns</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Create SMS Campaign
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Total Campaigns</p>
          <p className={`text-2xl font-bold ${textPrimary}`}>{stats?.total_campaigns || 0}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Total Sent</p>
          <p className="text-2xl font-bold text-blue-500">{stats?.total_sent || 0}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Delivered</p>
          <p className="text-2xl font-bold text-green-500">{stats?.total_delivered || 0}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Clicked</p>
          <p className="text-2xl font-bold text-red-500">{stats?.total_clicked || 0}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Click Rate</p>
          <p className="text-2xl font-bold text-purple-500">
            {stats?.total_sent > 0 ? ((stats?.total_clicked / stats?.total_sent) * 100).toFixed(1) : 0}%
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-slate-700">
        {['campaigns', 'templates'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 font-medium transition-colors capitalize ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-500'
                : textSecondary
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Campaigns Tab */}
      {activeTab === 'campaigns' && (
        <div className="space-y-4">
          {campaigns.map((campaign) => (
            <div key={campaign.id} className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className={`font-semibold ${textPrimary}`}>{campaign.name}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(campaign.status)}`}>
                      {campaign.status}
                    </span>
                  </div>
                  <p className={`text-sm ${textSecondary} mb-2`}>{campaign.description || 'No description'}</p>
                  <div className={`p-3 rounded ${isDark ? 'bg-slate-700' : 'bg-slate-100'} mb-3`}>
                    <p className={`text-sm font-mono ${textPrimary}`}>{campaign.message_template}</p>
                  </div>
                  <div className={`text-sm ${textSecondary} flex gap-4`}>
                    <span>Sender: <span className={textPrimary}>{campaign.sender_id || 'Unknown'}</span></span>
                    <span>Targets: <span className={textPrimary}>{campaign.target_count || 0}</span></span>
                    <span>Sent: <span className={textPrimary}>{campaign.sent_count || 0}</span></span>
                    <span>Clicked: <span className="text-red-500">{campaign.clicked_count || 0}</span></span>
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => setShowTargetsModal(campaign)}
                    className="px-3 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700"
                  >
                    Add Targets
                  </button>
                  {campaign.status === 'draft' && (
                    <button
                      onClick={() => handleSend(campaign.id)}
                      className="px-3 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
                    >
                      Send
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(campaign.id)}
                    className="px-3 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}

          {campaigns.length === 0 && (
            <div className={`text-center py-12 ${textSecondary}`}>
              No SMS campaigns yet. Create one to get started!
            </div>
          )}
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template) => (
            <div key={template.id} className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
              <div className="flex justify-between items-start mb-2">
                <h3 className={`font-semibold ${textPrimary}`}>{template.name}</h3>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(template.difficulty)}`}>
                  {template.difficulty}
                </span>
              </div>
              <span className={`inline-block px-2 py-1 rounded text-xs mb-2 ${isDark ? 'bg-slate-700' : 'bg-slate-100'} ${textSecondary}`}>
                {template.category}
              </span>
              <div className={`p-3 rounded ${isDark ? 'bg-slate-700' : 'bg-slate-100'} mb-3`}>
                <p className={`text-sm ${textPrimary}`}>{template.message}</p>
              </div>
              <button
                onClick={() => {
                  setShowCreateModal(true);
                }}
                className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
              >
                Use Template
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateSMSModal
          templates={templates}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => { setShowCreateModal(false); loadData(); }}
          isDark={isDark}
        />
      )}

      {/* Add Targets Modal */}
      {showTargetsModal && (
        <AddTargetsModal
          campaign={showTargetsModal}
          onClose={() => setShowTargetsModal(null)}
          onSuccess={() => { setShowTargetsModal(null); loadData(); }}
          isDark={isDark}
        />
      )}
    </div>
  );
}

function CreateSMSModal({ templates, onClose, onSuccess, isDark }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    message_template: '',
    sender_id: 'PhishTest'
  });
  const [loading, setLoading] = useState(false);
  const [senderType, setSenderType] = useState('company'); // 'company', 'phone', 'custom'

  // Azerbaijan companies preset
  const azerbaijanCompanies = [
    { value: 'Birbank', label: 'Birbank' },
    { value: 'Umico', label: 'Umico' },
    { value: 'Kapital', label: 'Kapital Bank' },
    { value: 'KapitalBank', label: 'KapitalBank' },
    { value: 'Bakcell', label: 'Bakcell' },
    { value: 'Azercell', label: 'Azercell' },
    { value: 'Azericard', label: 'Azericard' },
    { value: 'Nar', label: 'Nar Mobile' },
    { value: 'ABB', label: 'ABB (Azerbaijan)' },
    { value: 'Pasha', label: 'Pasha Bank' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createSMSCampaign(formData);
      onSuccess();
    } catch (error) {
      console.error('Error creating campaign:', error);
      alert('Failed to create SMS campaign');
    } finally {
      setLoading(false);
    }
  };

  const applyTemplate = (template) => {
    setFormData({
      ...formData,
      message_template: template.message
    });
  };

  const inputClass = isDark
    ? 'w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white'
    : 'w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className={`${isDark ? 'bg-slate-800' : 'bg-white'} rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto relative`}>
        <button
          type="button"
          onClick={onClose}
          className={`absolute top-4 right-4 p-2 rounded-lg transition-colors ${
            isDark
              ? 'text-slate-400 hover:text-white hover:bg-slate-700'
              : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
          }`}
          aria-label="Close modal"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>Create SMS Campaign</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Campaign Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className={inputClass}
              placeholder="e.g., Q4 Security Awareness Test"
              required
            />
          </div>
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className={inputClass}
              rows="2"
            />
          </div>
          {/* Sender ID Section */}
          <div>
            <label className={`block mb-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Sender Type</label>
            <div className="flex gap-4 mb-3">
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  value="company"
                  checked={senderType === 'company'}
                  onChange={(e) => {
                    setSenderType(e.target.value);
                    setFormData({ ...formData, sender_id: 'Birbank' });
                  }}
                  className="mr-2"
                />
                <span className={isDark ? 'text-slate-300' : 'text-slate-700'}>Company Name</span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  value="phone"
                  checked={senderType === 'phone'}
                  onChange={(e) => {
                    setSenderType(e.target.value);
                    setFormData({ ...formData, sender_id: '' }); // Empty = use default Twilio number
                  }}
                  className="mr-2"
                />
                <span className={isDark ? 'text-slate-300' : 'text-slate-700'}>Phone Number</span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  value="custom"
                  checked={senderType === 'custom'}
                  onChange={(e) => {
                    setSenderType(e.target.value);
                    setFormData({ ...formData, sender_id: '' });
                  }}
                  className="mr-2"
                />
                <span className={isDark ? 'text-slate-300' : 'text-slate-700'}>Custom</span>
              </label>
            </div>

            {/* Company Name Dropdown */}
            {senderType === 'company' && (
              <div>
                <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                  Azerbaijan Company
                </label>
                <select
                  value={formData.sender_id}
                  onChange={(e) => setFormData({ ...formData, sender_id: e.target.value })}
                  className={inputClass}
                >
                  {azerbaijanCompanies.map((company) => (
                    <option key={company.value} value={company.value}>
                      {company.label}
                    </option>
                  ))}
                </select>
                <p className={`text-xs mt-1 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                  SMS will appear from: {formData.sender_id}
                </p>
                <div className={`mt-2 p-3 rounded-lg ${isDark ? 'bg-yellow-900/20 border border-yellow-700' : 'bg-yellow-50 border border-yellow-200'}`}>
                  <p className={`text-xs ${isDark ? 'text-yellow-300' : 'text-yellow-800'}`}>
                    ⚠️ <strong>Twilio Trial Limitation:</strong> Alphanumeric sender IDs (company names) require an upgraded Twilio account.
                    Trial accounts can only use phone numbers. To use company names, upgrade your Twilio account at console.twilio.com
                  </p>
                </div>
              </div>
            )}

            {/* Phone Number Input */}
            {senderType === 'phone' && (
              <div>
                <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                  Phone Number (Optional)
                </label>
                <input
                  type="text"
                  value={formData.sender_id}
                  onChange={(e) => setFormData({ ...formData, sender_id: e.target.value })}
                  className={inputClass}
                  placeholder="Leave empty to use your Twilio number"
                />
                <div className={`mt-2 p-3 rounded-lg ${isDark ? 'bg-blue-900/20 border border-blue-700' : 'bg-blue-50 border border-blue-200'}`}>
                  <p className={`text-xs ${isDark ? 'text-blue-300' : 'text-blue-800'}`}>
                    💡 <strong>Tip:</strong> Leave this field empty to automatically use your Twilio phone number (+18166436401).
                    Only enter a custom number if you have registered it with Twilio.
                  </p>
                </div>
              </div>
            )}

            {/* Custom Sender ID */}
            {senderType === 'custom' && (
              <div>
                <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                  Custom Sender ID
                </label>
                <input
                  type="text"
                  value={formData.sender_id}
                  onChange={(e) => setFormData({ ...formData, sender_id: e.target.value })}
                  className={inputClass}
                  placeholder="e.g., BankAlert, IT-Dept, Support"
                />
                <p className={`text-xs mt-1 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                  Max 11 alphanumeric characters
                </p>
              </div>
            )}
          </div>
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Message Template</label>
            <textarea
              value={formData.message_template}
              onChange={(e) => setFormData({ ...formData, message_template: e.target.value })}
              className={inputClass}
              rows="4"
              placeholder="Your message. Use {{link}} for tracking link, {{name}} for recipient name"
              required
            />
            <p className={`text-xs mt-1 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              Variables: {'{{link}}'} - tracking link, {'{{name}}'} - recipient name
            </p>
          </div>

          {/* Quick Templates */}
          <div>
            <label className={`block mb-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Quick Templates</label>
            <div className="flex flex-wrap gap-2">
              {templates.slice(0, 4).map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => applyTemplate(t)}
                  className={`px-3 py-1 rounded text-sm ${isDark ? 'bg-slate-700 hover:bg-slate-600' : 'bg-slate-100 hover:bg-slate-200'} ${isDark ? 'text-slate-300' : 'text-slate-700'}`}
                >
                  {t.name}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 justify-end">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-slate-600 text-white rounded-lg">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
              {loading ? 'Creating...' : 'Create Campaign'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function AddTargetsModal({ campaign, onClose, onSuccess, isDark }) {
  const [targetsText, setTargetsText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Parse targets from text (format: phone,email per line)
      const targets = targetsText.split('\n')
        .filter(line => line.trim())
        .map(line => {
          const [phone, email] = line.split(',').map(s => s.trim());
          return { phone_number: phone, email: email || '' };
        });

      await addSMSTargets(campaign.id, { targets });
      onSuccess();
    } catch (error) {
      console.error('Error adding targets:', error);
      alert('Failed to add targets');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = isDark
    ? 'w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white'
    : 'w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-900';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className={`${isDark ? 'bg-slate-800' : 'bg-white'} rounded-xl p-6 w-full max-w-md`}>
        <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
          Add Targets to "{campaign.name}"
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
              Targets (one per line: phone,email)
            </label>
            <textarea
              value={targetsText}
              onChange={(e) => setTargetsText(e.target.value)}
              className={`${inputClass} font-mono text-sm`}
              rows="8"
              placeholder="+1234567890,user@example.com&#10;+1234567891,user2@example.com"
              required
            />
          </div>
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-slate-600 text-white rounded-lg">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="px-4 py-2 bg-purple-600 text-white rounded-lg">
              {loading ? 'Adding...' : 'Add Targets'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SMSPhishing;
