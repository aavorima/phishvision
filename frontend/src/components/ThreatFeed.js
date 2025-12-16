import React, { useState, useEffect, useCallback } from 'react';
import { useTheme } from '../ThemeContext';
import { useAuth } from '../AuthContext';
import { Link } from 'react-router-dom';
import {
  getThreatFeed,
  getThreatStats,
  searchThreats
} from '../api/api';

function ThreatFeed() {
  const { isDark } = useTheme();
  const { user } = useAuth();
  const [threats, setThreats] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [filters, setFilters] = useState({
    classification: '',
    threat_type: '',
    days: 30
  });

  // Cyber security aesthetic colors
  const colors = {
    bg: isDark ? 'bg-[#0a0e17]' : 'bg-slate-50',
    card: isDark ? 'bg-[#111827]/80' : 'bg-white',
    cardHover: isDark ? 'hover:bg-[#1a2234]' : 'hover:bg-slate-50',
    border: isDark ? 'border-[#1e293b]' : 'border-slate-200',
    text: isDark ? 'text-slate-100' : 'text-slate-900',
    textMuted: isDark ? 'text-slate-400' : 'text-slate-500',
    accent: 'text-cyan-400',
    accentBg: 'bg-cyan-500/10',
    gridLine: isDark ? 'rgba(34, 211, 238, 0.03)' : 'rgba(6, 182, 212, 0.05)'
  };

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [feedRes, statsRes] = await Promise.all([
        getThreatFeed({ page, per_page: 15, ...filters }),
        getThreatStats()
      ]);
      setThreats(feedRes.data.threats || []);
      setTotalPages(feedRes.data.pages || 1);
      setStats(statsRes.data);
      setError(null);
    } catch (err) {
      setError('Failed to load threat feed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchQuery.length < 3) return;

    setIsSearching(true);
    try {
      const res = await searchThreats(searchQuery);
      setSearchResults(res.data);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults(null);
  };

  const getClassificationStyle = (classification) => {
    const styles = {
      malicious: {
        bg: 'bg-red-500/20',
        border: 'border-red-500/50',
        text: 'text-red-400',
        glow: 'shadow-red-500/20'
      },
      suspicious: {
        bg: 'bg-amber-500/20',
        border: 'border-amber-500/50',
        text: 'text-amber-400',
        glow: 'shadow-amber-500/20'
      },
      safe: {
        bg: 'bg-emerald-500/20',
        border: 'border-emerald-500/50',
        text: 'text-emerald-400',
        glow: 'shadow-emerald-500/20'
      }
    };
    return styles[classification] || styles.suspicious;
  };

  const getThreatTypeIcon = (type) => {
    const iconProps = { className: "w-5 h-5", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", strokeWidth: 2 };
    const icons = {
      credential_theft: (
        <svg {...iconProps} className="w-5 h-5 text-amber-500">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
        </svg>
      ),
      bec: (
        <svg {...iconProps} className="w-5 h-5 text-blue-500">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      brand_impersonation: (
        <svg {...iconProps} className="w-5 h-5 text-purple-500">
          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 11l2 2 4-4" />
        </svg>
      ),
      delivery_scam: (
        <svg {...iconProps} className="w-5 h-5 text-orange-500">
          <path strokeLinecap="round" strokeLinejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
      ),
      reward_scam: (
        <svg {...iconProps} className="w-5 h-5 text-pink-500">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
        </svg>
      ),
      tech_support_scam: (
        <svg {...iconProps} className="w-5 h-5 text-slate-500">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      social_engineering: (
        <svg {...iconProps} className="w-5 h-5 text-red-500">
          <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      )
    };
    return icons[type] || (
      <svg {...iconProps} className="w-5 h-5 text-amber-500">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    );
  };

  const formatTimeAgo = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  // Grid background pattern
  const gridPattern = {
    backgroundImage: `
      linear-gradient(${colors.gridLine} 1px, transparent 1px),
      linear-gradient(90deg, ${colors.gridLine} 1px, transparent 1px)
    `,
    backgroundSize: '50px 50px'
  };

  return (
    <div className={`min-h-screen ${colors.bg} ${colors.text}`} style={gridPattern}>
      {/* Header Section */}
      <div className="relative overflow-hidden">
        {/* Gradient overlay */}
        <div className={`absolute inset-0 ${isDark ? 'bg-gradient-to-b from-cyan-500/5 via-transparent to-transparent' : 'bg-gradient-to-b from-cyan-100/50 via-transparent to-transparent'}`} />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Title */}
          <div className="flex items-center gap-4 mb-8">
            <div className={`w-12 h-12 rounded-xl ${isDark ? 'bg-cyan-500/20' : 'bg-cyan-100'} flex items-center justify-center`}>
              <svg className="w-6 h-6 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">
                <span className="text-cyan-500">Threat</span> Intelligence Feed
              </h1>
              <p className={`${colors.textMuted} text-sm font-mono`}>
                Community-driven phishing threat database
              </p>
            </div>
            <div className="ml-auto flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
              </span>
              <span className={`text-xs ${colors.textMuted} font-mono`}>LIVE</span>
            </div>
          </div>

          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
              <StatCard
                label="24H THREATS"
                value={stats.threats_24h}
                icon="clock"
                accent="cyan"
                isDark={isDark}
              />
              <StatCard
                label="7D THREATS"
                value={stats.threats_7d}
                icon="calendar"
                accent="blue"
                isDark={isDark}
              />
              <StatCard
                label="TOTAL IOCs"
                value={stats.total_iocs}
                icon="target"
                accent="purple"
                isDark={isDark}
              />
              <StatCard
                label="MALICIOUS"
                value={stats.classifications?.malicious || 0}
                icon="alert"
                accent="red"
                isDark={isDark}
              />
              <StatCard
                label="SUSPICIOUS"
                value={stats.classifications?.suspicious || 0}
                icon="warning"
                accent="amber"
                isDark={isDark}
              />
              <StatCard
                label="SAFE"
                value={stats.classifications?.safe || 0}
                icon="check"
                accent="emerald"
                isDark={isDark}
              />
            </div>
          )}

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search IOCs: domain, URL, IP address..."
                className={`w-full px-4 py-3 pl-12 rounded-xl ${isDark ? 'bg-[#111827] border-[#1e293b]' : 'bg-white border-slate-200'} border-2 focus:border-cyan-500 focus:ring-0 font-mono text-sm transition-colors ${colors.text}`}
              />
              <svg className={`absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 ${colors.textMuted}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className={`absolute right-4 top-1/2 -translate-y-1/2 ${colors.textMuted} hover:text-cyan-500`}
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </form>

          {/* Search Results */}
          {searchResults && (
            <div className={`mb-6 p-4 rounded-xl ${colors.card} border ${colors.border}`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold">Search Results</h3>
                <button onClick={clearSearch} className="text-sm text-cyan-500 hover:text-cyan-400">
                  Clear
                </button>
              </div>
              {searchResults.found ? (
                <div>
                  <p className="text-sm mb-2">
                    <span className="text-cyan-500 font-mono">{searchResults.match_count}</span> threat(s) found containing "{searchQuery}"
                  </p>
                  {searchResults.is_authenticated && searchResults.threats?.length > 0 && (
                    <div className="space-y-2">
                      {searchResults.threats.map(threat => (
                        <Link
                          key={threat.short_id}
                          to={`/threats/${threat.short_id}`}
                          className={`block p-3 rounded-lg ${isDark ? 'bg-[#0a0e17] hover:bg-[#111827]' : 'bg-slate-50 hover:bg-slate-100'} transition-colors`}
                        >
                          <span className={`font-mono text-sm ${getClassificationStyle(threat.classification).text}`}>
                            {threat.classification.toUpperCase()}
                          </span>
                          <span className="mx-2">·</span>
                          <span className="text-sm">{threat.sanitized_subject}</span>
                        </Link>
                      ))}
                    </div>
                  )}
                  {!searchResults.is_authenticated && (
                    <p className={`text-sm ${colors.textMuted} flex items-center gap-2`}>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                      Login to view detailed results
                    </p>
                  )}
                </div>
              ) : (
                <p className={`text-sm ${colors.textMuted}`}>
                  No threats found matching "{searchQuery}"
                </p>
              )}
            </div>
          )}

          {/* Filters */}
          <div className="flex flex-wrap gap-3 mb-6">
            <select
              value={filters.classification}
              onChange={(e) => setFilters({ ...filters, classification: e.target.value })}
              className={`px-4 py-2 rounded-lg ${isDark ? 'bg-[#111827] border-[#1e293b]' : 'bg-white border-slate-200'} border text-sm font-medium ${colors.text}`}
            >
              <option value="">All Classifications</option>
              <option value="malicious">Malicious</option>
              <option value="suspicious">Suspicious</option>
              <option value="safe">Safe</option>
            </select>

            <select
              value={filters.threat_type}
              onChange={(e) => setFilters({ ...filters, threat_type: e.target.value })}
              className={`px-4 py-2 rounded-lg ${isDark ? 'bg-[#111827] border-[#1e293b]' : 'bg-white border-slate-200'} border text-sm font-medium ${colors.text}`}
            >
              <option value="">All Threat Types</option>
              <option value="credential_theft">Credential Theft</option>
              <option value="bec">BEC</option>
              <option value="brand_impersonation">Brand Impersonation</option>
              <option value="delivery_scam">Delivery Scam</option>
              <option value="social_engineering">Social Engineering</option>
            </select>

            <select
              value={filters.days}
              onChange={(e) => setFilters({ ...filters, days: parseInt(e.target.value) })}
              className={`px-4 py-2 rounded-lg ${isDark ? 'bg-[#111827] border-[#1e293b]' : 'bg-white border-slate-200'} border text-sm font-medium ${colors.text}`}
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>

            <button
              onClick={() => fetchData()}
              className="px-4 py-2 bg-cyan-500/20 text-cyan-500 rounded-lg text-sm font-medium hover:bg-cyan-500/30 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Threat Feed */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {/* Login Banner for guests */}
        {!user && (
          <div className={`mb-6 p-4 rounded-xl ${isDark ? 'bg-cyan-500/10 border-cyan-500/30' : 'bg-cyan-50 border-cyan-200'} border flex items-center justify-between`}>
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg ${isDark ? 'bg-cyan-500/20' : 'bg-cyan-100'} flex items-center justify-center`}>
                <svg className="w-5 h-5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <p className="font-medium text-cyan-500">Want full IOC details?</p>
                <p className={`text-sm ${colors.textMuted}`}>Login to view complete indicators, vote on threats, and submit your own findings.</p>
              </div>
            </div>
            <Link
              to="/login"
              className="px-4 py-2 bg-cyan-500 text-white rounded-lg font-medium hover:bg-cyan-600 transition-colors"
            >
              Sign In
            </Link>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3">
              <svg className="animate-spin h-6 w-6 text-cyan-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="font-mono text-sm">Loading threat data...</span>
            </div>
          </div>
        ) : error ? (
          <div className={`p-6 rounded-xl ${isDark ? 'bg-red-500/10 border-red-500/30' : 'bg-red-50 border-red-200'} border text-center`}>
            <p className="text-red-500">{error}</p>
            <button onClick={fetchData} className="mt-2 text-sm text-cyan-500 hover:underline">
              Try again
            </button>
          </div>
        ) : threats.length === 0 ? (
          <div className={`p-12 rounded-xl ${colors.card} border ${colors.border} text-center`}>
            <div className={`w-16 h-16 mx-auto mb-4 rounded-full ${isDark ? 'bg-slate-700' : 'bg-slate-100'} flex items-center justify-center`}>
              <svg className={`w-8 h-8 ${colors.textMuted}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <h3 className="text-lg font-medium mb-2">No threats found</h3>
            <p className={colors.textMuted}>Try adjusting your filters or check back later.</p>
          </div>
        ) : (
          <>
            {/* Threat Cards */}
            <div className="space-y-3">
              {threats.map((threat, index) => (
                <ThreatCard
                  key={threat.short_id}
                  threat={threat}
                  isDark={isDark}
                  colors={colors}
                  getClassificationStyle={getClassificationStyle}
                  getThreatTypeIcon={getThreatTypeIcon}
                  formatTimeAgo={formatTimeAgo}
                  isAuthenticated={!!user}
                  animationDelay={index * 50}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className={`px-4 py-2 rounded-lg ${isDark ? 'bg-[#111827]' : 'bg-white'} border ${colors.border} disabled:opacity-50 disabled:cursor-not-allowed hover:border-cyan-500 transition-colors flex items-center gap-2`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                  </svg>
                  Previous
                </button>
                <span className={`px-4 py-2 font-mono text-sm ${colors.textMuted}`}>
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className={`px-4 py-2 rounded-lg ${isDark ? 'bg-[#111827]' : 'bg-white'} border ${colors.border} disabled:opacity-50 disabled:cursor-not-allowed hover:border-cyan-500 transition-colors flex items-center gap-2`}
                >
                  Next
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ label, value, icon, accent, isDark }) {
  const accentColors = {
    cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30 text-cyan-500',
    blue: 'from-blue-500/20 to-blue-500/5 border-blue-500/30 text-blue-500',
    purple: 'from-purple-500/20 to-purple-500/5 border-purple-500/30 text-purple-500',
    red: 'from-red-500/20 to-red-500/5 border-red-500/30 text-red-500',
    amber: 'from-amber-500/20 to-amber-500/5 border-amber-500/30 text-amber-500',
    emerald: 'from-emerald-500/20 to-emerald-500/5 border-emerald-500/30 text-emerald-500'
  };

  const getIcon = () => {
    const iconClass = "w-5 h-5";
    const icons = {
      clock: (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      calendar: (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
      target: (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      alert: (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      warning: (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      check: (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    };
    return icons[icon] || icons.alert;
  };

  return (
    <div className={`p-4 rounded-xl bg-gradient-to-br ${accentColors[accent]} border backdrop-blur-sm`}>
      <div className="flex items-center gap-2 mb-1">
        {getIcon()}
        <span className={`text-xs font-mono ${isDark ? 'text-slate-400' : 'text-slate-500'} tracking-wider`}>
          {label}
        </span>
      </div>
      <div className="text-2xl font-bold font-mono">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
    </div>
  );
}

// Threat Card Component
function ThreatCard({
  threat,
  isDark,
  colors,
  getClassificationStyle,
  getThreatTypeIcon,
  formatTimeAgo,
  isAuthenticated,
  animationDelay
}) {
  const style = getClassificationStyle(threat.classification);

  return (
    <Link
      to={`/threats/${threat.short_id}`}
      className={`block p-4 rounded-xl ${colors.card} border ${colors.border} ${colors.cardHover} transition-all duration-200 hover:shadow-lg ${style.glow} group`}
      style={{
        animation: `fadeSlideIn 0.4s ease-out ${animationDelay}ms both`
      }}
    >
      <div className="flex items-start gap-4">
        {/* Classification Badge */}
        <div className={`px-3 py-1 rounded-lg ${style.bg} ${style.text} border ${style.border} font-mono text-xs font-bold uppercase tracking-wider`}>
          {threat.classification}
        </div>

        {/* Main Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{getThreatTypeIcon(threat.threat_type)}</span>
            <span className={`text-sm ${colors.textMuted} font-mono`}>
              {threat.threat_type?.replace(/_/g, ' ') || 'Unknown'}
            </span>
            {threat.detected_brands?.length > 0 && (
              <>
                <span className={colors.textMuted}>·</span>
                <span className="text-sm text-cyan-500 font-medium">
                  {threat.detected_brands.slice(0, 2).join(', ')}
                  {threat.detected_brands.length > 2 && ` +${threat.detected_brands.length - 2}`}
                </span>
              </>
            )}
          </div>

          <h3 className={`font-medium ${colors.text} truncate group-hover:text-cyan-500 transition-colors`}>
            {threat.sanitized_subject || 'No Subject'}
          </h3>

          <div className={`flex items-center gap-4 mt-2 text-xs ${colors.textMuted}`}>
            <span className="font-mono">
              ID: {threat.short_id}
            </span>
            <span>·</span>
            <span>
              {threat.ioc_count} IOC{threat.ioc_count !== 1 ? 's' : ''}
            </span>
            <span>·</span>
            <span>
              {formatTimeAgo(threat.first_seen)}
            </span>
          </div>
        </div>

        {/* Risk Score */}
        <div className="text-right">
          <div className={`text-2xl font-bold font-mono ${style.text}`}>
            {Math.round(threat.risk_score)}
          </div>
          <div className={`text-xs ${colors.textMuted}`}>Risk</div>
        </div>

        {/* Arrow */}
        <svg className={`w-5 h-5 ${colors.textMuted} group-hover:text-cyan-500 group-hover:translate-x-1 transition-all`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </Link>
  );
}

// Add animation keyframes via style tag
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes fadeSlideIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;
document.head.appendChild(styleSheet);

export default ThreatFeed;
