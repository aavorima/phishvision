import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import { getCampaign } from '../api/api';

function CampaignDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const [campaign, setCampaign] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCampaign();
  }, [id]);

  const loadCampaign = async () => {
    try {
      setLoading(true);
      const response = await getCampaign(id);
      setCampaign(response.data);
    } catch (error) {
      console.error('Error loading campaign:', error);
    } finally {
      setLoading(false);
    }
  };

  const bgPrimary = isDark ? 'bg-gray-900' : 'bg-gray-50';
  const bgCard = isDark ? 'bg-gray-800' : 'bg-white';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-600';
  const borderColor = isDark ? 'border-gray-700' : 'border-gray-200';
  const hoverBg = isDark ? 'hover:bg-gray-700' : 'hover:bg-gray-50';

  if (loading) {
    return <div className={`text-center py-12 ${textPrimary}`}>Loading campaign details...</div>;
  }

  if (!campaign) {
    return <div className={`text-center py-12 ${textPrimary}`}>Campaign not found</div>;
  }

  const openRate = campaign.total_targets > 0
    ? ((campaign.opened_count / campaign.total_targets) * 100).toFixed(1)
    : 0;
  const clickRate = campaign.total_targets > 0
    ? ((campaign.clicked_count / campaign.total_targets) * 100).toFixed(1)
    : 0;

  return (
    <div className={`space-y-6 p-6 ${bgPrimary}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/campaigns')}
            className={`${textSecondary} hover:${textPrimary} transition flex items-center gap-2`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
          <div>
            <h1 className={`text-3xl font-bold ${textPrimary}`}>{campaign.name}</h1>
            <p className={`${textSecondary} mt-1`}>
              Created {new Date(campaign.created_at).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className={`${bgCard} rounded-lg shadow p-6`}>
          <div className={`text-sm ${textSecondary} mb-1`}>Total Sent</div>
          <div className={`text-3xl font-bold ${textPrimary}`}>{campaign.total_targets}</div>
        </div>
        <div className={`${bgCard} rounded-lg shadow p-6`}>
          <div className={`text-sm ${textSecondary} mb-1`}>Opened</div>
          <div className="text-3xl font-bold text-indigo-600">{campaign.opened_count}</div>
          <div className={`text-sm ${textSecondary}`}>{openRate}% open rate</div>
        </div>
        <div className={`${bgCard} rounded-lg shadow p-6`}>
          <div className={`text-sm ${textSecondary} mb-1`}>Clicked</div>
          <div className="text-3xl font-bold text-indigo-600">{campaign.clicked_count}</div>
          <div className={`text-sm ${textSecondary}`}>{clickRate}% click rate</div>
        </div>
        <div className={`${bgCard} rounded-lg shadow p-6`}>
          <div className={`text-sm ${textSecondary} mb-1`}>Status</div>
          <div className="text-2xl font-bold text-green-600 capitalize">{campaign.status}</div>
        </div>
      </div>

      {/* Target Details */}
      <div className={`${bgCard} rounded-lg shadow`}>
        <div className={`p-6 border-b ${borderColor}`}>
          <h2 className={`text-xl font-semibold ${textPrimary}`}>Target Details</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className={isDark ? 'bg-gray-700' : 'bg-gray-50'}>
              <tr>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Email</th>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Sent</th>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Opened</th>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Clicked</th>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase`}>Status</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${borderColor}`}>
              {campaign.targets.map((target) => (
                <tr key={target.id} className={hoverBg}>
                  <td className={`px-6 py-4 text-sm ${textPrimary}`}>{target.email}</td>
                  <td className={`px-6 py-4 text-sm ${textSecondary}`}>
                    {new Date(target.sent_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {target.opened_at ? (
                      <span className="text-indigo-600 flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                        {new Date(target.opened_at).toLocaleString()}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {target.clicked_at ? (
                      <span className="text-indigo-600 flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                        {new Date(target.clicked_at).toLocaleString()}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {target.clicked_at ? (
                      <span className={`px-2 py-1 rounded text-xs font-medium ${isDark ? 'bg-red-900/30 text-red-400' : 'bg-red-100 text-red-800'}`}>
                        Vulnerable
                      </span>
                    ) : target.opened_at ? (
                      <span className={`px-2 py-1 rounded text-xs font-medium ${isDark ? 'bg-yellow-900/30 text-yellow-400' : 'bg-yellow-100 text-yellow-800'}`}>
                        Opened
                      </span>
                    ) : (
                      <span className={`px-2 py-1 rounded text-xs font-medium ${isDark ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-800'}`}>
                        Sent
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default CampaignDetails;
