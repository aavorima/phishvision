import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../ThemeContext';
import { submitToThreatFeed } from '../api/api';

function SubmitToFeed({ analysisId, analysisResult, onClose, onSuccess }) {
  const { isDark } = useTheme();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const colors = {
    bg: isDark ? 'bg-[#0a0e17]' : 'bg-white',
    card: isDark ? 'bg-[#111827]' : 'bg-slate-50',
    border: isDark ? 'border-[#1e293b]' : 'border-slate-200',
    text: isDark ? 'text-slate-100' : 'text-slate-900',
    textMuted: isDark ? 'text-slate-400' : 'text-slate-500'
  };

  const getClassificationColor = (classification) => {
    const colors = {
      malicious: 'text-red-500 bg-red-500/10 border-red-500/30',
      suspicious: 'text-amber-500 bg-amber-500/10 border-amber-500/30',
      safe: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30'
    };
    return colors[classification] || colors.suspicious;
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await submitToThreatFeed({
        analysis_id: analysisId,
        anonymous: isAnonymous
      });

      setResult(response.data);
      setSubmitted(true);

      if (onSuccess) {
        onSuccess(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit to threat feed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className={`relative w-full max-w-lg rounded-2xl ${colors.bg} border ${colors.border} shadow-2xl overflow-hidden`}>
        {/* Header */}
        <div className={`px-6 py-4 border-b ${colors.border} flex items-center justify-between`}>
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl ${isDark ? 'bg-cyan-500/20' : 'bg-cyan-100'} flex items-center justify-center`}>
              <svg className="w-5 h-5 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h2 className={`font-bold ${colors.text}`}>Share to Threat Feed</h2>
              <p className={`text-sm ${colors.textMuted}`}>Contribute to community intelligence</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg ${isDark ? 'hover:bg-white/10' : 'hover:bg-black/5'} transition-colors`}
          >
            <svg className={`w-5 h-5 ${colors.textMuted}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {submitted ? (
            // Success State
            <div className="text-center py-4">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <svg className="w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className={`text-xl font-bold mb-2 ${colors.text}`}>
                {result?.is_duplicate ? 'Similar Threat Found!' : 'Successfully Submitted!'}
              </h3>
              <p className={`${colors.textMuted} mb-4`}>
                {result?.is_duplicate
                  ? 'This threat was already in our database. We updated the submission count.'
                  : 'Your analysis has been added to the community threat feed.'
                }
              </p>

              {result?.short_id && (
                <Link
                  to={`/threats/${result.short_id}`}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 transition-colors"
                >
                  View Threat Entry
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </Link>
              )}
            </div>
          ) : (
            // Form State
            <>
              {/* Analysis Preview */}
              <div className={`p-4 rounded-xl ${colors.card} border ${colors.border} mb-4`}>
                <div className="flex items-start justify-between mb-3">
                  <span className={`px-3 py-1 rounded-lg border text-sm font-bold uppercase ${getClassificationColor(analysisResult?.classification)}`}>
                    {analysisResult?.classification}
                  </span>
                  <span className={`font-mono text-lg font-bold ${
                    analysisResult?.risk_score >= 70 ? 'text-red-500' :
                    analysisResult?.risk_score >= 40 ? 'text-amber-500' : 'text-emerald-500'
                  }`}>
                    {Math.round(analysisResult?.risk_score || 0)}
                  </span>
                </div>
                <p className={`text-sm ${colors.text} line-clamp-2`}>
                  {analysisResult?.email_subject || 'No Subject'}
                </p>
                <p className={`text-xs ${colors.textMuted} mt-1`}>
                  From: {analysisResult?.email_from}
                </p>
              </div>

              {/* What Gets Shared */}
              <div className={`p-4 rounded-xl ${isDark ? 'bg-cyan-500/10' : 'bg-cyan-50'} border ${isDark ? 'border-cyan-500/30' : 'border-cyan-200'} mb-4`}>
                <h4 className="font-medium text-cyan-500 mb-2 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  What Gets Shared
                </h4>
                <ul className={`text-sm ${colors.textMuted} space-y-1`}>
                  <li>Extracted IOCs (domains, URLs, IPs)</li>
                  <li>Sanitized subject (personal info removed)</li>
                  <li>Classification and risk score</li>
                  <li>Detected tactics and brands</li>
                </ul>
                <p className={`text-xs ${colors.textMuted} mt-2 pt-2 border-t ${isDark ? 'border-cyan-500/20' : 'border-cyan-200'}`}>
                  Full email content and personal information are NOT shared.
                </p>
              </div>

              {/* Anonymous Toggle */}
              <div className={`p-4 rounded-xl ${colors.card} border ${colors.border} mb-4`}>
                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className={`font-medium ${colors.text}`}>Submit Anonymously</p>
                    <p className={`text-sm ${colors.textMuted}`}>
                      {isAnonymous ? 'Your username will NOT appear' : 'Your username will appear as submitter'}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setIsAnonymous(!isAnonymous)}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      isAnonymous ? 'bg-cyan-500' : isDark ? 'bg-slate-700' : 'bg-slate-300'
                    }`}
                  >
                    <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                      isAnonymous ? 'translate-x-7' : 'translate-x-1'
                    }`} />
                  </button>
                </label>
              </div>

              {/* Error Message */}
              {error && (
                <div className={`p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-500 text-sm mb-4`}>
                  {error}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={onClose}
                  className={`flex-1 py-3 rounded-xl border ${colors.border} ${colors.text} font-medium hover:bg-black/5 dark:hover:bg-white/5 transition-colors`}
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="flex-1 py-3 rounded-xl bg-cyan-500 text-white font-medium hover:bg-cyan-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Submitting...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      Share to Feed
                    </>
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default SubmitToFeed;
