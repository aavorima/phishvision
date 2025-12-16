/**
 * PhishVision Extension - Options Page Script
 */

// Default settings
const DEFAULT_SETTINGS = {
  backendUrl: 'http://localhost:5000',
  enableNotifications: true,
  enablePassiveMonitoring: false
};

// DOM Elements
const backendUrlInput = document.getElementById('backendUrl');
const testConnectionBtn = document.getElementById('testConnection');
const connectionStatus = document.getElementById('connectionStatus');
const enableNotifications = document.getElementById('enableNotifications');
const enablePassiveMonitoring = document.getElementById('enablePassiveMonitoring');
const accountInfo = document.getElementById('accountInfo');
const signOutBtn = document.getElementById('signOutBtn');
const clearCacheBtn = document.getElementById('clearCache');
const clearHistoryBtn = document.getElementById('clearHistory');
const saveBtn = document.getElementById('saveBtn');
const saveStatus = document.getElementById('saveStatus');

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
  await loadSettings();
  await loadAccountInfo();
  setupEventListeners();
}

/**
 * Load settings from storage
 */
async function loadSettings() {
  const data = await chrome.storage.local.get('settings');
  const settings = data.settings || DEFAULT_SETTINGS;

  backendUrlInput.value = settings.backendUrl || DEFAULT_SETTINGS.backendUrl;
  enableNotifications.checked = settings.enableNotifications !== false;
  enablePassiveMonitoring.checked = settings.enablePassiveMonitoring === true;
}

/**
 * Load account information
 */
async function loadAccountInfo() {
  const data = await chrome.storage.local.get('user');

  if (data.user) {
    accountInfo.innerHTML = `
      <p>Signed in as:</p>
      <p class="email">${escapeHtml(data.user.email)}</p>
    `;
    signOutBtn.classList.remove('hidden');
  } else {
    accountInfo.innerHTML = '<p>Not signed in</p>';
    signOutBtn.classList.add('hidden');
  }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Test connection
  testConnectionBtn.addEventListener('click', testConnection);

  // Save settings
  saveBtn.addEventListener('click', saveSettings);

  // Sign out
  signOutBtn.addEventListener('click', handleSignOut);

  // Clear cache
  clearCacheBtn.addEventListener('click', async () => {
    // Send message to background to clear cache
    await chrome.runtime.sendMessage({ action: 'clearCache' });
    showStatus(clearCacheBtn, 'Cache cleared!', 'success');
  });

  // Clear history
  clearHistoryBtn.addEventListener('click', async () => {
    await chrome.storage.local.remove('scanHistory');
    showStatus(clearHistoryBtn, 'History cleared!', 'success');
  });

  // Auto-save on toggle changes
  enableNotifications.addEventListener('change', saveSettings);
  enablePassiveMonitoring.addEventListener('change', saveSettings);
}

/**
 * Test backend connection
 */
async function testConnection() {
  const url = backendUrlInput.value.trim();
  if (!url) {
    showConnectionStatus('Please enter a URL', 'error');
    return;
  }

  showConnectionStatus('Testing...', 'loading');

  try {
    const response = await fetch(`${url}/api/extension/status`, {
      method: 'GET',
      mode: 'cors',
      credentials: 'include'
    });

    if (response.ok) {
      const data = await response.json();
      const authStatus = data.authenticated ? 'authenticated' : 'not logged in';
      showConnectionStatus(`Connected! (${authStatus})`, 'success');
    } else {
      showConnectionStatus(`Server error: ${response.status}`, 'error');
    }
  } catch (error) {
    console.error('Connection test failed:', error);
    showConnectionStatus('Cannot connect to server', 'error');
  }
}

/**
 * Save settings to storage
 */
async function saveSettings() {
  const settings = {
    backendUrl: backendUrlInput.value.trim() || DEFAULT_SETTINGS.backendUrl,
    enableNotifications: enableNotifications.checked,
    enablePassiveMonitoring: enablePassiveMonitoring.checked
  };

  // Validate URL format
  try {
    new URL(settings.backendUrl);
  } catch {
    showSaveStatus('Invalid URL format', 'error');
    return;
  }

  await chrome.storage.local.set({ settings });
  showSaveStatus('Settings saved!', 'success');

  // Clear status after 2 seconds
  setTimeout(() => {
    saveStatus.textContent = '';
    saveStatus.className = 'status';
  }, 2000);
}

/**
 * Handle sign out
 */
async function handleSignOut() {
  try {
    const data = await chrome.storage.local.get('settings');
    const settings = data.settings || DEFAULT_SETTINGS;

    // Call logout endpoint
    await fetch(`${settings.backendUrl}/api/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    });
  } catch (error) {
    console.error('Logout error:', error);
  }

  // Clear user data
  await chrome.storage.local.remove(['user']);
  loadAccountInfo();
}

/**
 * Show connection status
 */
function showConnectionStatus(message, type) {
  connectionStatus.textContent = message;
  connectionStatus.className = `status ${type}`;
}

/**
 * Show save status
 */
function showSaveStatus(message, type) {
  saveStatus.textContent = message;
  saveStatus.className = `status ${type}`;
}

/**
 * Show temporary status next to a button
 */
function showStatus(button, message, type) {
  const existingStatus = button.nextElementSibling;
  if (existingStatus && existingStatus.classList.contains('temp-status')) {
    existingStatus.remove();
  }

  const status = document.createElement('span');
  status.className = `status temp-status ${type}`;
  status.textContent = message;
  status.style.marginLeft = '12px';
  button.parentNode.insertBefore(status, button.nextSibling);

  setTimeout(() => status.remove(), 2000);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
