/**
 * PhishVision Extension - Background Service Worker
 * Handles context menus, API calls, and extension coordination
 */

// Default settings
const DEFAULT_SETTINGS = {
  backendUrl: 'http://localhost:5000',
  enableNotifications: true,
  enablePassiveMonitoring: false
};

// URL result cache (in-memory, cleared on service worker restart)
const urlCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Initialize extension on install
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('PhishVision Extension installed:', details.reason);

  // Set default settings
  const settings = await chrome.storage.local.get('settings');
  if (!settings.settings) {
    await chrome.storage.local.set({ settings: DEFAULT_SETTINGS });
  }

  // Create context menus
  createContextMenus();
});

// Create context menus on startup
chrome.runtime.onStartup.addListener(() => {
  createContextMenus();
});

/**
 * Create right-click context menu items
 */
function createContextMenus() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: 'check-link',
      title: 'Check this link with PhishVision',
      contexts: ['link']
    });

    chrome.contextMenus.create({
      id: 'analyze-selection',
      title: 'Analyze selected text with PhishVision',
      contexts: ['selection']
    });

    chrome.contextMenus.create({
      id: 'analyze-page',
      title: 'Analyze this page with PhishVision',
      contexts: ['page']
    });
  });
}

/**
 * Handle context menu clicks
 */
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  switch (info.menuItemId) {
    case 'check-link':
      await handleCheckLink(info.linkUrl, tab);
      break;
    case 'analyze-selection':
      await handleAnalyzeSelection(info.selectionText, tab);
      break;
    case 'analyze-page':
      await handleAnalyzePage(tab);
      break;
  }
});

/**
 * Check a URL from context menu
 */
async function handleCheckLink(url, tab) {
  try {
    // Update badge to show loading
    chrome.action.setBadgeText({ text: '...', tabId: tab.id });
    chrome.action.setBadgeBackgroundColor({ color: '#666666', tabId: tab.id });

    const result = await checkUrl(url);

    // Update badge with result
    updateBadge(result.classification, tab.id);

    // Show notification if dangerous
    if (result.classification === 'malicious') {
      showNotification('Dangerous Link Detected!',
        `Risk Score: ${result.risk_score}/100\n${result.reasons[0] || 'Multiple phishing indicators found'}`,
        'danger');
    } else if (result.classification === 'suspicious') {
      showNotification('Suspicious Link',
        `Risk Score: ${result.risk_score}/100\nProceed with caution.`,
        'warning');
    }

    // Store result for popup to display
    await chrome.storage.local.set({
      lastResult: { type: 'url', data: result, timestamp: Date.now() }
    });

  } catch (error) {
    console.error('Error checking URL:', error);
    chrome.action.setBadgeText({ text: 'ERR', tabId: tab.id });
    chrome.action.setBadgeBackgroundColor({ color: '#ff3366', tabId: tab.id });
  }
}

/**
 * Analyze selected text
 */
async function handleAnalyzeSelection(text, tab) {
  try {
    chrome.action.setBadgeText({ text: '...', tabId: tab.id });
    chrome.action.setBadgeBackgroundColor({ color: '#666666', tabId: tab.id });

    const result = await analyzeContent(text);

    updateBadge(result.classification, tab.id);

    if (result.classification === 'malicious') {
      showNotification('Phishing Content Detected!',
        `Risk Score: ${result.risk_score}/100`,
        'danger');
    }

    await chrome.storage.local.set({
      lastResult: { type: 'content', data: result, timestamp: Date.now() }
    });

    // Open popup to show results
    chrome.action.openPopup();

  } catch (error) {
    console.error('Error analyzing selection:', error);
    chrome.action.setBadgeText({ text: 'ERR', tabId: tab.id });
  }
}

/**
 * Analyze current page
 */
async function handleAnalyzePage(tab) {
  try {
    // Send message to content script to get page info
    chrome.tabs.sendMessage(tab.id, { action: 'getPageLinks' }, async (response) => {
      if (chrome.runtime.lastError) {
        console.error('Content script error:', chrome.runtime.lastError);
        return;
      }

      if (response && response.links) {
        chrome.action.setBadgeText({ text: '...', tabId: tab.id });

        const result = await checkUrlsBatch(response.links);

        await chrome.storage.local.set({
          lastResult: { type: 'page', data: result, pageUrl: tab.url, timestamp: Date.now() }
        });

        // Update badge based on worst result
        if (result.summary.malicious > 0) {
          updateBadge('malicious', tab.id);
          showNotification('Dangerous Links Found!',
            `${result.summary.malicious} malicious links detected on this page.`,
            'danger');
        } else if (result.summary.suspicious > 0) {
          updateBadge('suspicious', tab.id);
        } else {
          updateBadge('safe', tab.id);
        }
      }
    });
  } catch (error) {
    console.error('Error analyzing page:', error);
  }
}

/**
 * Update extension badge
 */
function updateBadge(classification, tabId) {
  const config = {
    safe: { text: '', color: '#00ff88' },
    suspicious: { text: '!', color: '#ffaa00' },
    malicious: { text: '!!', color: '#ff3366' }
  };

  const { text, color } = config[classification] || config.safe;

  if (tabId) {
    chrome.action.setBadgeText({ text, tabId });
    chrome.action.setBadgeBackgroundColor({ color, tabId });
  } else {
    chrome.action.setBadgeText({ text });
    chrome.action.setBadgeBackgroundColor({ color });
  }
}

/**
 * Show browser notification
 */
async function showNotification(title, message, type = 'info') {
  const settings = await chrome.storage.local.get('settings');
  if (!settings.settings?.enableNotifications) return;

  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'src/assets/icons/icon-128.png',
    title: `PhishVision: ${title}`,
    message: message,
    priority: type === 'danger' ? 2 : 1
  });
}

/**
 * API Functions
 */

async function getBackendUrl() {
  const settings = await chrome.storage.local.get('settings');
  return settings.settings?.backendUrl || DEFAULT_SETTINGS.backendUrl;
}

async function checkUrl(url) {
  // Check cache first
  const cached = urlCache.get(url);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.result;
  }

  const backendUrl = await getBackendUrl();
  const response = await fetch(`${backendUrl}/api/extension/check-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ url })
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication required');
    }
    throw new Error(`API error: ${response.status}`);
  }

  const result = await response.json();

  // Cache result
  urlCache.set(url, { result, timestamp: Date.now() });

  return result;
}

async function checkUrlsBatch(urls) {
  const backendUrl = await getBackendUrl();
  const response = await fetch(`${backendUrl}/api/extension/check-urls`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ urls: urls.slice(0, 50) })
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication required');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

async function analyzeContent(content, subject = '', sender = '') {
  const backendUrl = await getBackendUrl();
  const response = await fetch(`${backendUrl}/api/extension/analyze-quick`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ content, subject, sender })
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication required');
    }
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

async function checkAuthStatus() {
  const backendUrl = await getBackendUrl();
  try {
    const response = await fetch(`${backendUrl}/api/auth/me`, {
      credentials: 'include'
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Handle messages from popup and content scripts
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      switch (message.action) {
        case 'checkUrl':
          sendResponse(await checkUrl(message.url));
          break;
        case 'checkUrlsBatch':
          sendResponse(await checkUrlsBatch(message.urls));
          break;
        case 'analyzeContent':
          sendResponse(await analyzeContent(message.content, message.subject, message.sender));
          break;
        case 'checkAuth':
          sendResponse({ authenticated: await checkAuthStatus() });
          break;
        case 'getSettings':
          const settings = await chrome.storage.local.get('settings');
          sendResponse(settings.settings || DEFAULT_SETTINGS);
          break;
        case 'updateBadge':
          updateBadge(message.classification, sender.tab?.id);
          sendResponse({ success: true });
          break;
        default:
          sendResponse({ error: 'Unknown action' });
      }
    } catch (error) {
      sendResponse({ error: error.message });
    }
  })();

  return true; // Keep message channel open for async response
});

console.log('PhishVision background service worker loaded');
