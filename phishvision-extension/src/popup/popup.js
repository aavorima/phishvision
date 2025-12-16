/**
 * PhishVision Extension - Popup Script
 */

// DOM Elements
const loginView = document.getElementById('loginView');
const mainView = document.getElementById('mainView');
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');
const serverUrl = document.getElementById('serverUrl');
const loading = document.getElementById('loading');

// Tabs
const tabs = document.querySelectorAll('.tab');
const tabPanes = document.querySelectorAll('.tab-pane');

// Buttons
const scanBtn = document.getElementById('scanBtn');
const checkUrlBtn = document.getElementById('checkUrlBtn');
const scanPageBtn = document.getElementById('scanPageBtn');
const analyzeEmailBtn = document.getElementById('analyzeEmailBtn');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const logoutBtn = document.getElementById('logoutBtn');
const settingsBtn = document.getElementById('settingsBtn');
const closeResults = document.getElementById('closeResults');

// Email view elements
const emailView = document.getElementById('emailView');
const regularPageView = document.getElementById('regularPageView');
const emailProvider = document.getElementById('emailProvider');
const emailSender = document.getElementById('emailSender');
const emailSubject = document.getElementById('emailSubject');

// Store extracted email data
let currentEmailData = null;

// Store current analysis ID for feedback
let currentAnalysisId = null;

// Inputs
const scanContent = document.getElementById('scanContent');
const urlInput = document.getElementById('urlInput');

// Results
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
  try {
    // Load settings and show server URL
    const settings = await getSettings();
    serverUrl.textContent = settings.backendUrl.replace(/^https?:\/\//, '');

    // Check authentication status
    await checkAuth();

    // Check for pending results
    await checkPendingResults();

    // Update current page URL and detect email
    updateCurrentPageUrl();
    await detectEmailPage();

    // Setup event listeners
    setupEventListeners();
  } catch (error) {
    console.error('Init error:', error);
    // Show login view as fallback
    showLoginView();
    showLoading(false);
  }
}

function setupEventListeners() {
  // Tab navigation
  tabs.forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });

  // Login form
  loginForm.addEventListener('submit', handleLogin);

  // Scan button
  scanBtn.addEventListener('click', handleScan);

  // URL check
  checkUrlBtn.addEventListener('click', handleUrlCheck);
  urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleUrlCheck();
  });

  // Page scan
  scanPageBtn.addEventListener('click', handlePageScan);

  // Email analysis
  analyzeEmailBtn.addEventListener('click', handleEmailAnalysis);

  // History
  clearHistoryBtn.addEventListener('click', clearHistory);

  // Logout
  logoutBtn.addEventListener('click', handleLogout);

  // Settings
  settingsBtn.addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });

  // Close results
  closeResults.addEventListener('click', () => {
    resultsSection.classList.add('hidden');
  });
}

/**
 * Check authentication status
 */
async function checkAuth() {
  showLoading(true);
  try {
    const response = await sendMessage({ action: 'checkAuth' });
    if (response.authenticated) {
      showMainView();
      await loadUserInfo();
    } else {
      showLoginView();
    }
  } catch (error) {
    console.error('Auth check failed:', error);
    showLoginView();
  }
  showLoading(false);
}

/**
 * Handle login form submission
 */
async function handleLogin(e) {
  e.preventDefault();
  showLoading(true);
  loginError.classList.add('hidden');

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  try {
    const settings = await getSettings();
    const response = await fetch(`${settings.backendUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
      await chrome.storage.local.set({ user: data.user });
      showMainView();
      document.getElementById('userEmail').textContent = data.user.email;
    } else {
      showLoginError(data.error || 'Login failed');
    }
  } catch (error) {
    console.error('Login error:', error);
    showLoginError('Cannot connect to server');
  }
  showLoading(false);
}

/**
 * Handle logout
 */
async function handleLogout() {
  try {
    const settings = await getSettings();
    await fetch(`${settings.backendUrl}/api/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    });
  } catch (error) {
    console.error('Logout error:', error);
  }

  await chrome.storage.local.remove(['user']);
  showLoginView();
}

/**
 * Load user info
 */
async function loadUserInfo() {
  const data = await chrome.storage.local.get('user');
  if (data.user) {
    document.getElementById('userEmail').textContent = data.user.email;
  }
}

/**
 * Handle content scan
 */
async function handleScan() {
  const content = scanContent.value.trim();
  if (!content) {
    alert('Please enter content to analyze');
    return;
  }

  showLoading(true);
  try {
    const result = await sendMessage({
      action: 'analyzeContent',
      content: content
    });

    if (result.error) {
      throw new Error(result.error);
    }

    displayContentResults(result);
    saveToHistory('content', result);
  } catch (error) {
    console.error('Scan error:', error);
    alert('Analysis failed: ' + error.message);
  }
  showLoading(false);
}

/**
 * Handle URL check
 */
async function handleUrlCheck() {
  let url = urlInput.value.trim();
  if (!url) {
    alert('Please enter a URL to check');
    return;
  }

  // Add protocol if missing
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url;
  }

  showLoading(true);
  try {
    const result = await sendMessage({
      action: 'checkUrl',
      url: url
    });

    if (result.error) {
      throw new Error(result.error);
    }

    displayUrlResults(result);
    saveToHistory('url', result);
  } catch (error) {
    console.error('URL check error:', error);
    alert('Check failed: ' + error.message);
  }
  showLoading(false);
}

/**
 * Handle page scan
 */
async function handlePageScan() {
  showLoading(true);
  try {
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Request links from content script
    chrome.tabs.sendMessage(tab.id, { action: 'getPageLinks' }, async (response) => {
      if (chrome.runtime.lastError || !response) {
        showLoading(false);
        alert('Cannot scan this page. Try refreshing the page.');
        return;
      }

      if (response.links.length === 0) {
        showLoading(false);
        alert('No links found on this page');
        return;
      }

      // Check all links
      const result = await sendMessage({
        action: 'checkUrlsBatch',
        urls: response.links
      });

      if (result.error) {
        throw new Error(result.error);
      }

      displayPageResults(result);
      saveToHistory('page', result);
      showLoading(false);
    });
  } catch (error) {
    console.error('Page scan error:', error);
    alert('Scan failed: ' + error.message);
    showLoading(false);
  }
}

/**
 * Detect if current page is an email page
 */
async function detectEmailPage() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id) {
      showRegularPageView();
      return;
    }

    // First check if it's an email page
    chrome.tabs.sendMessage(tab.id, { action: 'detectEmailPage' }, (detection) => {
      if (chrome.runtime.lastError) {
        console.log('Cannot detect email page:', chrome.runtime.lastError);
        showRegularPageView();
        return;
      }

      console.log('Email detection result:', detection);

      if (detection && detection.isEmailPage && detection.isViewingEmail) {
        // Try to extract email content
        chrome.tabs.sendMessage(tab.id, { action: 'extractEmail' }, (response) => {
          if (chrome.runtime.lastError) {
            console.log('Cannot extract email:', chrome.runtime.lastError);
            // Still show email view with basic info
            showEmailViewBasic(detection);
            return;
          }

          if (response && response.success && response.email) {
            currentEmailData = response;
            showEmailView(response);
          } else if (response && response.detection) {
            // Extraction failed but we know it's an email page
            showEmailViewBasic(response.detection);
          } else {
            showRegularPageView();
          }
        });
      } else if (detection && detection.isEmailPage) {
        // On email provider but not viewing specific email
        showRegularPageView();
      } else {
        showRegularPageView();
      }
    });
  } catch (error) {
    console.error('Email detection error:', error);
    showRegularPageView();
  }
}

/**
 * Show email view with extracted data
 */
function showEmailView(data) {
  emailView.classList.remove('hidden');
  regularPageView.classList.add('hidden');

  emailProvider.textContent = data.detection.providerName + ' Email';
  emailSender.textContent = data.email.senderEmail || data.email.sender || 'Unknown';
  emailSubject.textContent = data.email.subject || '(No subject)';
}

/**
 * Show email view with basic detection info (when extraction fails)
 */
function showEmailViewBasic(detection) {
  emailView.classList.remove('hidden');
  regularPageView.classList.add('hidden');

  emailProvider.textContent = detection.providerName + ' Email';
  emailSender.textContent = 'Click to analyze';
  emailSubject.textContent = '(Email detected)';

  // Set minimal email data for analysis attempt
  currentEmailData = {
    detection: detection,
    email: {
      subject: '',
      sender: '',
      senderEmail: '',
      body: '',
      links: [],
      linkCount: 0
    },
    warnings: {}
  };
}

/**
 * Show regular page view
 */
function showRegularPageView() {
  emailView.classList.add('hidden');
  regularPageView.classList.remove('hidden');
}

/**
 * Handle email analysis
 */
async function handleEmailAnalysis() {
  if (!currentEmailData) {
    alert('No email data available. Please refresh the email page and try again.');
    return;
  }

  showLoading(true);

  try {
    let email = currentEmailData.email;

    // If email body is empty, try to re-extract
    if (!email.body || email.body.length < 10) {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.id) {
        const freshData = await new Promise((resolve) => {
          chrome.tabs.sendMessage(tab.id, { action: 'extractEmail' }, (response) => {
            if (chrome.runtime.lastError) {
              resolve(null);
            } else {
              resolve(response);
            }
          });
        });

        if (freshData && freshData.success && freshData.email) {
          currentEmailData = freshData;
          email = freshData.email;
          showEmailView(freshData);
        }
      }
    }

    // If still no content, try to get page content as fallback
    if (!email.body || email.body.length < 10) {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.id) {
        const pageContent = await new Promise((resolve) => {
          chrome.tabs.sendMessage(tab.id, { action: 'getPageContent' }, (response) => {
            if (chrome.runtime.lastError) {
              resolve(null);
            } else {
              resolve(response);
            }
          });
        });

        if (pageContent && pageContent.text) {
          email.body = pageContent.text;
          email.subject = email.subject || pageContent.title;
        }
      }
    }

    if (!email.body || email.body.length < 10) {
      throw new Error('Could not extract email content. Please try selecting the email text manually.');
    }

    // Send to backend for analysis
    const result = await sendMessage({
      action: 'analyzeContent',
      content: email.body,
      subject: email.subject,
      sender: email.senderEmail || email.sender
    });

    if (result.error) {
      throw new Error(result.error);
    }

    // Add email-specific warnings
    if (currentEmailData.warnings) {
      result.emailWarnings = currentEmailData.warnings;
    }
    result.emailLinks = email.links || [];
    result.linkCount = email.linkCount || 0;

    displayEmailResults(result);
    saveToHistory('email', result);
  } catch (error) {
    console.error('Email analysis error:', error);
    alert('Analysis failed: ' + error.message);
  }

  showLoading(false);
}

/**
 * Display email analysis results
 */
function displayEmailResults(result) {
  const scoreClass = getScoreClass(result.classification);

  // Store analysis ID for feedback
  currentAnalysisId = result.analysis_id;

  let warningsHtml = '';

  // DOM-based warnings
  if (result.emailWarnings) {
    if (result.emailWarnings.hasHiddenLinks) {
      warningsHtml += `
        <div class="warning-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span>Hidden links detected in this email!</span>
        </div>
      `;
    }
    if (result.emailWarnings.hasMismatchedLinks) {
      warningsHtml += `
        <div class="warning-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span>Link URLs don't match displayed text!</span>
        </div>
      `;
    }
  }

  // AI analysis info
  let aiInfoHtml = '';
  if (result.ai_used) {
    aiInfoHtml = `
      <div class="ai-info">
        <span class="ai-badge">AI Enhanced</span>
        ${result.ai_confidence ? `<span class="ai-confidence">${Math.round(result.ai_confidence * 100)}% confidence</span>` : ''}
      </div>
    `;
  }

  // AI reasoning
  let aiReasoningHtml = '';
  if (result.ai_reasoning) {
    aiReasoningHtml = `
      <div class="reasons-list ai-reasoning">
        <h4>AI Analysis</h4>
        <p style="font-size:11px;color:var(--text-secondary);">${escapeHtml(result.ai_reasoning)}</p>
      </div>
    `;
  }

  // Feedback section
  const feedbackHtml = currentAnalysisId ? `
    <div class="feedback-section" id="feedbackSection">
      <div class="feedback-question">Was this analysis correct?</div>
      <div class="feedback-buttons">
        <button class="feedback-btn correct" onclick="submitFeedback('${result.classification}')" title="Yes, this is correct">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          Correct
        </button>
        <button class="feedback-btn safe" onclick="submitFeedback('safe')" title="Actually it's safe">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          It's Safe
        </button>
        <button class="feedback-btn phishing" onclick="submitFeedback('malicious')" title="Actually it's phishing">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          It's Phishing
        </button>
      </div>
      <div id="feedbackMessage" class="feedback-message hidden"></div>
    </div>
  ` : '';

  resultsContent.innerHTML = `
    <div class="risk-score">
      <div class="score-value ${scoreClass}">${Math.round(result.risk_score)}</div>
      <div class="score-label">Risk Score</div>
      <span class="classification ${result.classification}">${result.classification}</span>
    </div>

    ${aiInfoHtml}
    ${warningsHtml}

    ${result.linkCount > 0 ? `
    <div style="margin-top:12px;font-size:11px;color:var(--text-muted);text-align:center;">
      ${result.linkCount} link${result.linkCount > 1 ? 's' : ''} found in email
    </div>
    ` : ''}

    ${aiReasoningHtml}

    ${result.explanation ? `
    <div class="reasons-list">
      <h4>Analysis Details</h4>
      <pre style="font-size:11px;white-space:pre-wrap;color:var(--text-secondary);max-height:120px;overflow:auto;">${escapeHtml(result.explanation.substring(0, 400))}</pre>
    </div>
    ` : ''}

    ${result.recommendations && Array.isArray(result.recommendations) && result.recommendations.length > 0 ? `
    <div class="reasons-list">
      <h4>Recommendations</h4>
      <ul>
        ${result.recommendations.slice(0, 3).map(r => `<li>${escapeHtml(r)}</li>`).join('')}
      </ul>
    </div>
    ` : (result.recommendations && typeof result.recommendations === 'string' ? `
    <div class="reasons-list">
      <h4>Recommendations</h4>
      <p style="font-size:12px;color:var(--text-secondary);">${escapeHtml(result.recommendations.substring(0, 200))}</p>
    </div>
    ` : '')}

    ${feedbackHtml}
  `;

  resultsSection.classList.remove('hidden');
}

/**
 * Display content analysis results
 */
function displayContentResults(result) {
  const scoreClass = getScoreClass(result.classification);

  // Store analysis ID for feedback
  currentAnalysisId = result.analysis_id;

  // AI analysis info
  let aiInfoHtml = '';
  if (result.ai_used) {
    aiInfoHtml = `
      <div class="ai-info">
        <span class="ai-badge">AI Enhanced</span>
        ${result.ai_confidence ? `<span class="ai-confidence">${Math.round(result.ai_confidence * 100)}% confidence</span>` : ''}
      </div>
    `;
  }

  // AI reasoning
  let aiReasoningHtml = '';
  if (result.ai_reasoning) {
    aiReasoningHtml = `
      <div class="reasons-list ai-reasoning">
        <h4>AI Analysis</h4>
        <p style="font-size:11px;color:var(--text-secondary);">${escapeHtml(result.ai_reasoning)}</p>
      </div>
    `;
  }

  // Feedback section
  const feedbackHtml = currentAnalysisId ? `
    <div class="feedback-section" id="feedbackSection">
      <div class="feedback-question">Was this analysis correct?</div>
      <div class="feedback-buttons">
        <button class="feedback-btn correct" onclick="submitFeedback('${result.classification}')" title="Yes, this is correct">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          Correct
        </button>
        <button class="feedback-btn safe" onclick="submitFeedback('safe')" title="Actually it's safe">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          It's Safe
        </button>
        <button class="feedback-btn phishing" onclick="submitFeedback('malicious')" title="Actually it's phishing">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          It's Phishing
        </button>
      </div>
      <div id="feedbackMessage" class="feedback-message hidden"></div>
    </div>
  ` : '';

  resultsContent.innerHTML = `
    <div class="risk-score">
      <div class="score-value ${scoreClass}">${Math.round(result.risk_score)}</div>
      <div class="score-label">Risk Score</div>
      <span class="classification ${result.classification}">${result.classification}</span>
    </div>

    ${aiInfoHtml}

    ${aiReasoningHtml}

    ${result.explanation ? `
    <div class="reasons-list">
      <h4>Analysis Details</h4>
      <pre style="font-size:11px;white-space:pre-wrap;color:var(--text-secondary);max-height:150px;overflow:auto;">${escapeHtml(result.explanation.substring(0, 500))}</pre>
    </div>
    ` : ''}

    ${feedbackHtml}
  `;

  resultsSection.classList.remove('hidden');
}

/**
 * Display URL check results
 */
function displayUrlResults(result) {
  const scoreClass = getScoreClass(result.classification);

  resultsContent.innerHTML = `
    <div class="risk-score">
      <div class="score-value ${scoreClass}">${Math.round(result.risk_score)}</div>
      <div class="score-label">Risk Score</div>
      <span class="classification ${result.classification}">${result.classification}</span>
    </div>

    <div style="margin-top:12px;font-size:11px;word-break:break-all;color:var(--text-muted);">
      ${escapeHtml(result.url)}
    </div>

    ${result.reasons && result.reasons.length > 0 ? `
    <div class="reasons-list">
      <h4>Issues Found</h4>
      <ul>
        ${result.reasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
      </ul>
    </div>
    ` : ''}
  `;

  resultsSection.classList.remove('hidden');
}

/**
 * Display page scan results
 */
function displayPageResults(result) {
  const summary = result.summary;

  resultsContent.innerHTML = `
    <div class="page-results">
      <div class="stat-box">
        <div class="stat-value" style="color:var(--safe)">${summary.safe}</div>
        <div class="stat-label">Safe</div>
      </div>
      <div class="stat-box">
        <div class="stat-value" style="color:var(--warning)">${summary.suspicious}</div>
        <div class="stat-label">Suspicious</div>
      </div>
      <div class="stat-box">
        <div class="stat-value" style="color:var(--danger)">${summary.malicious}</div>
        <div class="stat-label">Malicious</div>
      </div>
    </div>

    <div style="margin-top:12px;font-size:11px;color:var(--text-muted);">
      Scanned ${summary.total} links on this page
    </div>

    ${summary.malicious > 0 || summary.suspicious > 0 ? `
    <div class="reasons-list">
      <h4>Problematic Links</h4>
      <ul>
        ${result.results
          .filter(r => r.classification !== 'safe')
          .slice(0, 5)
          .map(r => `<li style="font-size:10px;word-break:break-all;">
            <span style="color:${r.classification === 'malicious' ? 'var(--danger)' : 'var(--warning)'}">
              [${r.risk_score}]
            </span>
            ${escapeHtml(r.url.substring(0, 50))}...
          </li>`)
          .join('')}
      </ul>
    </div>
    ` : ''}
  `;

  resultsSection.classList.remove('hidden');
}

/**
 * Check for pending results from context menu actions
 */
async function checkPendingResults() {
  const data = await chrome.storage.local.get('lastResult');
  if (data.lastResult && Date.now() - data.lastResult.timestamp < 30000) {
    const result = data.lastResult;

    if (result.type === 'url') {
      displayUrlResults(result.data);
    } else if (result.type === 'content') {
      displayContentResults(result.data);
    } else if (result.type === 'page') {
      displayPageResults(result.data);
    }

    // Clear pending result
    await chrome.storage.local.remove('lastResult');
  }
}

/**
 * Update current page URL display
 */
async function updateCurrentPageUrl() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url) {
      document.getElementById('currentUrl').textContent =
        tab.url.length > 50 ? tab.url.substring(0, 50) + '...' : tab.url;
    }
  } catch (error) {
    console.error('Cannot get current tab:', error);
  }
}

/**
 * Save scan to history
 */
async function saveToHistory(type, result) {
  const data = await chrome.storage.local.get('scanHistory');
  const history = data.scanHistory || [];

  history.unshift({
    type,
    classification: result.classification,
    score: result.risk_score || result.summary?.malicious || 0,
    timestamp: Date.now()
  });

  // Keep only last 20 items
  await chrome.storage.local.set({
    scanHistory: history.slice(0, 20)
  });

  loadHistory();
}

/**
 * Load history
 */
async function loadHistory() {
  const data = await chrome.storage.local.get('scanHistory');
  const history = data.scanHistory || [];
  const historyList = document.getElementById('historyList');

  if (history.length === 0) {
    historyList.innerHTML = '<p class="empty-state">No recent scans</p>';
    return;
  }

  historyList.innerHTML = history.map(item => `
    <div class="history-item">
      <div>
        <span class="type">${item.type.toUpperCase()}</span>
        <span style="margin-left:8px;font-size:11px;color:var(--text-muted)">
          ${formatTime(item.timestamp)}
        </span>
      </div>
      <span class="score" style="background:${getScoreBgColor(item.classification)};color:${getScoreColor(item.classification)}">
        ${Math.round(item.score)}
      </span>
    </div>
  `).join('');
}

/**
 * Clear history
 */
async function clearHistory() {
  await chrome.storage.local.remove('scanHistory');
  loadHistory();
}

/**
 * Tab switching
 */
function switchTab(tabName) {
  tabs.forEach(t => t.classList.remove('active'));
  tabPanes.forEach(p => p.classList.remove('active'));

  document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
  document.getElementById(`${tabName}Tab`).classList.add('active');

  if (tabName === 'history') {
    loadHistory();
  }
}

/**
 * Utility functions
 */
function showLoginView() {
  loginView.classList.remove('hidden');
  mainView.classList.add('hidden');
}

function showMainView() {
  loginView.classList.add('hidden');
  mainView.classList.remove('hidden');
}

function showLoginError(message) {
  loginError.textContent = message;
  loginError.classList.remove('hidden');
}

function showLoading(show) {
  loading.classList.toggle('hidden', !show);
}

async function getSettings() {
  const response = await sendMessage({ action: 'getSettings' });
  return response || { backendUrl: 'http://localhost:5000' };
}

function sendMessage(message) {
  return new Promise((resolve) => {
    try {
      chrome.runtime.sendMessage(message, (response) => {
        if (chrome.runtime.lastError) {
          console.error('Message error:', chrome.runtime.lastError);
          resolve(null);
        } else {
          resolve(response);
        }
      });
    } catch (error) {
      console.error('SendMessage error:', error);
      resolve(null);
    }
  });
}

function getScoreClass(classification) {
  const classes = {
    safe: 'score-safe',
    suspicious: 'score-suspicious',
    malicious: 'score-malicious'
  };
  return classes[classification] || 'score-safe';
}

function getScoreColor(classification) {
  const colors = {
    safe: 'var(--safe)',
    suspicious: 'var(--warning)',
    malicious: 'var(--danger)'
  };
  return colors[classification] || colors.safe;
}

function getScoreBgColor(classification) {
  const colors = {
    safe: 'rgba(0,255,136,0.15)',
    suspicious: 'rgba(255,170,0,0.15)',
    malicious: 'rgba(255,51,102,0.15)'
  };
  return colors[classification] || colors.safe;
}

function formatTime(timestamp) {
  const diff = Date.now() - timestamp;
  if (diff < 60000) return 'Just now';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
  return new Date(timestamp).toLocaleDateString();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Submit user feedback on analysis results
 */
async function submitFeedback(userClassification) {
  if (!currentAnalysisId) {
    console.error('No analysis ID available for feedback');
    return;
  }

  const feedbackSection = document.getElementById('feedbackSection');
  const feedbackMessage = document.getElementById('feedbackMessage');
  const buttons = feedbackSection?.querySelectorAll('.feedback-btn');

  // Disable buttons while submitting
  buttons?.forEach(btn => btn.disabled = true);

  try {
    const settings = await getSettings();
    const response = await fetch(`${settings.backendUrl}/api/feedback/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        analysis_id: currentAnalysisId,
        user_classification: userClassification
      })
    });

    const data = await response.json();

    if (response.ok && data.success) {
      // Show success message
      if (feedbackMessage) {
        feedbackMessage.textContent = data.message || 'Thank you for your feedback!';
        feedbackMessage.className = 'feedback-message success';
        feedbackMessage.classList.remove('hidden');
      }

      // Show learning info if pattern was created/updated
      if (data.learning_result) {
        if (data.learning_result.pattern_created) {
          feedbackMessage.innerHTML += '<br><small>New detection pattern learned!</small>';
        } else if (data.learning_result.pattern_updated) {
          feedbackMessage.innerHTML += '<br><small>Detection patterns adjusted.</small>';
        }
      }

      // Hide buttons after successful feedback
      const buttonsDiv = feedbackSection?.querySelector('.feedback-buttons');
      if (buttonsDiv) {
        buttonsDiv.style.display = 'none';
      }

    } else {
      throw new Error(data.error || 'Failed to submit feedback');
    }
  } catch (error) {
    console.error('Feedback submission error:', error);

    // Show error message
    if (feedbackMessage) {
      feedbackMessage.textContent = 'Could not submit feedback. Please try again.';
      feedbackMessage.className = 'feedback-message error';
      feedbackMessage.classList.remove('hidden');
    }

    // Re-enable buttons
    buttons?.forEach(btn => btn.disabled = false);
  }
}
