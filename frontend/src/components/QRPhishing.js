import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import { getQRCampaigns, createQRCampaign, deleteQRCampaign, getQRStats, getQRCampaign } from '../api/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function QRPhishing() {
  const [campaigns, setCampaigns] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [selectedCampaigns, setSelectedCampaigns] = useState([]);
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
      const [campaignsRes, statsRes] = await Promise.all([
        getQRCampaigns(),
        getQRStats()
      ]);
      setCampaigns(campaignsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this QR campaign?')) {
      try {
        await deleteQRCampaign(id);
        loadData();
      } catch (error) {
        console.error('Error deleting:', error);
      }
    }
  };

  const handleBulkDelete = async () => {
    if (selectedCampaigns.length === 0) {
      alert('Please select at least one campaign to delete.');
      return;
    }
    if (window.confirm(`Delete ${selectedCampaigns.length} QR campaign(s)?`)) {
      try {
        await Promise.all(selectedCampaigns.map(id => deleteQRCampaign(id)));
        setSelectedCampaigns([]);
        loadData();
      } catch (error) {
        console.error('Error deleting campaigns:', error);
        alert('Failed to delete some campaigns.');
      }
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

  const downloadQR = (campaignId) => {
    window.open(`${API_BASE_URL}/api/qr/campaigns/${campaignId}/image`, '_blank');
  };

  const downloadPoster = (campaignId) => {
    window.open(`${API_BASE_URL}/api/qr/campaigns/${campaignId}/poster`, '_blank');
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
          <h1 className={`text-2xl font-bold ${textPrimary}`}>QR Code Phishing (Quishing)</h1>
          <p className={textSecondary}>Create and track malicious QR codes for security testing</p>
        </div>
        <div className="flex gap-3">
          {campaigns.length > 0 && (
            <>
              <button
                onClick={toggleSelectAll}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedCampaigns.length === campaigns.length
                    ? 'bg-blue-600 text-white'
                    : isDark
                      ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                      : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                }`}
              >
                {selectedCampaigns.length === campaigns.length ? 'Deselect All' : 'Select All'}
              </button>
              {selectedCampaigns.length > 0 && (
                <button
                  onClick={handleBulkDelete}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Delete Selected ({selectedCampaigns.length})
                </button>
              )}
            </>
          )}
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Create QR Campaign
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Total Campaigns</p>
          <p className={`text-2xl font-bold ${textPrimary}`}>{stats?.total_campaigns || 0}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Active Campaigns</p>
          <p className="text-2xl font-bold text-green-500">{stats?.active_campaigns || 0}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Total Scans</p>
          <p className="text-2xl font-bold text-blue-500">{stats?.total_scans || 0}</p>
        </div>
        <div className={`${cardBg} rounded-xl p-4 border ${cardBorder}`}>
          <p className={textSecondary}>Unique Scanners</p>
          <p className="text-2xl font-bold text-purple-500">{stats?.unique_scanners || 0}</p>
        </div>
      </div>

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {campaigns.map((campaign) => {
          const isSelected = selectedCampaigns.includes(campaign.id);
          return (
            <div
              key={campaign.id}
              className={`${cardBg} rounded-xl border ${
                isSelected
                  ? 'border-blue-500 shadow-lg shadow-blue-500/20'
                  : cardBorder
              } overflow-hidden relative transition-all`}
            >
              {/* Selection Checkbox */}
              <div className="absolute top-4 left-4 z-10">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleCampaignSelection(campaign.id);
                  }}
                  className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-all ${
                    isSelected
                      ? 'bg-blue-600 border-blue-600'
                      : isDark
                        ? 'bg-slate-700 border-slate-500 hover:border-blue-500'
                        : 'bg-white border-slate-400 hover:border-blue-500'
                  }`}
                >
                  {isSelected && (
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              </div>

              {/* QR Code Preview */}
              <div className="p-4 bg-white flex justify-center">
                <img
                  src={`${API_BASE_URL}/api/qr/campaigns/${campaign.id}/image`}
                  alt="QR Code"
                  className="w-48 h-48 object-contain"
                />
              </div>

              {/* Campaign Info */}
              <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className={`font-semibold ${textPrimary}`}>{campaign.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    campaign.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {campaign.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

              <p className={`text-sm ${textSecondary} mb-3`}>{campaign.description || 'No description'}</p>

              <div className={`text-sm ${textSecondary} space-y-1 mb-4`}>
                <p><span className="font-medium">Location:</span> {campaign.placement_location || 'Not specified'}</p>
                <p><span className="font-medium">Scans:</span> {campaign.scan_count || 0}</p>
              </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => downloadQR(campaign.id)}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
                  >
                    Download QR
                  </button>
                  <button
                    onClick={() => downloadPoster(campaign.id)}
                    className="flex-1 px-3 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700"
                  >
                    Get Poster
                  </button>
                  <button
                    onClick={() => setSelectedCampaign(campaign)}
                    className="px-3 py-2 bg-slate-600 text-white rounded-lg text-sm hover:bg-slate-700"
                  >
                    Stats
                  </button>
                  <button
                    onClick={() => handleDelete(campaign.id)}
                    className="px-3 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {campaigns.length === 0 && (
          <div className={`col-span-3 text-center py-12 ${textSecondary}`}>
            No QR campaigns yet. Create one to get started!
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateQRModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => { setShowCreateModal(false); loadData(); }}
          isDark={isDark}
        />
      )}

      {/* Stats Modal */}
      {selectedCampaign && (
        <CampaignStatsModal
          campaign={selectedCampaign}
          onClose={() => setSelectedCampaign(null)}
          isDark={isDark}
        />
      )}
    </div>
  );
}

function CreateQRModal({ onClose, onSuccess, isDark }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    placement_location: '',
    color: '#1a73e8'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createQRCampaign(formData);
      onSuccess();
    } catch (error) {
      console.error('Error creating campaign:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to create QR campaign';
      alert(errorMessage);
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
        <h2 className={`text-xl font-bold mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>Create QR Campaign</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Campaign Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className={inputClass}
              placeholder="e.g., Break Room WiFi Test"
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
              placeholder="Purpose of this QR campaign"
            />
          </div>
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Placement Location</label>
            <input
              type="text"
              value={formData.placement_location}
              onChange={(e) => setFormData({ ...formData, placement_location: e.target.value })}
              className={inputClass}
              placeholder="e.g., Break room poster, Elevator notice"
            />
          </div>
          <div>
            <label className={`block mb-1 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>QR Code Color</label>
            <div className="flex gap-2">
              <input
                type="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="w-12 h-10 rounded cursor-pointer"
              />
              <input
                type="text"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className={inputClass}
              />
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

function CampaignStatsModal({ campaign, onClose, isDark }) {
  const [campaignDetails, setCampaignDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const textPrimary = isDark ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDark ? 'text-slate-400' : 'text-slate-500';

  useEffect(() => {
    loadCampaignDetails();
  }, [campaign.id]);

  const loadCampaignDetails = async () => {
    try {
      setLoading(true);
      const response = await getQRCampaign(campaign.id);
      setCampaignDetails(response.data);
    } catch (error) {
      console.error('Error loading campaign details:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className={`${isDark ? 'bg-slate-800' : 'bg-white'} rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto`}>
        <h2 className={`text-xl font-bold mb-4 ${textPrimary}`}>{campaign.name} - Statistics</h2>

        {loading ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <>
            <div className="space-y-4 mb-6">
              <div className="grid grid-cols-2 gap-4">
                <div className={`p-4 rounded-lg ${isDark ? 'bg-slate-700' : 'bg-slate-100'}`}>
                  <p className={textSecondary}>Total Scans</p>
                  <p className={`text-2xl font-bold ${textPrimary}`}>{campaign.scan_count || 0}</p>
                </div>
                <div className={`p-4 rounded-lg ${isDark ? 'bg-slate-700' : 'bg-slate-100'}`}>
                  <p className={textSecondary}>Status</p>
                  <p className={`text-2xl font-bold ${campaign.is_active ? 'text-green-500' : 'text-gray-500'}`}>
                    {campaign.is_active ? 'Active' : 'Inactive'}
                  </p>
                </div>
              </div>

              <div className={`p-4 rounded-lg ${isDark ? 'bg-slate-700' : 'bg-slate-100'}`}>
                <p className={`font-medium ${textPrimary} mb-2`}>Target URL</p>
                <p className={`text-sm ${textSecondary} break-all`}>{campaign.target_url}</p>
              </div>

              <div className={`p-4 rounded-lg ${isDark ? 'bg-slate-700' : 'bg-slate-100'}`}>
                <p className={`font-medium ${textPrimary} mb-2`}>Placement</p>
                <p className={`text-sm ${textSecondary}`}>{campaign.placement_location || 'Not specified'}</p>
              </div>

              <div className={`p-4 rounded-lg ${isDark ? 'bg-slate-700' : 'bg-slate-100'}`}>
                <p className={`font-medium ${textPrimary} mb-2`}>Created</p>
                <p className={`text-sm ${textSecondary}`}>{new Date(campaign.created_at).toLocaleDateString()}</p>
              </div>
            </div>

            {/* Target Details Table */}
            {campaignDetails && campaignDetails.targets && (
              <div className={`rounded-lg border ${isDark ? 'border-slate-700' : 'border-slate-200'} overflow-hidden`}>
                <div className={`p-4 border-b ${isDark ? 'border-slate-700 bg-slate-700' : 'border-slate-200 bg-slate-50'}`}>
                  <h3 className={`font-semibold ${textPrimary}`}>Target Details</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className={isDark ? 'bg-slate-700' : 'bg-slate-50'}>
                      <tr>
                        <th className={`px-4 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Name</th>
                        <th className={`px-4 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Email</th>
                        <th className={`px-4 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Department</th>
                        <th className={`px-4 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Sent</th>
                        <th className={`px-4 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Scanned</th>
                      </tr>
                    </thead>
                    <tbody className={`divide-y ${isDark ? 'divide-slate-700' : 'divide-slate-200'}`}>
                      {campaignDetails.targets.length === 0 ? (
                        <tr>
                          <td colSpan="5" className={`px-4 py-8 text-center ${textSecondary}`}>
                            No targets added yet
                          </td>
                        </tr>
                      ) : (
                        campaignDetails.targets.map((target) => (
                          <tr key={target.id} className={isDark ? 'hover:bg-slate-700' : 'hover:bg-slate-50'}>
                            <td className={`px-4 py-3 text-sm ${textPrimary}`}>{target.name || '—'}</td>
                            <td className={`px-4 py-3 text-sm ${textPrimary}`}>{target.email}</td>
                            <td className={`px-4 py-3 text-sm ${textSecondary}`}>{target.department || '—'}</td>
                            <td className={`px-4 py-3 text-sm ${textSecondary}`}>
                              {target.sent_at ? new Date(target.sent_at).toLocaleString() : '—'}
                            </td>
                            <td className="px-4 py-3 text-sm">
                              {target.scanned_at ? (
                                <span className="text-red-500 flex items-center gap-1">
                                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                                  </svg>
                                  {new Date(target.scanned_at).toLocaleString()}
                                </span>
                              ) : (
                                <span className="text-gray-400">Not scanned</span>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

        <div className="mt-6 flex justify-end">
          <button onClick={onClose} className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default QRPhishing;
