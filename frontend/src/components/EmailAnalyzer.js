import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import { analyzeEmail, getAnalysisHistory, clearAnalysisHistory } from '../api/api';
import ConfirmDialog from './ConfirmDialog';
import SubmitToFeed from './SubmitToFeed';
import { parseEmail, validateParsedEmail, formatPreview } from '../utils/emailParser';

function EmailAnalyzer() {
  const { isDark } = useTheme();
  const [rawEmail, setRawEmail] = useState('');
  const [parsedData, setParsedData] = useState(null);
  const [formData, setFormData] = useState({
    email_from: '',
    email_subject: '',
    email_body: '',
    headers: ''
  });
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [showClearDialog, setShowClearDialog] = useState(false);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [showErrorDialog, setShowErrorDialog] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [parseError, setParseError] = useState('');
  const [showSubmitToFeed, setShowSubmitToFeed] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await getAnalysisHistory(10);
      setHistory(response.data);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const handleClearHistory = async () => {
    try {
      await clearAnalysisHistory();
      setHistory([]);
      setResult(null);
      setShowClearDialog(false);
      setShowSuccessDialog(true);
    } catch (error) {
      console.error('Error clearing history:', error);
      setShowClearDialog(false);
      setErrorMessage('Failed to clear history. Please try again.');
      setShowErrorDialog(true);
    }
  };

  const handleEmailPaste = (e) => {
    const pastedText = e.target.value;
    setRawEmail(pastedText);
    setParseError('');

    if (pastedText.trim().length > 10) {
      // Auto-parse the email
      const parsed = parseEmail(pastedText);
      setParsedData(parsed);

      if (!parsed.success) {
        setParseError(parsed.error || 'Could not parse email');
      } else {
        // Validate parsed data
        const validation = validateParsedEmail(parsed);
        if (!validation.isValid) {
          setParseError('Parsing issues: ' + validation.errors.join(', '));
        }
      }

      // Update form data
      setFormData({
        email_from: parsed.email_from,
        email_subject: parsed.email_subject,
        email_body: parsed.email_body,
        headers: parsed.headers
      });
    } else {
      setParsedData(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Final validation before submission
    if (!formData.email_from || !formData.email_subject || !formData.email_body) {
      setErrorMessage('Please paste a complete email with From, Subject, and Body');
      setShowErrorDialog(true);
      return;
    }

    try {
      setAnalyzing(true);
      const response = await analyzeEmail(formData);
      setResult(response.data);
      loadHistory();
    } catch (error) {
      console.error('Error analyzing email:', error);
      setErrorMessage('Error analyzing email. Please try again.');
      setShowErrorDialog(true);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleClear = () => {
    setRawEmail('');
    setParsedData(null);
    setFormData({
      email_from: '',
      email_subject: '',
      email_body: '',
      headers: ''
    });
    setParseError('');
    setResult(null);
  };

  const getRiskColor = (classification) => {
    const colors = {
      safe: 'bg-green-500',
      suspicious: 'bg-yellow-500',
      malicious: 'bg-red-500'
    };
    return colors[classification] || colors.safe;
  };

  const getRiskBadgeColor = (classification) => {
    const colors = {
      safe: 'bg-green-500/20 text-green-400 border-green-500/30',
      suspicious: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      malicious: 'bg-red-500/20 text-red-400 border-red-500/30'
    };
    return colors[classification] || colors.safe;
  };

  const getAuthBadge = (status) => {
    if (status === 'pass') return (
      <span className="px-3 py-1 bg-green-900/30 text-green-400 rounded-full text-xs font-bold border border-green-800 inline-flex items-center gap-1">
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        PASS
      </span>
    );
    if (status === 'fail') return (
      <span className="px-3 py-1 bg-red-900/30 text-red-400 rounded-full text-xs font-bold border border-red-800 inline-flex items-center gap-1">
        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
        FAIL
      </span>
    );
    return <span className={`px-3 py-1 rounded-full text-xs font-bold border ${isDark ? 'bg-slate-700 text-slate-400 border-slate-600' : 'bg-slate-200 text-slate-600 border-slate-300'}`}>— NONE</span>;
  };

  const bgPrimary = isDark ? 'bg-slate-900' : 'bg-slate-50';
  const bgSecondary = isDark ? 'bg-slate-800' : 'bg-white';
  const bgTertiary = isDark ? 'bg-slate-700' : 'bg-slate-100';
  const borderColor = isDark ? 'border-slate-700' : 'border-slate-200';
  const borderColorDark = isDark ? 'border-slate-600' : 'border-slate-300';
  const textPrimary = isDark ? 'text-slate-50' : 'text-slate-900';
  const textSecondary = isDark ? 'text-slate-400' : 'text-slate-600';
  const textTertiary = isDark ? 'text-slate-500' : 'text-slate-500';
  const inputBg = isDark ? 'bg-slate-700' : 'bg-white';
  const inputBorder = isDark ? 'border-slate-600' : 'border-slate-300';
  const placeholderColor = isDark ? 'placeholder-slate-400' : 'placeholder-slate-500';

  return (
    <div className={`min-h-screen ${bgPrimary} p-6`}>
      {/* Header */}
      <div className="mb-8">
        <div className={`${bgSecondary} border ${borderColor} rounded-xl shadow-xl p-8`}>
          <div className="flex items-center justify-between">
            <div>
              <h1 className={`text-4xl font-bold ${textPrimary} mb-2`}>
                Email Threat Analyzer
              </h1>
              <p className={`${textSecondary} text-lg`}>AI-Powered Phishing Detection</p>
            </div>
            <div className="text-right">
              <div className={`text-sm ${textSecondary}`}>Analysis Engine</div>
              <div className={`text-lg font-semibold ${textPrimary}`}>PhishVision AI</div>
              <div className="mt-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/30">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  ACTIVE
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Analysis Form */}
        <div className="lg:col-span-2 space-y-6">
          <div className={`${bgSecondary} border ${borderColor} rounded-lg shadow-sm p-6`}>
            <div className="flex justify-between items-center mb-4">
              <h2 className={`text-lg font-semibold ${textPrimary}`}>
                Paste Email to Analyze
              </h2>
              {rawEmail && (
                <button
                  onClick={handleClear}
                  className={`text-xs px-3 py-1 rounded transition ${isDark ? 'bg-slate-700 text-slate-300 hover:bg-slate-600' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
                >
                  Clear
                </button>
              )}
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className={`block text-sm font-bold ${textPrimary} mb-2`}>
                  PASTE FULL EMAIL HERE
                </label>
                <p className={`text-xs ${textSecondary} mb-3`}>
                  Paste the complete email (with headers, subject, and body). Supports raw emails, forwarded emails, or Gmail/Outlook copy-paste.
                </p>
                <textarea
                  required
                  value={rawEmail}
                  onChange={handleEmailPaste}
                  className={`w-full px-4 py-3 ${inputBg} border ${inputBorder} rounded-lg ${textPrimary} ${placeholderColor} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm`}
                  rows="12"
                  placeholder={`Paste email here... Example:

From: sender@example.com
Subject: Urgent: Account Verification Required
Date: Mon, 29 Nov 2024 10:30:00 +0000

Dear User,

We have detected unusual activity...`}
                />
              </div>

              {/* Parse Error */}
              {parseError && (
                <div className={`${isDark ? 'bg-yellow-900/30 border-yellow-800' : 'bg-yellow-50 border-yellow-200'} border rounded-lg p-4`}>
                  <div className="flex items-start">
                    <svg className="w-5 h-5 text-yellow-500 mr-2 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div>
                      <p className={`font-medium text-sm ${isDark ? 'text-yellow-400' : 'text-yellow-700'}`}>
                        Parsing Warning
                      </p>
                      <p className={`text-xs mt-1 ${isDark ? 'text-yellow-300' : 'text-yellow-600'}`}>
                        {parseError}. You can still try analyzing.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Parsed Data Preview */}
              {parsedData && parsedData.success && (
                <div className={`${isDark ? 'bg-blue-900/30 border-blue-800' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
                  <h3 className={`font-bold text-sm ${isDark ? 'text-blue-400' : 'text-blue-700'} mb-3 flex items-center`}>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Extracted Email Data
                  </h3>
                  <div className="space-y-2">
                    <div>
                      <span className={`text-xs font-semibold ${isDark ? 'text-blue-300' : 'text-blue-600'}`}>From:</span>
                      <p className={`text-sm ${isDark ? 'text-blue-200' : 'text-blue-800'} truncate`}>
                        {parsedData.email_from || '(not detected)'}
                      </p>
                    </div>
                    <div>
                      <span className={`text-xs font-semibold ${isDark ? 'text-blue-300' : 'text-blue-600'}`}>Subject:</span>
                      <p className={`text-sm ${isDark ? 'text-blue-200' : 'text-blue-800'}`}>
                        {formatPreview(parsedData.email_subject, 80)}
                      </p>
                    </div>
                    <div>
                      <span className={`text-xs font-semibold ${isDark ? 'text-blue-300' : 'text-blue-600'}`}>Body Preview:</span>
                      <p className={`text-sm ${isDark ? 'text-blue-200' : 'text-blue-800'}`}>
                        {formatPreview(parsedData.email_body, 120)}
                      </p>
                    </div>
                    {parsedData.headers && (
                      <div>
                        <span className={`text-xs font-semibold ${isDark ? 'text-blue-300' : 'text-blue-600'}`}>Headers:</span>
                        <p className={`text-xs ${isDark ? 'text-blue-200' : 'text-blue-800'}`}>
                          {parsedData.headers.split('\n').length} header lines detected
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={analyzing || !rawEmail || !parsedData}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-4 rounded-lg font-bold text-lg transition shadow-lg"
              >
                {analyzing ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing...
                  </span>
                ) : 'Analyze Email'}
              </button>
            </form>
          </div>

          {/* Analysis Result */}
          {result && (
            <div className={`${bgSecondary} border ${borderColor} rounded-lg shadow-sm p-6`}>
              <h2 className={`text-lg font-semibold ${textPrimary} mb-4`}>
                Analysis Report
              </h2>

              {/* Risk Classification */}
              <div className={`${getRiskColor(result.classification)} rounded-xl p-6 mb-6 text-white shadow-lg`}>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-sm font-bold uppercase opacity-90">CLASSIFICATION</div>
                    <div className="text-4xl font-bold capitalize mt-2">{result.classification}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold uppercase opacity-90">RISK SCORE</div>
                    <div className="text-6xl font-bold">{result.risk_score}</div>
                    <div className="text-sm opacity-90">/ 100</div>
                  </div>
                </div>
              </div>

              {/* Email Authentication */}
              <div className={`${isDark ? 'bg-slate-700/50 border-slate-600' : 'bg-slate-100 border-slate-300'} rounded-xl p-6 mb-6 border`}>
                <h3 className={`font-bold ${textPrimary} mb-4 text-lg`}>
                  Email Authentication
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className={`text-sm ${textSecondary} mb-2`}>SPF</div>
                    {getAuthBadge(result.spf_status)}
                  </div>
                  <div className="text-center">
                    <div className={`text-sm ${textSecondary} mb-2`}>DKIM</div>
                    {getAuthBadge(result.dkim_status)}
                  </div>
                  <div className="text-center">
                    <div className={`text-sm ${textSecondary} mb-2`}>DMARC</div>
                    {getAuthBadge(result.dmarc_status)}
                  </div>
                </div>
              </div>

              {/* Explanation */}
              <div className={`${isDark ? 'bg-slate-700/50 border-slate-600' : 'bg-slate-100 border-slate-300'} rounded-lg p-4 mb-4 border`}>
                <h3 className={`font-medium ${textPrimary} mb-2 text-sm`}>
                  Explanation
                </h3>
                <p className={`${isDark ? 'text-slate-300' : 'text-slate-700'} leading-relaxed whitespace-pre-line text-sm`}>{result.explanation}</p>
              </div>

              {/* Recommendations */}
              <div className={`${isDark ? 'bg-slate-700/50 border-slate-600' : 'bg-slate-100 border-slate-300'} rounded-lg p-4 border`}>
                <h3 className={`font-medium ${textPrimary} mb-3 text-sm`}>
                  Recommendations
                </h3>
                <ul className="space-y-2">
                  {JSON.parse(result.recommendations).map((rec, index) => (
                    <li key={index} className={`flex items-start ${isDark ? 'text-slate-300' : 'text-slate-700'} text-sm`}>
                      <svg className="w-4 h-4 text-blue-400 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <circle cx="10" cy="10" r="3" />
                      </svg>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Share to Threat Feed */}
              {result.classification !== 'safe' && (
                <div className={`${isDark ? 'bg-cyan-500/10 border-cyan-500/30' : 'bg-cyan-50 border-cyan-200'} rounded-lg p-4 border mt-4`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg ${isDark ? 'bg-cyan-500/20' : 'bg-cyan-100'} flex items-center justify-center`}>
                        <svg className="w-5 h-5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                      </div>
                      <div>
                        <p className={`font-medium ${textPrimary} text-sm`}>Help the community</p>
                        <p className={`text-xs ${textSecondary}`}>Share this threat to the public intelligence feed</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowSubmitToFeed(true)}
                      className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-medium text-sm transition-colors flex items-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      Share to Feed
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* History Sidebar */}
        <div className="lg:col-span-1">
          <div className={`${bgSecondary} border ${borderColor} rounded-xl shadow-xl p-6 sticky top-6`}>
            <div className="flex items-center justify-between mb-6">
              <h2 className={`text-xl font-bold ${textPrimary}`}>
                Recent Analyses
              </h2>
              {history.length > 0 && (
                <button
                  onClick={() => setShowClearDialog(true)}
                  className={`text-xs px-2 py-1 rounded transition ${isDark ? 'bg-red-900/30 text-red-400 hover:bg-red-900/50' : 'bg-red-100 text-red-600 hover:bg-red-200'}`}
                  title="Clear all history"
                >
                  Clear
                </button>
              )}
            </div>

            <div className="space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
              {history.length > 0 ? (
                history.map((item) => (
                  <div
                    key={item.id}
                    className={`${isDark ? 'bg-slate-700/50 border-slate-600 hover:bg-slate-700' : 'bg-slate-100 border-slate-300 hover:bg-slate-200'} border rounded-lg p-4 transition-all duration-200 cursor-pointer`}
                    onClick={() => setResult(item)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getRiskBadgeColor(item.classification)}`}>
                        {item.classification.toUpperCase()}
                      </span>
                      <span className={`text-2xl font-bold ${textPrimary}`}>
                        {item.risk_score}
                      </span>
                    </div>
                    <div className={`text-sm font-medium ${textPrimary} truncate mb-1`}>
                      {item.email_subject}
                    </div>
                    <div className={`text-xs ${textSecondary} truncate mb-2`}>{item.email_from}</div>
                    <div className={`text-xs ${textTertiary}`}>
                      {new Date(item.analyzed_at).toLocaleString()}
                    </div>
                  </div>
                ))
              ) : (
                <div className={`flex flex-col items-center justify-center py-12 ${textTertiary}`}>
                  <svg className="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="text-sm text-center">No analysis history yet</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: ${isDark ? 'rgba(51, 65, 85, 0.3)' : 'rgba(241, 245, 249, 0.5)'};
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: ${isDark ? 'rgba(59, 130, 246, 0.5)' : 'rgba(59, 130, 246, 0.4)'};
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: ${isDark ? 'rgba(59, 130, 246, 0.8)' : 'rgba(59, 130, 246, 0.6)'};
        }
      `}</style>

      {/* Confirmation Dialogs */}
      <ConfirmDialog
        isOpen={showClearDialog}
        title="Clear Analysis History"
        message="Are you sure you want to clear all analysis history? This action cannot be undone."
        onConfirm={handleClearHistory}
        onCancel={() => setShowClearDialog(false)}
        confirmText="Clear History"
        cancelText="Cancel"
        type="danger"
      />

      <ConfirmDialog
        isOpen={showSuccessDialog}
        title="Success"
        message="Analysis history cleared successfully."
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

      {/* Submit to Threat Feed Modal */}
      {showSubmitToFeed && result && (
        <SubmitToFeed
          analysisId={result.id}
          analysisResult={result}
          onClose={() => setShowSubmitToFeed(false)}
          onSuccess={() => {
            // Optionally refresh or show success
          }}
        />
      )}
    </div>
  );
}

export default EmailAnalyzer;
