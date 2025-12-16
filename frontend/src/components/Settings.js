import React, { useState, useEffect } from 'react';
import { useTheme } from '../ThemeContext';
import { useAuth } from '../AuthContext';
import { getSettings, updateSettings, testSmtpConnection, sendTestEmail, updateProfile, changePassword, testGeminiConnection } from '../api/api';

function Settings() {
  const { isDark } = useTheme();
  const { user, updateUser } = useAuth();

  const [activeTab, setActiveTab] = useState('smtp');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [smtpStatus, setSmtpStatus] = useState(null);

  // Profile form
  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    email: ''
  });

  // Password form
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // SMTP Settings form
  const [smtpForm, setSmtpForm] = useState({
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_use_tls: true,
    smtp_from_email: '',
    smtp_from_name: ''
  });

  const [testEmail, setTestEmail] = useState('');

  // AI Settings form
  const [aiForm, setAiForm] = useState({
    gemini_api_key: '',
    twilio_account_sid: '',
    twilio_auth_token: '',
    twilio_phone_number: ''
  });
  const [aiStatus, setAiStatus] = useState(null);
  const [twilioStatus, setTwilioStatus] = useState(null);

  useEffect(() => {
    if (user) {
      setProfileForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || ''
      });
      setTestEmail(user.email || '');
    }
    loadSettings();
    checkSmtpStatus();
  }, [user]);

  const loadSettings = async () => {
    try {
      const response = await getSettings();
      const settings = response.data;
      setSmtpForm({
        smtp_host: settings.smtp_host || '',
        smtp_port: settings.smtp_port || 587,
        smtp_username: settings.smtp_username || '',
        smtp_password: settings.smtp_password || '',
        smtp_use_tls: settings.smtp_use_tls !== false,
        smtp_from_email: settings.smtp_from_email || '',
        smtp_from_name: settings.smtp_from_name || ''
      });
      setAiForm({
        gemini_api_key: settings.gemini_api_key || '',
        twilio_account_sid: settings.twilio_account_sid || '',
        twilio_auth_token: settings.twilio_auth_token || '',
        twilio_phone_number: settings.twilio_phone_number || ''
      });
      setAiStatus({
        configured: settings.gemini_api_key_set || false
      });
      setTwilioStatus({
        configured: settings.twilio_configured || false
      });
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const checkSmtpStatus = async () => {
    try {
      // Use getSettings to check if SMTP is configured (more reliable than smtp-status)
      const response = await getSettings();
      const settings = response.data;
      // Password shows as '********' when set, null when not set
      const hasPassword = settings.smtp_password && settings.smtp_password !== '';
      const isConfigured = !!(settings.smtp_host && settings.smtp_username && hasPassword);
      setSmtpStatus({
        configured: isConfigured,
        config: {
          host: settings.smtp_host,
          port: settings.smtp_port
        }
      });
    } catch (error) {
      console.error('Failed to check SMTP status:', error);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await updateProfile(profileForm);
      updateUser(response.data.user);
      showMessage('success', 'Profile updated successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      showMessage('error', 'Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password
      });
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
      showMessage('success', 'Password changed successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.error || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleSmtpSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updateSettings(smtpForm);
      showMessage('success', 'SMTP settings saved successfully');
      checkSmtpStatus();
    } catch (error) {
      showMessage('error', error.response?.data?.error || 'Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    setLoading(true);
    try {
      await testSmtpConnection();
      showMessage('success', 'SMTP connection successful!');
    } catch (error) {
      showMessage('error', error.response?.data?.error || 'Connection failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSendTestEmail = async () => {
    if (!testEmail) {
      showMessage('error', 'Please enter a test email address');
      return;
    }
    setLoading(true);
    try {
      await sendTestEmail({ email: testEmail });
      showMessage('success', `Test email sent to ${testEmail}`);
    } catch (error) {
      showMessage('error', error.response?.data?.error || 'Failed to send test email');
    } finally {
      setLoading(false);
    }
  };

  const handleAiSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updateSettings(aiForm);
      showMessage('success', 'AI settings saved successfully');
      loadSettings(); // Reload to get updated status
    } catch (error) {
      showMessage('error', error.response?.data?.error || 'Failed to save AI settings');
    } finally {
      setLoading(false);
    }
  };

  const handleTestGemini = async () => {
    const key = aiForm.gemini_api_key?.trim();
    if (!key) {
      showMessage('error', 'Please enter an API key first');
      return;
    }
    setLoading(true);
    try {
      // Send key (or '********' which tells backend to use saved key)
      const response = await testGeminiConnection({ api_key: key });
      showMessage('success', `Gemini API connected! Response: ${response.data.test_response}`);
    } catch (error) {
      const errMsg = error.response?.data?.error || error.message || 'Gemini API test failed';
      showMessage('error', errMsg);
    } finally {
      setLoading(false);
    }
  };

  const inputClass = `w-full px-4 py-3 rounded-xl border transition-all duration-200 outline-none ${
    isDark
      ? 'bg-surface-3 border-white/10 text-white placeholder-white/30 focus:border-primary focus:ring-2 focus:ring-primary/20'
      : 'bg-white border-black/10 text-surface-1 placeholder-surface-1/30 focus:border-primary focus:ring-2 focus:ring-primary/20'
  }`;

  const tabs = [
    { id: 'smtp', label: 'SMTP Settings', icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
    { id: 'ai', label: 'AI Settings', icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
    { id: 'profile', label: 'Profile', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
    { id: 'security', label: 'Security', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' }
  ];

  return (
    <div className={`min-h-screen p-6 ${isDark ? 'bg-surface-1' : 'bg-surface-light-1'}`}>
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className={`absolute top-0 right-0 w-[600px] h-[600px] rounded-full blur-3xl ${isDark ? 'bg-primary/3' : 'bg-primary/5'}`} />
        <div className={`absolute bottom-0 left-0 w-[400px] h-[400px] rounded-full blur-3xl ${isDark ? 'bg-accent/3' : 'bg-accent/5'}`} />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className={`text-3xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-1'}`}>
            Settings
          </h1>
          <p className={`mt-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
            Configure your account and email settings
          </p>
        </div>

        {/* Message */}
        {message.text && (
          <div className={`mb-6 p-4 rounded-xl flex items-center ${
            message.type === 'success'
              ? 'bg-success/10 border border-success/20 text-success'
              : 'bg-danger/10 border border-danger/20 text-danger'
          }`}>
            <svg className="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {message.type === 'success' ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              )}
            </svg>
            {message.text}
          </div>
        )}

        <div className="flex gap-6">
          {/* Sidebar Tabs */}
          <div className={`w-56 rounded-2xl p-3 border flex-shrink-0 ${isDark ? 'bg-surface-2 border-white/5' : 'bg-white border-black/5'}`}>
            <div className="space-y-1">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-primary text-surface-1'
                      : isDark
                        ? 'text-white/60 hover:text-white hover:bg-white/5'
                        : 'text-surface-1/60 hover:text-surface-1 hover:bg-black/5'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={tab.icon} />
                  </svg>
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className={`flex-1 rounded-2xl border overflow-hidden ${isDark ? 'bg-surface-2 border-white/5' : 'bg-white border-black/5'}`}>
            {/* SMTP Settings Tab */}
            {activeTab === 'smtp' && (
              <div>
                {/* SMTP Status Banner */}
                <div className={`p-4 border-b ${isDark ? 'border-white/5' : 'border-black/5'} ${
                  smtpStatus?.configured
                    ? 'bg-success/10'
                    : 'bg-warning/10'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${smtpStatus?.configured ? 'bg-success' : 'bg-warning'}`}>
                        <div className={`w-3 h-3 rounded-full animate-ping ${smtpStatus?.configured ? 'bg-success' : 'bg-warning'}`} />
                      </div>
                      <span className={`font-medium ${smtpStatus?.configured ? 'text-success' : 'text-warning'}`}>
                        {smtpStatus?.configured ? 'SMTP Configured' : 'SMTP Not Configured'}
                      </span>
                    </div>
                    {smtpStatus?.config && (
                      <span className={`text-sm ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                        {smtpStatus.config.host ? `${smtpStatus.config.host}:${smtpStatus.config.port}` : 'No host configured'}
                      </span>
                    )}
                  </div>
                  {!smtpStatus?.configured && (
                    <p className={`text-sm mt-2 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                      Configure your SMTP settings below to send phishing simulation emails.
                    </p>
                  )}
                </div>

                <div className="p-6 space-y-6">
                  <div>
                    <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      SMTP Mail Server Configuration
                    </h2>
                    <p className={`text-sm mt-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                      Configure your SMTP server to send phishing simulation emails.
                    </p>
                  </div>

                  <form onSubmit={handleSmtpSubmit} className="space-y-5">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          SMTP Host
                        </label>
                        <input
                          type="text"
                          value={smtpForm.smtp_host}
                          onChange={(e) => setSmtpForm({ ...smtpForm, smtp_host: e.target.value })}
                          placeholder="smtp.gmail.com"
                          className={inputClass}
                        />
                      </div>
                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          SMTP Port
                        </label>
                        <input
                          type="number"
                          value={smtpForm.smtp_port}
                          onChange={(e) => setSmtpForm({ ...smtpForm, smtp_port: parseInt(e.target.value) })}
                          placeholder="587"
                          className={inputClass}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          Username
                        </label>
                        <input
                          type="text"
                          value={smtpForm.smtp_username}
                          onChange={(e) => setSmtpForm({ ...smtpForm, smtp_username: e.target.value })}
                          placeholder="your@email.com"
                          className={inputClass}
                        />
                      </div>
                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          Password
                        </label>
                        <input
                          type="password"
                          value={smtpForm.smtp_password}
                          onChange={(e) => setSmtpForm({ ...smtpForm, smtp_password: e.target.value })}
                          placeholder="App password or SMTP password"
                          className={inputClass}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          From Email
                        </label>
                        <input
                          type="email"
                          value={smtpForm.smtp_from_email}
                          onChange={(e) => setSmtpForm({ ...smtpForm, smtp_from_email: e.target.value })}
                          placeholder="noreply@yourdomain.com"
                          className={inputClass}
                        />
                      </div>
                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          From Name
                        </label>
                        <input
                          type="text"
                          value={smtpForm.smtp_from_name}
                          onChange={(e) => setSmtpForm({ ...smtpForm, smtp_from_name: e.target.value })}
                          placeholder="IT Support"
                          className={inputClass}
                        />
                      </div>
                    </div>

                    <div className={`flex items-center p-4 rounded-xl ${isDark ? 'bg-surface-3/50' : 'bg-surface-light-3'}`}>
                      <input
                        type="checkbox"
                        id="use_tls"
                        checked={smtpForm.smtp_use_tls}
                        onChange={(e) => setSmtpForm({ ...smtpForm, smtp_use_tls: e.target.checked })}
                        className="w-5 h-5 text-primary rounded border-white/20 focus:ring-primary"
                      />
                      <label htmlFor="use_tls" className={`ml-3 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                        <span className="font-medium">Use TLS/STARTTLS</span>
                        <span className={`block text-sm ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                          Enable for port 587. Disable for SSL on port 465.
                        </span>
                      </label>
                    </div>

                    <div className="flex gap-3">
                      <button
                        type="submit"
                        disabled={loading}
                        className="group relative px-6 py-3 rounded-xl font-semibold text-surface-1 overflow-hidden transition-all duration-300 disabled:opacity-50 hover:scale-[1.02]"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
                        <span className="relative">
                          {loading ? 'Saving...' : 'Save Settings'}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={handleTestConnection}
                        disabled={loading}
                        className={`px-6 py-3 rounded-xl font-semibold transition-all duration-200 hover:scale-[1.02] ${
                          isDark
                            ? 'bg-surface-3 text-white border border-white/10 hover:bg-surface-4'
                            : 'bg-surface-light-3 text-surface-1 border border-black/10 hover:bg-surface-light-4'
                        }`}
                      >
                        Test Connection
                      </button>
                    </div>
                  </form>

                  {/* Test Email Section */}
                  <div className={`pt-6 border-t ${isDark ? 'border-white/5' : 'border-black/5'}`}>
                    <h3 className={`text-md font-semibold ${isDark ? 'text-white' : 'text-surface-1'} mb-4`}>
                      Send Test Email
                    </h3>
                    <div className="flex gap-3">
                      <input
                        type="email"
                        value={testEmail}
                        onChange={(e) => setTestEmail(e.target.value)}
                        placeholder="recipient@example.com"
                        className={`flex-1 ${inputClass}`}
                      />
                      <button
                        onClick={handleSendTestEmail}
                        disabled={loading}
                        className="group relative px-6 py-3 rounded-xl font-semibold text-white overflow-hidden transition-all duration-300 disabled:opacity-50 hover:scale-[1.02]"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-success to-success-dim" />
                        <span className="relative">Send Test</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* AI Settings Tab */}
            {activeTab === 'ai' && (
              <div>
                {/* AI Status Banner */}
                <div className={`p-4 border-b ${isDark ? 'border-white/5' : 'border-black/5'} ${
                  aiStatus?.configured
                    ? 'bg-success/10'
                    : 'bg-warning/10'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${aiStatus?.configured ? 'bg-success' : 'bg-warning'}`}>
                        <div className={`w-3 h-3 rounded-full animate-ping ${aiStatus?.configured ? 'bg-success' : 'bg-warning'}`} />
                      </div>
                      <span className={`font-medium ${aiStatus?.configured ? 'text-success' : 'text-warning'}`}>
                        {aiStatus?.configured ? 'Gemini AI Configured' : 'Gemini AI Not Configured'}
                      </span>
                    </div>
                  </div>
                  {!aiStatus?.configured && (
                    <p className={`text-sm mt-2 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                      Configure your Gemini API key to enable AI-powered template generation.
                    </p>
                  )}
                </div>

                <div className="p-6 space-y-6">
                  <div>
                    <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      Google Gemini AI Configuration
                    </h2>
                    <p className={`text-sm mt-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                      Configure your Gemini API key for AI-powered phishing template generation.
                    </p>
                  </div>

                  <form onSubmit={handleAiSubmit} className="space-y-5">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                        Gemini API Key
                      </label>
                      <input
                        type="text"
                        value={aiForm.gemini_api_key}
                        onChange={(e) => setAiForm({ ...aiForm, gemini_api_key: e.target.value })}
                        placeholder="AIzaSy..."
                        className={`${inputClass} font-mono text-sm`}
                      />
                      <p className={`text-xs mt-2 ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>
                        Get your API key from <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google AI Studio</a>
                      </p>
                    </div>

                    <div className={`p-4 rounded-xl ${isDark ? 'bg-surface-3/50' : 'bg-surface-light-3'}`}>
                      <div className="flex items-start">
                        <svg className={`w-5 h-5 mr-3 mt-0.5 ${isDark ? 'text-primary' : 'text-primary'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                          <p className={`text-sm font-medium ${isDark ? 'text-white' : 'text-surface-1'}`}>
                            What can Gemini AI do?
                          </p>
                          <ul className={`text-sm mt-2 space-y-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                            <li>Generate realistic phishing email templates</li>
                            <li>Create brand-specific impersonation emails</li>
                            <li>Improve existing templates with AI suggestions</li>
                            <li>Analyze email patterns for training purposes</li>
                          </ul>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <button
                        type="submit"
                        disabled={loading}
                        className="group relative px-6 py-3 rounded-xl font-semibold text-surface-1 overflow-hidden transition-all duration-300 disabled:opacity-50 hover:scale-[1.02]"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
                        <span className="relative">
                          {loading ? 'Saving...' : 'Save API Key'}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={handleTestGemini}
                        disabled={loading}
                        className={`px-6 py-3 rounded-xl font-semibold transition-all duration-200 hover:scale-[1.02] disabled:opacity-50 ${
                          isDark
                            ? 'bg-surface-3 text-white border border-white/10 hover:bg-surface-4'
                            : 'bg-surface-light-3 text-surface-1 border border-black/10 hover:bg-surface-light-4'
                        }`}
                      >
                        Test Connection
                      </button>
                    </div>
                  </form>

                  {/* Twilio SMS Configuration */}
                  <div className={`mt-8 pt-8 border-t ${isDark ? 'border-white/5' : 'border-black/5'}`}>
                    <div className="mb-6">
                      <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-surface-1'}`}>
                        Twilio SMS Configuration
                      </h2>
                      <p className={`text-sm mt-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                        Configure Twilio credentials to send SMS phishing simulations.
                      </p>
                    </div>

                    {twilioStatus && (
                      <div className={`mb-4 p-3 rounded-lg flex items-center ${
                        twilioStatus.configured
                          ? (isDark ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-700')
                          : (isDark ? 'bg-yellow-900/30 text-yellow-400' : 'bg-yellow-100 text-yellow-700')
                      }`}>
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          {twilioStatus.configured ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          )}
                        </svg>
                        <span className="text-sm font-medium">
                          {twilioStatus.configured ? 'Twilio SMS Configured' : 'Twilio SMS Not Configured'}
                        </span>
                      </div>
                    )}

                    <form onSubmit={handleAiSubmit} className="space-y-5">
                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          Account SID
                        </label>
                        <input
                          type="text"
                          value={aiForm.twilio_account_sid}
                          onChange={(e) => setAiForm({ ...aiForm, twilio_account_sid: e.target.value })}
                          placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                          className={`${inputClass} font-mono text-sm`}
                        />
                      </div>

                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          Auth Token
                        </label>
                        <input
                          type="password"
                          value={aiForm.twilio_auth_token}
                          onChange={(e) => setAiForm({ ...aiForm, twilio_auth_token: e.target.value })}
                          placeholder="your_auth_token_here"
                          className={`${inputClass} font-mono text-sm`}
                        />
                      </div>

                      <div>
                        <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                          Phone Number
                        </label>
                        <input
                          type="text"
                          value={aiForm.twilio_phone_number}
                          onChange={(e) => setAiForm({ ...aiForm, twilio_phone_number: e.target.value })}
                          placeholder="+1234567890"
                          className={`${inputClass} font-mono text-sm`}
                        />
                        <p className={`text-xs mt-2 ${isDark ? 'text-white/40' : 'text-surface-1/40'}`}>
                          Get your Twilio credentials from <a href="https://console.twilio.com/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Twilio Console</a>
                        </p>
                      </div>

                      <div className={`p-4 rounded-xl ${isDark ? 'bg-surface-3/50' : 'bg-surface-light-3'}`}>
                        <div className="flex items-start">
                          <svg className={`w-5 h-5 mr-3 mt-0.5 ${isDark ? 'text-primary' : 'text-primary'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <div>
                            <p className={`text-sm font-medium ${isDark ? 'text-white' : 'text-surface-1'}`}>
                              How to get Twilio credentials
                            </p>
                            <ol className={`text-sm mt-2 space-y-1 list-decimal list-inside ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                              <li>Sign up for a Twilio account at twilio.com</li>
                              <li>Go to Console Dashboard</li>
                              <li>Copy Account SID and Auth Token</li>
                              <li>Purchase a phone number or use trial number</li>
                              <li>Enter credentials above and save</li>
                            </ol>
                          </div>
                        </div>
                      </div>

                      <button
                        type="submit"
                        disabled={loading}
                        className="group relative px-6 py-3 rounded-xl font-semibold text-surface-1 overflow-hidden transition-all duration-300 disabled:opacity-50 hover:scale-[1.02]"
                      >
                        <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
                        <span className="relative">
                          {loading ? 'Saving...' : 'Save Twilio Settings'}
                        </span>
                      </button>
                    </form>
                  </div>
                </div>
              </div>
            )}

            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="p-6">
                <form onSubmit={handleProfileSubmit} className="space-y-6">
                  <div>
                    <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      Profile Information
                    </h2>
                    <p className={`text-sm mt-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                      Update your account profile information.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                        First Name
                      </label>
                      <input
                        type="text"
                        value={profileForm.first_name}
                        onChange={(e) => setProfileForm({ ...profileForm, first_name: e.target.value })}
                        className={inputClass}
                      />
                    </div>
                    <div>
                      <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                        Last Name
                      </label>
                      <input
                        type="text"
                        value={profileForm.last_name}
                        onChange={(e) => setProfileForm({ ...profileForm, last_name: e.target.value })}
                        className={inputClass}
                      />
                    </div>
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={profileForm.email}
                      onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                      className={inputClass}
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="group relative px-6 py-3 rounded-xl font-semibold text-surface-1 overflow-hidden transition-all duration-300 disabled:opacity-50 hover:scale-[1.02]"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
                    <span className="relative">
                      {loading ? 'Saving...' : 'Save Changes'}
                    </span>
                  </button>
                </form>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="p-6">
                <form onSubmit={handlePasswordSubmit} className="space-y-6">
                  <div>
                    <h2 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      Change Password
                    </h2>
                    <p className={`text-sm mt-1 ${isDark ? 'text-white/50' : 'text-surface-1/50'}`}>
                      Update your account password.
                    </p>
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={passwordForm.current_password}
                      onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                      className={inputClass}
                      required
                    />
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      New Password
                    </label>
                    <input
                      type="password"
                      value={passwordForm.new_password}
                      onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                      className={inputClass}
                      required
                      minLength={6}
                    />
                  </div>

                  <div>
                    <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-white' : 'text-surface-1'}`}>
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      value={passwordForm.confirm_password}
                      onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                      className={inputClass}
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="group relative px-6 py-3 rounded-xl font-semibold text-surface-1 overflow-hidden transition-all duration-300 disabled:opacity-50 hover:scale-[1.02]"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-primary to-primary-dim" />
                    <span className="relative">
                      {loading ? 'Changing...' : 'Change Password'}
                    </span>
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
