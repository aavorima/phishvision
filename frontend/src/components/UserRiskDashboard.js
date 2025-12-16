import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import {
  getRiskUsers,
  getRiskStats,
  getRiskHeatmap,
  recalculateRiskScores
} from '../api/api';

function UserRiskDashboard() {
  const { isDark } = useTheme();
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [heatmap, setHeatmap] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({ risk_level: '', department: '' });
  const [sortBy, setSortBy] = useState('risk_score');

  const bgColor = isDark ? 'bg-gray-800' : 'bg-white';
  const textColor = isDark ? 'text-white' : 'text-gray-900';
  const textMuted = isDark ? 'text-gray-400' : 'text-gray-500';
  const borderColor = isDark ? 'border-gray-700' : 'border-gray-200';
  const inputBg = isDark ? 'bg-gray-700 text-white' : 'bg-white text-gray-900';

  useEffect(() => {
    fetchData();
  }, [filter, sortBy]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersRes, statsRes, heatmapRes] = await Promise.all([
        getRiskUsers({ ...filter, sort_by: sortBy }),
        getRiskStats(),
        getRiskHeatmap()
      ]);
      setUsers(usersRes.data.users || []);
      setStats(statsRes.data);
      setHeatmap(heatmapRes.data.heatmap || []);
      setError(null);
    } catch (err) {
      setError('Failed to load risk data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    try {
      setRecalculating(true);
      await recalculateRiskScores();
      await fetchData();
    } catch (err) {
      console.error('Failed to recalculate:', err);
    } finally {
      setRecalculating(false);
    }
  };

  const getRiskLevelColor = (level) => {
    const colors = {
      critical: 'bg-red-500 text-white',
      high: 'bg-orange-500 text-white',
      medium: 'bg-yellow-500 text-black',
      low: 'bg-green-500 text-white'
    };
    return colors[level] || 'bg-gray-500 text-white';
  };

  const getRiskScoreColor = (score) => {
    if (score >= 75) return 'text-red-500';
    if (score >= 50) return 'text-orange-500';
    if (score >= 25) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getHeatmapColor = (avgRisk) => {
    if (avgRisk >= 75) return 'bg-red-600';
    if (avgRisk >= 50) return 'bg-orange-500';
    if (avgRisk >= 25) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading && !stats) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className={`${bgColor} rounded-lg p-8 text-center`}>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className={`mt-4 ${textMuted}`}>Loading risk data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className={`text-2xl font-bold ${textColor}`}>User Risk Dashboard</h1>
          <p className={textMuted}>Track and manage user phishing susceptibility</p>
        </div>
        <button
          onClick={handleRecalculate}
          disabled={recalculating}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
        >
          {recalculating ? 'Recalculating...' : 'Recalculate Scores'}
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
            <p className={textMuted + ' text-sm'}>Total Users</p>
            <p className={`text-3xl font-bold ${textColor}`}>{stats.total_users}</p>
          </div>
          <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
            <p className={textMuted + ' text-sm'}>Average Risk Score</p>
            <p className={`text-3xl font-bold ${getRiskScoreColor(stats.average_risk_score)}`}>
              {stats.average_risk_score}
            </p>
          </div>
          <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
            <p className={textMuted + ' text-sm'}>Overall Open Rate</p>
            <p className={`text-3xl font-bold ${textColor}`}>{stats.overall_open_rate || 0}%</p>
          </div>
          <div className={`${bgColor} rounded-lg p-4 border ${borderColor}`}>
            <p className={textMuted + ' text-sm'}>Overall Click Rate</p>
            <p className={`text-3xl font-bold text-red-500`}>{stats.overall_click_rate || 0}%</p>
          </div>
        </div>
      )}

      {/* Risk Distribution */}
      {stats && (
        <div className={`${bgColor} rounded-lg p-4 border ${borderColor} mb-6`}>
          <h3 className={`font-semibold ${textColor} mb-3`}>Risk Level Distribution</h3>
          <div className="flex space-x-4">
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-green-500 mr-2"></span>
              <span className={textMuted}>Low: {stats.risk_level_distribution?.low || 0}</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></span>
              <span className={textMuted}>Medium: {stats.risk_level_distribution?.medium || 0}</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-orange-500 mr-2"></span>
              <span className={textMuted}>High: {stats.risk_level_distribution?.high || 0}</span>
            </div>
            <div className="flex items-center">
              <span className="w-3 h-3 rounded-full bg-red-500 mr-2"></span>
              <span className={textMuted}>Critical: {stats.risk_level_distribution?.critical || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Department Heatmap */}
      {heatmap.length > 0 && (
        <div className={`${bgColor} rounded-lg p-4 border ${borderColor} mb-6`}>
          <h3 className={`font-semibold ${textColor} mb-3`}>Department Risk Heatmap</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {heatmap.map((dept) => (
              <div
                key={dept.department}
                className={`${getHeatmapColor(dept.average_risk)} rounded-lg p-3 text-white`}
              >
                <p className="font-medium truncate">{dept.department}</p>
                <p className="text-2xl font-bold">{dept.average_risk}</p>
                <p className="text-xs opacity-80">{dept.user_count} users</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Risk Users */}
      {stats?.top_risk_users?.length > 0 && (
        <div className={`${bgColor} rounded-lg p-4 border ${borderColor} mb-6`}>
          <h3 className={`font-semibold ${textColor} mb-3`}>Top 10 At-Risk Users</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className={textMuted + ' text-left text-sm'}>
                  <th className="pb-2">Email</th>
                  <th className="pb-2">Department</th>
                  <th className="pb-2">Risk Score</th>
                  <th className="pb-2">Click Rate</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_risk_users.map((user, idx) => (
                  <tr key={user.id} className={`border-t ${borderColor}`}>
                    <td className={`py-2 ${textColor}`}>{user.email}</td>
                    <td className={`py-2 ${textMuted}`}>{user.department || '-'}</td>
                    <td className={`py-2 font-bold ${getRiskScoreColor(user.risk_score)}`}>
                      {user.risk_score}
                    </td>
                    <td className={`py-2 ${textMuted}`}>{user.click_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className={`${bgColor} rounded-lg p-4 border ${borderColor} mb-6`}>
        <div className="flex flex-wrap gap-4">
          <select
            value={filter.risk_level}
            onChange={(e) => setFilter({ ...filter, risk_level: e.target.value })}
            className={`px-3 py-2 rounded border ${borderColor} ${inputBg}`}
          >
            <option value="">All Risk Levels</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className={`px-3 py-2 rounded border ${borderColor} ${inputBg}`}
          >
            <option value="risk_score">Sort by Risk Score</option>
            <option value="email">Sort by Email</option>
            <option value="updated_at">Sort by Last Updated</option>
          </select>
        </div>
      </div>

      {/* User List */}
      <div className={`${bgColor} rounded-lg border ${borderColor}`}>
        <div className={`p-4 border-b ${borderColor}`}>
          <h3 className={`font-semibold ${textColor}`}>All Users ({users.length})</h3>
        </div>

        {users.length === 0 ? (
          <div className="p-8 text-center">
            <p className={textMuted}>No users found. Run a campaign to start tracking user risk.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className={textMuted + ' text-left text-sm border-b ' + borderColor}>
                  <th className="p-4">Email</th>
                  <th className="p-4">Department</th>
                  <th className="p-4">Risk Score</th>
                  <th className="p-4">Risk Level</th>
                  <th className="p-4">Campaigns</th>
                  <th className="p-4">Open Rate</th>
                  <th className="p-4">Click Rate</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className={`border-b ${borderColor} hover:bg-gray-50 dark:hover:bg-gray-700/50`}>
                    <td className={`p-4 ${textColor}`}>{user.email}</td>
                    <td className={`p-4 ${textMuted}`}>{user.department || '-'}</td>
                    <td className={`p-4 font-bold ${getRiskScoreColor(user.risk_score)}`}>
                      {user.risk_score}
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs ${getRiskLevelColor(user.risk_level)}`}>
                        {user.risk_level}
                      </span>
                    </td>
                    <td className={`p-4 ${textMuted}`}>{user.campaigns_received}</td>
                    <td className={`p-4 ${textMuted}`}>{user.open_rate}%</td>
                    <td className={`p-4 ${user.click_rate > 0 ? 'text-red-500' : textMuted}`}>
                      {user.click_rate}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default UserRiskDashboard;
