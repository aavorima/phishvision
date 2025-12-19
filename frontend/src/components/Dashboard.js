import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardStats, getRecentActivity, getThreatDistribution, getCampaignPerformance, getSOCMetrics, getRiskStats } from '../api/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { useTheme } from '../ThemeContext';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [threatDist, setThreatDist] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [socMetrics, setSocMetrics] = useState(null);
  const [riskStats, setRiskStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');
  const { isDark } = useTheme();

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, activityRes, threatRes, campaignRes, socRes, riskRes] = await Promise.all([
        getDashboardStats(),
        getRecentActivity(),
        getThreatDistribution(),
        getCampaignPerformance(),
        getSOCMetrics(30).catch(() => ({ data: null })),
        getRiskStats().catch(() => ({ data: null }))
      ]);
      setStats(statsRes.data);
      setActivity(activityRes.data);
      setThreatDist(threatRes.data);
      setCampaigns(campaignRes.data);
      setSocMetrics(socRes.data);
      setRiskStats(riskRes.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${isDark ? 'bg-[#0a0a0f]' : 'bg-[#f5f6f8]'}`}>
        <div className="p-8">
          <div className="animate-pulse space-y-6">
            <div className={`h-8 w-48 rounded ${isDark ? 'bg-white/5' : 'bg-black/5'}`} />
            <div className="grid grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className={`h-28 rounded-lg ${isDark ? 'bg-white/5' : 'bg-black/5'}`} />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const threatData = threatDist ? [
    { name: 'Safe', value: threatDist.safe, color: '#22c55e' },
    { name: 'Suspicious', value: threatDist.suspicious, color: '#f59e0b' },
    { name: 'Malicious', value: threatDist.malicious, color: '#ef4444' }
  ].filter(item => item.value > 0) : [];

  const totalThreats = threatData.reduce((sum, item) => sum + item.value, 0);

  // Calculate key percentages
  const openRate = stats?.phishing_simulation?.open_rate || 0;
  const clickRate = stats?.phishing_simulation?.click_rate || 0;
  const reportRate = stats?.phishing_simulation?.report_rate || 0;
  const securityScore = socMetrics?.security_posture_score || 85;

  return (
    <div className={`min-h-full ${isDark ? 'bg-[#0a0a0f]' : 'bg-[#f5f6f8]'}`}>
      <div className="max-w-[1800px] mx-auto p-6 space-y-6">

        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className={`text-2xl font-semibold tracking-tight ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Security Dashboard
            </h1>
            <div className="flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              <span className={`text-xs font-medium ${isDark ? 'text-emerald-400' : 'text-emerald-600'}`}>Live</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Time Range Selector */}
            <div className={`flex rounded-lg p-1 ${isDark ? 'bg-white/5' : 'bg-black/5'}`}>
              {['24h', '7d', '30d', '90d'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors duration-150 ${
                    timeRange === range
                      ? isDark ? 'bg-white/10 text-white' : 'bg-white text-gray-900 shadow-sm'
                      : isDark ? 'text-white/50 hover:text-white/80' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>

            <button
              onClick={loadData}
              className={`p-2 rounded-lg transition-colors duration-150 ${isDark ? 'hover:bg-white/5 text-white/50 hover:text-white' : 'hover:bg-black/5 text-gray-400 hover:text-gray-600'}`}
              title="Refresh data"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>

        {/* Security Score Hero Card */}
        <div className={`relative overflow-hidden rounded-2xl ${isDark ? 'bg-gradient-to-br from-[#12141a] to-[#0d0f14] border border-white/5' : 'bg-white border border-black/5 shadow-sm'}`}>
          <div className="absolute inset-0 opacity-30">
            <div className={`absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl ${securityScore >= 70 ? 'bg-emerald-500/20' : securityScore >= 40 ? 'bg-amber-500/20' : 'bg-red-500/20'}`} />
          </div>

          <div className="relative p-8">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className={`text-sm font-medium uppercase tracking-wider mb-2 ${isDark ? 'text-white/40' : 'text-gray-400'}`}>
                  Organization Security Score
                </p>
                <div className="flex items-baseline gap-3">
                  <span className={`text-7xl font-bold tracking-tight tabular-nums ${
                    securityScore >= 70 ? 'text-emerald-500' : securityScore >= 40 ? 'text-amber-500' : 'text-red-500'
                  }`}>
                    {securityScore}
                  </span>
                  <span className={`text-2xl ${isDark ? 'text-white/30' : 'text-gray-300'}`}>/100</span>
                </div>
                <p className={`mt-3 text-sm ${isDark ? 'text-white/50' : 'text-gray-500'}`}>
                  {securityScore >= 70 ? 'Your organization has strong security awareness' :
                   securityScore >= 40 ? 'Room for improvement in security training' :
                   'Immediate attention required'}
                </p>
              </div>

              {/* Quick Stats */}
              <div className="flex gap-8">
                <QuickStat
                  label="Phishing Tests"
                  value={stats?.campaigns?.total || 0}
                  change={`${stats?.campaigns?.active || 0} active`}
                  isDark={isDark}
                />
                <QuickStat
                  label="Emails Analyzed"
                  value={stats?.email_analysis?.total_analyzed || 0}
                  change={`${stats?.email_analysis?.malicious || 0} threats`}
                  isDark={isDark}
                />
                <QuickStat
                  label="Users Trained"
                  value={riskStats?.total_users || 0}
                  change={`${riskStats?.risk_level_distribution?.low || 0} low risk`}
                  isDark={isDark}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics Row */}
        <div className="grid grid-cols-4 gap-4">
          <MetricCard
            title="Open Rate"
            value={`${openRate.toFixed(1)}%`}
            description="Emails opened by recipients"
            trend={openRate > 50 ? 'warning' : 'success'}
            icon={<IconEnvelope />}
            isDark={isDark}
          />
          <MetricCard
            title="Click Rate"
            value={`${clickRate.toFixed(1)}%`}
            description="Clicked phishing links"
            trend={clickRate > 20 ? 'danger' : clickRate > 10 ? 'warning' : 'success'}
            icon={<IconCursor />}
            isDark={isDark}
          />
          <MetricCard
            title="Report Rate"
            value={`${reportRate.toFixed(1)}%`}
            description="Reported as suspicious"
            trend={reportRate > 30 ? 'success' : 'warning'}
            icon={<IconFlag />}
            isDark={isDark}
          />
          <MetricCard
            title="Repeat Clickers"
            value={riskStats?.risk_level_distribution?.critical || 0}
            description="High-risk employees"
            trend={(riskStats?.risk_level_distribution?.critical || 0) > 5 ? 'danger' : 'success'}
            icon={<IconUsers />}
            isDark={isDark}
          />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-12 gap-6">

          {/* Threat Analysis - Left Column */}
          <div className="col-span-4 space-y-6">

            {/* Threat Distribution */}
            <div className={`rounded-xl p-6 ${isDark ? 'bg-[#12141a] border border-white/5' : 'bg-white border border-black/5 shadow-sm'}`}>
              <div className="flex items-center justify-between mb-6">
                <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>Threat Analysis</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-white/5 text-white/50' : 'bg-gray-100 text-gray-500'}`}>
                  {totalThreats} total
                </span>
              </div>

              {threatData.length > 0 ? (
                <>
                  <div className="relative">
                    <ResponsiveContainer width="100%" height={180}>
                      <PieChart>
                        <Pie
                          data={threatData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={75}
                          paddingAngle={2}
                          dataKey="value"
                          strokeWidth={0}
                        >
                          {threatData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            backgroundColor: isDark ? '#1a1c23' : '#ffffff',
                            border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                            borderRadius: '8px',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                          }}
                          itemStyle={{ color: isDark ? '#fff' : '#000' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                    {/* Center Label */}
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
                          {threatDist?.malicious || 0}
                        </div>
                        <div className={`text-xs ${isDark ? 'text-white/40' : 'text-gray-400'}`}>Threats</div>
                      </div>
                    </div>
                  </div>

                  {/* Legend */}
                  <div className="space-y-3 mt-4">
                    {threatData.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: item.color }} />
                          <span className={`text-sm ${isDark ? 'text-white/70' : 'text-gray-600'}`}>{item.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`text-sm font-semibold tabular-nums ${isDark ? 'text-white' : 'text-gray-900'}`}>
                            {item.value}
                          </span>
                          <span className={`text-xs ${isDark ? 'text-white/30' : 'text-gray-400'}`}>
                            ({((item.value / totalThreats) * 100).toFixed(0)}%)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <EmptyState message="No threat data available" isDark={isDark} />
              )}
            </div>

          </div>

          {/* Campaign Performance - Center Column */}
          <div className="col-span-5">
            <div className={`rounded-xl p-6 h-full ${isDark ? 'bg-[#12141a] border border-white/5' : 'bg-white border border-black/5 shadow-sm'}`}>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>Campaign Performance</h3>
                  <p className={`text-sm mt-1 ${isDark ? 'text-white/40' : 'text-gray-500'}`}>Open vs Click rates over time</p>
                </div>
                <Link to="/campaigns" className={`text-xs font-medium ${isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700'}`}>
                  View All →
                </Link>
              </div>

              {campaigns.length > 0 ? (
                <ResponsiveContainer width="100%" height={320}>
                  <AreaChart data={campaigns.slice(0, 8)} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorOpen" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorClick" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'} />
                    <XAxis
                      dataKey="name"
                      stroke={isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)'}
                      tick={{ fill: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)', fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      stroke={isDark ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.3)'}
                      tick={{ fill: isDark ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.5)', fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(v) => `${v}%`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: isDark ? '#1a1c23' : '#ffffff',
                        border: isDark ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0,0,0,0.1)',
                        borderRadius: '8px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                      }}
                      labelStyle={{ color: isDark ? '#fff' : '#000', marginBottom: '4px' }}
                      itemStyle={{ color: isDark ? '#fff' : '#000' }}
                    />
                    <Legend
                      verticalAlign="top"
                      height={36}
                      formatter={(value) => <span style={{ color: isDark ? 'rgba(255,255,255,0.7)' : 'rgba(0,0,0,0.7)', fontSize: '12px' }}>{value}</span>}
                    />
                    <Area
                      type="monotone"
                      dataKey="open_rate"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorOpen)"
                      name="Open Rate %"
                    />
                    <Area
                      type="monotone"
                      dataKey="click_rate"
                      stroke="#ef4444"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorClick)"
                      name="Click Rate %"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState message="No campaign data available" isDark={isDark} />
              )}
            </div>
          </div>

          {/* Activity Feed - Right Column */}
          <div className="col-span-3">
            <div className={`rounded-xl p-6 h-full ${isDark ? 'bg-[#12141a] border border-white/5' : 'bg-white border border-black/5 shadow-sm'}`}>
              <div className="flex items-center justify-between mb-6">
                <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>Recent Activity</h3>
                <div className="flex items-center gap-1.5">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500" />
                  </span>
                  <span className={`text-xs ${isDark ? 'text-white/40' : 'text-gray-400'}`}>Live</span>
                </div>
              </div>

              <div className="space-y-1 max-h-[360px] overflow-y-auto scrollbar-thin">
                {activity.length > 0 ? (
                  activity.slice(0, 15).map((item, index) => (
                    <ActivityRow key={index} item={item} isDark={isDark} />
                  ))
                ) : (
                  <EmptyState message="No recent activity" isDark={isDark} />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* User Risk Distribution */}
        {riskStats && riskStats.total_users > 0 && (
          <div className={`rounded-xl p-6 ${isDark ? 'bg-[#12141a] border border-white/5' : 'bg-white border border-black/5 shadow-sm'}`}>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className={`font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>Employee Risk Distribution</h3>
                <p className={`text-sm mt-1 ${isDark ? 'text-white/40' : 'text-gray-500'}`}>
                  {riskStats.total_users} employees tracked • Average risk score: {riskStats.average_risk_score}
                </p>
              </div>
              <Link to="/risk" className={`text-xs font-medium ${isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700'}`}>
                View Details →
              </Link>
            </div>

            {/* Risk Level Bar */}
            <div className="flex h-10 rounded-lg overflow-hidden">
              <RiskSegment
                label="Low"
                count={riskStats.risk_level_distribution?.low || 0}
                total={riskStats.total_users}
                color="#22c55e"
                isDark={isDark}
              />
              <RiskSegment
                label="Medium"
                count={riskStats.risk_level_distribution?.medium || 0}
                total={riskStats.total_users}
                color="#f59e0b"
                isDark={isDark}
              />
              <RiskSegment
                label="High"
                count={riskStats.risk_level_distribution?.high || 0}
                total={riskStats.total_users}
                color="#f97316"
                isDark={isDark}
              />
              <RiskSegment
                label="Critical"
                count={riskStats.risk_level_distribution?.critical || 0}
                total={riskStats.total_users}
                color="#ef4444"
                isDark={isDark}
              />
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-8 mt-4">
              <RiskLegendItem label="Low Risk" count={riskStats.risk_level_distribution?.low || 0} color="#22c55e" isDark={isDark} />
              <RiskLegendItem label="Medium" count={riskStats.risk_level_distribution?.medium || 0} color="#f59e0b" isDark={isDark} />
              <RiskLegendItem label="High" count={riskStats.risk_level_distribution?.high || 0} color="#f97316" isDark={isDark} />
              <RiskLegendItem label="Critical" count={riskStats.risk_level_distribution?.critical || 0} color="#ef4444" isDark={isDark} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Sub-components

function QuickStat({ label, value, change, isDark }) {
  return (
    <div className="text-right">
      <div className={`text-3xl font-bold tabular-nums ${isDark ? 'text-white' : 'text-gray-900'}`}>{value}</div>
      <div className={`text-sm ${isDark ? 'text-white/40' : 'text-gray-500'}`}>{label}</div>
      <div className={`text-xs mt-1 ${isDark ? 'text-white/30' : 'text-gray-400'}`}>{change}</div>
    </div>
  );
}

function MetricCard({ title, value, description, trend, icon, isDark }) {
  const trendColors = {
    success: { bg: isDark ? 'bg-emerald-500/10' : 'bg-emerald-50', text: 'text-emerald-500', border: 'border-emerald-500/20' },
    warning: { bg: isDark ? 'bg-amber-500/10' : 'bg-amber-50', text: 'text-amber-500', border: 'border-amber-500/20' },
    danger: { bg: isDark ? 'bg-red-500/10' : 'bg-red-50', text: 'text-red-500', border: 'border-red-500/20' },
  };
  const colors = trendColors[trend] || trendColors.success;

  return (
    <div className={`relative rounded-xl p-5 transition-colors duration-200 ${isDark ? 'bg-[#12141a] border border-white/5 hover:border-white/10' : 'bg-white border border-black/5 shadow-sm hover:shadow-md'}`}>
      <div className={`absolute top-0 left-0 right-0 h-1 rounded-t-xl ${colors.bg}`} />
      <div className="flex items-start justify-between">
        <div>
          <div className={`text-sm font-medium ${isDark ? 'text-white/50' : 'text-gray-500'}`}>{title}</div>
          <div className={`text-3xl font-bold mt-1 tabular-nums ${colors.text}`}>{value}</div>
          <div className={`text-xs mt-2 ${isDark ? 'text-white/30' : 'text-gray-400'}`}>{description}</div>
        </div>
        <div className={`p-2 rounded-lg ${colors.bg}`}>
          <div className={colors.text}>{icon}</div>
        </div>
      </div>
    </div>
  );
}

function SeverityBadge({ label, count, color, isDark }) {
  const colorMap = {
    red: { bg: 'bg-red-500/10', text: 'text-red-500' },
    orange: { bg: 'bg-orange-500/10', text: 'text-orange-500' },
    yellow: { bg: 'bg-amber-500/10', text: 'text-amber-500' },
    green: { bg: 'bg-emerald-500/10', text: 'text-emerald-500' },
  };
  const colors = colorMap[color];

  return (
    <div className={`flex-1 text-center py-2 rounded-lg ${colors.bg}`}>
      <div className={`text-lg font-bold tabular-nums ${colors.text}`}>{count}</div>
      <div className={`text-xs ${isDark ? 'text-white/40' : 'text-gray-500'}`}>{label}</div>
    </div>
  );
}

function ActivityRow({ item, isDark }) {
  const getTypeStyle = (type) => {
    if (type?.includes('click')) return { color: 'bg-red-500', label: 'Click' };
    if (type?.includes('open')) return { color: 'bg-blue-500', label: 'Open' };
    if (type?.includes('malicious') || type?.includes('threat')) return { color: 'bg-orange-500', label: 'Threat' };
    if (type?.includes('report')) return { color: 'bg-emerald-500', label: 'Report' };
    return { color: 'bg-gray-500', label: 'Event' };
  };
  const style = getTypeStyle(item.type);

  return (
    <div className={`group flex items-start gap-3 p-3 rounded-lg transition-colors duration-150 cursor-default ${isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50'}`}>
      <div className={`w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0 ${style.color}`} />
      <div className="flex-1 min-w-0">
        <p className={`text-sm truncate ${isDark ? 'text-white/80' : 'text-gray-700'}`}>{item.description}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className={`text-xs ${isDark ? 'text-white/30' : 'text-gray-400'}`}>
            {formatTimeAgo(item.timestamp)}
          </span>
          <span className={`text-xs px-1.5 py-0.5 rounded ${isDark ? 'bg-white/5 text-white/40' : 'bg-gray-100 text-gray-500'}`}>
            {style.label}
          </span>
        </div>
      </div>
    </div>
  );
}

function RiskSegment({ label, count, total, color, isDark }) {
  const percentage = total > 0 ? (count / total) * 100 : 0;
  if (percentage === 0) return null;

  return (
    <div
      className="flex items-center justify-center transition-opacity duration-150 hover:opacity-80 cursor-default"
      style={{ width: `${percentage}%`, backgroundColor: color }}
      title={`${label}: ${count} (${percentage.toFixed(1)}%)`}
    >
      {percentage > 10 && (
        <span className="text-xs font-semibold text-white">{count}</span>
      )}
    </div>
  );
}

function RiskLegendItem({ label, count, color, isDark }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
      <span className={`text-sm ${isDark ? 'text-white/60' : 'text-gray-600'}`}>{label}</span>
      <span className={`text-sm font-semibold tabular-nums ${isDark ? 'text-white' : 'text-gray-900'}`}>{count}</span>
    </div>
  );
}

function EmptyState({ message, isDark }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-3 ${isDark ? 'bg-white/5' : 'bg-gray-100'}`}>
        <svg className={`w-6 h-6 ${isDark ? 'text-white/20' : 'text-gray-300'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </div>
      <p className={`text-sm ${isDark ? 'text-white/30' : 'text-gray-400'}`}>{message}</p>
    </div>
  );
}

// Helper function
function formatTimeAgo(timestamp) {
  const now = new Date();
  const time = new Date(timestamp);
  const diff = Math.floor((now - time) / 1000);

  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

// Icons
function IconEnvelope() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  );
}

function IconCursor() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
    </svg>
  );
}

function IconFlag() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
    </svg>
  );
}

function IconUsers() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  );
}

export default Dashboard;
