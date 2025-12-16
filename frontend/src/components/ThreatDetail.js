import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import { useAuth } from '../AuthContext';
import { getThreatEntry, voteOnThreat } from '../api/api';

function ThreatDetail() {
  const { shortId } = useParams();
  const { isDark } = useTheme();
  const { user } = useAuth();
  const [threat, setThreat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userVote, setUserVote] = useState(null);
  const [isVoting, setIsVoting] = useState(false);
  const [copiedIOC, setCopiedIOC] = useState(null);

  const colors = {
    bg: isDark ? 'bg-[#0a0e17]' : 'bg-slate-50',
    card: isDark ? 'bg-[#111827]/80' : 'bg-white',
    border: isDark ? 'border-[#1e293b]' : 'border-slate-200',
    text: isDark ? 'text-slate-100' : 'text-slate-900',
    textMuted: isDark ? 'text-slate-400' : 'text-slate-500',
    gridLine: isDark ? 'rgba(34, 211, 238, 0.03)' : 'rgba(6, 182, 212, 0.05)'
  };

  useEffect(() => {
    fetchThreat();
  }, [shortId]);

  const fetchThreat = async () => {
    try {
      setLoading(true);
      const res = await getThreatEntry(shortId);
      setThreat(res.data.threat);
      setUserVote(res.data.user_vote);
      setError(null);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Threat entry not found');
      } else {
        setError('Failed to load threat details');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (voteType) => {
    if (!user || isVoting) return;

    setIsVoting(true);
    try {
      const res = await voteOnThreat(shortId, voteType);
      setUserVote(voteType);
      setThreat(prev => ({
        ...prev,
        community_votes: res.data.community_votes
      }));
    } catch (err) {
      console.error('Vote failed:', err);
    } finally {
      setIsVoting(false);
    }
  };

  const copyToClipboard = async (text, id) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIOC(id);
      setTimeout(() => setCopiedIOC(null), 2000);
    } catch (err) {
      console.error('Copy failed:', err);
    }
  };

  const copyAllIOCs = async () => {
    if (!threat?.iocs) return;
    const iocText = threat.iocs.map(ioc => `${ioc.type}: ${ioc.value}`).join('\n');
    await copyToClipboard(iocText, 'all');
  };

  const getClassificationStyle = (classification) => {
    const styles = {
      malicious: {
        bg: isDark ? 'bg-red-500/20' : 'bg-red-100',
        border: 'border-red-500/50',
        text: 'text-red-500',
        gradient: 'from-red-500/20 via-transparent to-transparent'
      },
      suspicious: {
        bg: isDark ? 'bg-amber-500/20' : 'bg-amber-100',
        border: 'border-amber-500/50',
        text: 'text-amber-500',
        gradient: 'from-amber-500/20 via-transparent to-transparent'
      },
      safe: {
        bg: isDark ? 'bg-emerald-500/20' : 'bg-emerald-100',
        border: 'border-emerald-500/50',
        text: 'text-emerald-500',
        gradient: 'from-emerald-500/20 via-transparent to-transparent'
      }
    };
    return styles[classification] || styles.suspicious;
  };

  const getIOCIcon = (type) => {
    const iconClass = "w-5 h-5";
    const icons = {
      domain: (
        <svg className={`${iconClass} text-blue-500`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
        </svg>
      ),
      url: (
        <svg className={`${iconClass} text-cyan-500`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      ),
      ip: (
        <svg className={`${iconClass} text-purple-500`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      sender_domain: (
        <svg className={`${iconClass} text-amber-500`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      email_pattern: (
        <svg className={`${iconClass} text-green-500`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
        </svg>
      )
    };
    return icons[type] || (
      <svg className={`${iconClass} text-slate-500`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
      </svg>
    );
  };

  const getTacticBadge = (tactic) => {
    const tactics = {
      authority: { label: 'Authority', color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
      urgency: { label: 'Urgency', color: 'bg-red-500/20 text-red-400 border-red-500/30' },
      fear: { label: 'Fear', color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
      greed: { label: 'Greed', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
      curiosity: { label: 'Curiosity', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
      trust: { label: 'Trust', color: 'bg-green-500/20 text-green-400 border-green-500/30' }
    };
    return tactics[tactic] || { label: tactic, color: 'bg-slate-500/20 text-slate-400 border-slate-500/30' };
  };

  const gridPattern = {
    backgroundImage: `
      linear-gradient(${colors.gridLine} 1px, transparent 1px),
      linear-gradient(90deg, ${colors.gridLine} 1px, transparent 1px)
    `,
    backgroundSize: '50px 50px'
  };

  if (loading) {
    return (
      <div className={`min-h-screen ${colors.bg} flex items-center justify-center`} style={gridPattern}>
        <div className="flex items-center gap-3">
          <svg className="animate-spin h-6 w-6 text-cyan-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className={`font-mono text-sm ${colors.text}`}>Loading threat data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen ${colors.bg} flex items-center justify-center`} style={gridPattern}>
        <div className={`p-8 rounded-xl ${colors.card} border ${colors.border} text-center max-w-md`}>
          <div className={`w-16 h-16 mx-auto mb-4 rounded-full ${isDark ? 'bg-red-500/20' : 'bg-red-100'} flex items-center justify-center`}>
            <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
          </div>
          <h2 className={`text-xl font-bold mb-2 ${colors.text}`}>{error}</h2>
          <p className={`${colors.textMuted} mb-4`}>The threat you're looking for doesn't exist or has been removed.</p>
          <Link
            to="/threats"
            className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back to Feed
          </Link>
        </div>
      </div>
    );
  }

  const classStyle = getClassificationStyle(threat?.classification);

  return (
    <div className={`min-h-screen ${colors.bg} ${colors.text}`} style={gridPattern}>
      {/* Header with gradient */}
      <div className={`relative bg-gradient-to-b ${classStyle.gradient}`}>
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Breadcrumb */}
          <Link
            to="/threats"
            className={`inline-flex items-center gap-2 ${colors.textMuted} hover:text-cyan-500 transition-colors mb-6`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Threat Feed
          </Link>

          {/* Main Header */}
          <div className="flex flex-col md:flex-row md:items-start gap-6">
            {/* Classification Badge */}
            <div className={`w-24 h-24 rounded-2xl ${classStyle.bg} border-2 ${classStyle.border} flex flex-col items-center justify-center`}>
              <div className={`text-3xl font-bold font-mono ${classStyle.text}`}>
                {Math.round(threat?.risk_score || 0)}
              </div>
              <div className={`text-xs font-mono ${classStyle.text} uppercase tracking-wider`}>
                Risk
              </div>
            </div>

            {/* Title & Meta */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <span className={`px-3 py-1 rounded-lg ${classStyle.bg} ${classStyle.text} border ${classStyle.border} font-mono text-sm font-bold uppercase`}>
                  {threat?.classification}
                </span>
                <span className={`px-3 py-1 rounded-lg ${isDark ? 'bg-slate-700' : 'bg-slate-200'} ${colors.textMuted} text-sm font-mono`}>
                  {threat?.threat_type?.replace(/_/g, ' ')}
                </span>
              </div>

              <h1 className="text-2xl font-bold mb-3">
                {threat?.sanitized_subject || 'No Subject'}
              </h1>

              <div className={`flex flex-wrap items-center gap-4 text-sm ${colors.textMuted}`}>
                <span className="font-mono">
                  ID: <span className="text-cyan-500">{threat?.short_id}</span>
                </span>
                <span>·</span>
                <span>
                  First seen: {new Date(threat?.first_seen).toLocaleDateString()}
                </span>
                <span>·</span>
                <span>
                  Views: {threat?.view_count?.toLocaleString()}
                </span>
                <span>·</span>
                <span>
                  Submitter: {threat?.submitter}
                </span>
              </div>

              {/* Brands */}
              {threat?.detected_brands?.length > 0 && (
                <div className="flex items-center gap-2 mt-3">
                  <span className={`text-sm ${colors.textMuted}`}>Impersonated:</span>
                  {threat.detected_brands.map(brand => (
                    <span
                      key={brand}
                      className={`px-2 py-1 rounded-md ${isDark ? 'bg-cyan-500/20' : 'bg-cyan-100'} text-cyan-500 text-sm font-medium capitalize`}
                    >
                      {brand}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid md:grid-cols-3 gap-6">
          {/* Main Column */}
          <div className="md:col-span-2 space-y-6">
            {/* IOCs Section */}
            <div className={`rounded-xl ${colors.card} border ${colors.border} overflow-hidden`}>
              <div className={`px-6 py-4 border-b ${colors.border} flex items-center justify-between`}>
                <h2 className="font-bold flex items-center gap-2">
                  <svg className="w-5 h-5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Indicators of Compromise
                </h2>
                {threat?.iocs?.length > 0 && user && (
                  <button
                    onClick={copyAllIOCs}
                    className={`px-3 py-1 rounded-lg ${isDark ? 'bg-[#0a0e17]' : 'bg-slate-100'} text-sm ${colors.textMuted} hover:text-cyan-500 transition-colors flex items-center gap-2`}
                  >
                    {copiedIOC === 'all' ? (
                      <>
                        <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                        Copied!
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        Copy All
                      </>
                    )}
                  </button>
                )}
              </div>

              <div className="p-6">
                {!user ? (
                  <div className="text-center py-8">
                    <div className={`w-16 h-16 mx-auto mb-3 rounded-full ${isDark ? 'bg-cyan-500/20' : 'bg-cyan-100'} flex items-center justify-center`}>
                      <svg className="w-8 h-8 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <p className={`${colors.textMuted} mb-4`}>
                      Login to view full IOC details
                    </p>
                    <Link
                      to="/login"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-colors"
                    >
                      Sign In to View
                    </Link>
                    <div className={`mt-6 p-4 rounded-lg ${isDark ? 'bg-[#0a0e17]' : 'bg-slate-100'}`}>
                      <p className={`text-sm ${colors.textMuted}`}>
                        <strong>{threat?.ioc_count}</strong> IOC{threat?.ioc_count !== 1 ? 's' : ''} available
                      </p>
                    </div>
                  </div>
                ) : threat?.iocs?.length > 0 ? (
                  <div className="space-y-3">
                    {threat.iocs.map((ioc, idx) => (
                      <div
                        key={idx}
                        className={`group p-4 rounded-lg ${isDark ? 'bg-[#0a0e17]' : 'bg-slate-50'} border ${colors.border} hover:border-cyan-500/50 transition-colors`}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              {getIOCIcon(ioc.type)}
                              <span className={`text-xs font-mono uppercase ${colors.textMuted}`}>
                                {ioc.type}
                              </span>
                              {ioc.context && (
                                <span className={`text-xs px-2 py-0.5 rounded ${isDark ? 'bg-slate-700' : 'bg-slate-200'} ${colors.textMuted}`}>
                                  {ioc.context}
                                </span>
                              )}
                            </div>
                            <code className={`block font-mono text-sm ${colors.text} break-all`}>
                              {ioc.value}
                            </code>
                            {ioc.occurrence_count > 1 && (
                              <p className={`text-xs ${colors.textMuted} mt-1`}>
                                Seen {ioc.occurrence_count} times globally
                              </p>
                            )}
                          </div>
                          <button
                            onClick={() => copyToClipboard(ioc.value, idx)}
                            className={`p-2 rounded-lg ${isDark ? 'bg-slate-700' : 'bg-slate-200'} opacity-0 group-hover:opacity-100 transition-opacity ${copiedIOC === idx ? 'text-green-500' : colors.textMuted} hover:text-cyan-500`}
                          >
                            {copiedIOC === idx ? (
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            ) : (
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                              </svg>
                            )}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className={`text-center py-8 ${colors.textMuted}`}>
                    No IOCs extracted from this threat
                  </p>
                )}
              </div>
            </div>

            {/* Tactics Section */}
            {threat?.detected_tactics?.length > 0 && user && (
              <div className={`rounded-xl ${colors.card} border ${colors.border} overflow-hidden`}>
                <div className={`px-6 py-4 border-b ${colors.border}`}>
                  <h2 className="font-bold flex items-center gap-2">
                    <svg className="w-5 h-5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Social Engineering Tactics
                  </h2>
                </div>
                <div className="p-6">
                  <div className="flex flex-wrap gap-2">
                    {threat.detected_tactics.map(tactic => {
                      const badge = getTacticBadge(tactic);
                      return (
                        <span
                          key={tactic}
                          className={`px-3 py-2 rounded-lg border ${badge.color} font-medium text-sm`}
                        >
                          {badge.label}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Community Voting */}
            <div className={`rounded-xl ${colors.card} border ${colors.border} overflow-hidden`}>
              <div className={`px-6 py-4 border-b ${colors.border}`}>
                <h2 className="font-bold flex items-center gap-2">
                  <svg className="w-5 h-5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  Community Verdict
                </h2>
              </div>
              <div className="p-6">
                <div className="flex items-center justify-center gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-500">
                      {threat?.community_votes?.phishing || 0}
                    </div>
                    <div className={`text-xs ${colors.textMuted}`}>Phishing</div>
                  </div>
                  <div className={`w-px h-10 ${colors.border}`}></div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-500">
                      {threat?.community_votes?.safe || 0}
                    </div>
                    <div className={`text-xs ${colors.textMuted}`}>Safe</div>
                  </div>
                </div>

                {user ? (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleVote('phishing')}
                      disabled={isVoting}
                      className={`flex-1 py-2 rounded-lg border transition-colors flex items-center justify-center gap-2 ${
                        userVote === 'phishing'
                          ? 'bg-red-500 text-white border-red-500'
                          : `${colors.border} hover:border-red-500 hover:text-red-500`
                      }`}
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      Phishing
                    </button>
                    <button
                      onClick={() => handleVote('safe')}
                      disabled={isVoting}
                      className={`flex-1 py-2 rounded-lg border transition-colors flex items-center justify-center gap-2 ${
                        userVote === 'safe'
                          ? 'bg-green-500 text-white border-green-500'
                          : `${colors.border} hover:border-green-500 hover:text-green-500`
                      }`}
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                      Safe
                    </button>
                  </div>
                ) : (
                  <p className={`text-center text-sm ${colors.textMuted}`}>
                    <Link to="/login" className="text-cyan-500 hover:underline">Login</Link> to vote
                  </p>
                )}
              </div>
            </div>

            {/* Threat Info */}
            <div className={`rounded-xl ${colors.card} border ${colors.border} overflow-hidden`}>
              <div className={`px-6 py-4 border-b ${colors.border}`}>
                <h2 className="font-bold flex items-center gap-2">
                  <svg className="w-5 h-5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Threat Info
                </h2>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <div className={`text-xs ${colors.textMuted} uppercase tracking-wider mb-1`}>First Seen</div>
                  <div className="font-mono text-sm">
                    {new Date(threat?.first_seen).toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className={`text-xs ${colors.textMuted} uppercase tracking-wider mb-1`}>Last Seen</div>
                  <div className="font-mono text-sm">
                    {new Date(threat?.last_seen).toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className={`text-xs ${colors.textMuted} uppercase tracking-wider mb-1`}>Similar Reports</div>
                  <div className="font-mono text-sm">
                    {threat?.similar_count || 1} submission{(threat?.similar_count || 1) !== 1 ? 's' : ''}
                  </div>
                </div>
                <div>
                  <div className={`text-xs ${colors.textMuted} uppercase tracking-wider mb-1`}>IOC Count</div>
                  <div className="font-mono text-sm">
                    {threat?.ioc_count || 0} indicator{(threat?.ioc_count || 0) !== 1 ? 's' : ''}
                  </div>
                </div>
              </div>
            </div>

            {/* Share */}
            <div className={`rounded-xl ${colors.card} border ${colors.border} p-6`}>
              <h2 className="font-bold mb-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Share Threat
              </h2>
              <div className={`p-3 rounded-lg ${isDark ? 'bg-[#0a0e17]' : 'bg-slate-100'} font-mono text-xs break-all ${colors.textMuted}`}>
                {window.location.href}
              </div>
              <button
                onClick={() => copyToClipboard(window.location.href, 'share')}
                className="w-full mt-3 py-2 rounded-lg border border-cyan-500 text-cyan-500 hover:bg-cyan-500 hover:text-white transition-colors text-sm font-medium flex items-center justify-center gap-2"
              >
                {copiedIOC === 'share' ? (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    Copied!
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy Link
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ThreatDetail;
