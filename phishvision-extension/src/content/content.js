/**
 * PhishVision Extension - Content Script
 * Runs on all web pages to extract links, detect emails, and interact with page content
 */

// Email provider configurations
const EMAIL_PROVIDERS = {
  gmail: {
    hostMatch: /mail\.google\.com/,
    selectors: {
      // Gmail selectors - multiple fallbacks for different views
      emailContainer: '[role="main"] [role="listitem"][data-message-id], .adn, .gs, .nH .if, [data-message-id]',
      subject: 'h2[data-thread-perm-id], h2.hP, [data-thread-perm-id] h2, .hP',
      sender: 'span[email], .gD, [email], .go',
      senderEmail: 'span[email], [email]',
      body: '.a3s.aiL, .a3s, .ii.gt, [data-message-id] .a3s, .gmail_quote',
      date: '.g3, .gH .g3, [title*="202"]'
    }
  },
  outlook: {
    hostMatch: /outlook\.(live|office365|office)\.com/,
    selectors: {
      emailContainer: '[role="main"] [role="document"], [data-app-section="ConversationContainer"], .customScrollBar, [aria-label*="Message"]',
      subject: '[role="heading"][aria-level="2"], .allowTextSelection, [aria-label*="Subject"]',
      sender: 'span[title*="@"], .OZZZK, [aria-label*="From"]',
      senderEmail: 'span[title*="@"]',
      body: '[role="document"] div[dir="ltr"], .XbIp4, [aria-label*="Message body"]',
      date: 'span[title*=":"], [aria-label*="Received"]'
    }
  },
  yahoo: {
    hostMatch: /mail\.yahoo\.com/,
    selectors: {
      emailContainer: '[data-test-id="message-view"], [data-test-id="message-list-item"]',
      subject: '[data-test-id="message-subject"], [data-test-id="message-group-subject-text"]',
      sender: '[data-test-id="message-from"], [data-test-id="message-group-sender-name"]',
      senderEmail: '[data-test-id="message-from"] span',
      body: '[data-test-id="message-view"] [dir="ltr"], [data-test-id="message-body"]',
      date: '[data-test-id="message-date"], [data-test-id="message-time"]'
    }
  }
};

// Listen for messages from background script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'getPageLinks':
      sendResponse({ links: extractPageLinks() });
      break;

    case 'getSelectedText':
      sendResponse({ text: window.getSelection().toString() });
      break;

    case 'highlightDangerousLinks':
      highlightLinks(message.results);
      sendResponse({ success: true });
      break;

    case 'getPageContent':
      sendResponse({
        title: document.title,
        url: window.location.href,
        text: document.body.innerText.substring(0, 5000)
      });
      break;

    case 'detectEmailPage':
      sendResponse(detectEmailPage());
      break;

    case 'extractEmail':
      sendResponse(extractEmailContent());
      break;

    default:
      sendResponse({ error: 'Unknown action' });
  }

  return true; // Keep channel open for async response
});

/**
 * Detect if current page is an email reading page
 */
function detectEmailPage() {
  const hostname = window.location.hostname;
  const url = window.location.href;

  console.log('PhishVision: Detecting email page on', hostname);

  for (const [provider, config] of Object.entries(EMAIL_PROVIDERS)) {
    if (config.hostMatch.test(hostname)) {
      console.log('PhishVision: Matched provider:', provider);

      // Check if we're viewing an email (not just inbox)
      const emailContainer = document.querySelector(config.selectors.emailContainer);
      const bodyEl = document.querySelector(config.selectors.body);
      const subjectEl = document.querySelector(config.selectors.subject);

      // For Gmail, also check URL pattern for opened email
      const isGmailOpenedEmail = provider === 'gmail' && url.includes('#inbox/') || url.includes('#sent/') || url.includes('#label/');

      const hasEmailContent = (emailContainer && emailContainer.innerText.length > 20) ||
                              (bodyEl && bodyEl.innerText.length > 20) ||
                              subjectEl ||
                              isGmailOpenedEmail;

      console.log('PhishVision: Email detected?', hasEmailContent, {
        emailContainer: !!emailContainer,
        bodyEl: !!bodyEl,
        subjectEl: !!subjectEl,
        isGmailOpenedEmail
      });

      return {
        isEmailPage: true,
        isViewingEmail: hasEmailContent,
        provider: provider,
        providerName: provider.charAt(0).toUpperCase() + provider.slice(1)
      };
    }
  }

  return {
    isEmailPage: false,
    isViewingEmail: false,
    provider: null,
    providerName: null
  };
}

/**
 * Extract email content from the page
 */
function extractEmailContent() {
  const detection = detectEmailPage();

  if (!detection.isEmailPage) {
    return { error: 'Not an email page', detection };
  }

  const config = EMAIL_PROVIDERS[detection.provider];
  if (!config) {
    return { error: 'Unknown email provider', detection };
  }

  try {
    // Extract subject
    const subjectEl = document.querySelector(config.selectors.subject);
    const subject = subjectEl ? subjectEl.innerText.trim() : '';

    // Extract sender
    const senderEl = document.querySelector(config.selectors.sender);
    const senderEmailEl = document.querySelector(config.selectors.senderEmail);
    const sender = senderEl ? senderEl.innerText.trim() : '';
    const senderEmail = senderEmailEl ?
      (senderEmailEl.getAttribute('email') || senderEmailEl.getAttribute('title') || senderEmailEl.innerText).trim() :
      extractEmailFromText(sender);

    // Extract body
    const bodyEl = document.querySelector(config.selectors.body);
    const body = bodyEl ? bodyEl.innerText.trim() : '';

    // Extract date
    const dateEl = document.querySelector(config.selectors.date);
    const date = dateEl ? dateEl.innerText.trim() : '';

    // Extract links from email
    const links = [];
    if (bodyEl) {
      bodyEl.querySelectorAll('a[href]').forEach(a => {
        const href = a.href;
        if (href && href.startsWith('http')) {
          links.push({
            url: href,
            text: a.innerText.trim().substring(0, 100)
          });
        }
      });
    }

    // Check for common phishing indicators in the DOM
    const hasHiddenLinks = checkForHiddenLinks(bodyEl);
    const hasMismatchedLinks = checkForMismatchedLinks(bodyEl);

    return {
      success: true,
      detection,
      email: {
        subject,
        sender,
        senderEmail,
        body: body.substring(0, 10000), // Limit body size
        date,
        links: links.slice(0, 50), // Limit links
        linkCount: links.length
      },
      warnings: {
        hasHiddenLinks,
        hasMismatchedLinks
      }
    };
  } catch (error) {
    return {
      error: 'Failed to extract email: ' + error.message,
      detection
    };
  }
}

/**
 * Extract email address from text
 */
function extractEmailFromText(text) {
  const match = text.match(/[\w.-]+@[\w.-]+\.\w+/);
  return match ? match[0] : text;
}

/**
 * Check for hidden links (display:none, visibility:hidden, tiny size)
 */
function checkForHiddenLinks(container) {
  if (!container) return false;

  const links = container.querySelectorAll('a[href]');
  for (const link of links) {
    const style = window.getComputedStyle(link);
    if (
      style.display === 'none' ||
      style.visibility === 'hidden' ||
      style.opacity === '0' ||
      (parseInt(style.fontSize) < 2) ||
      (link.offsetWidth < 2 && link.offsetHeight < 2)
    ) {
      return true;
    }
  }
  return false;
}

/**
 * Check for mismatched links (display text doesn't match href)
 */
function checkForMismatchedLinks(container) {
  if (!container) return false;

  const links = container.querySelectorAll('a[href]');
  for (const link of links) {
    const href = link.href.toLowerCase();
    const text = link.innerText.toLowerCase().trim();

    // Check if text looks like a URL but doesn't match href
    if (text.match(/^https?:\/\//) || text.match(/^www\./)) {
      try {
        const textDomain = new URL(text.startsWith('www.') ? 'https://' + text : text).hostname;
        const hrefDomain = new URL(href).hostname;

        if (textDomain !== hrefDomain &&
            !hrefDomain.endsWith('.' + textDomain) &&
            !textDomain.endsWith('.' + hrefDomain)) {
          return true;
        }
      } catch {
        // Invalid URL in text, might be suspicious
      }
    }
  }
  return false;
}

/**
 * Extract all unique links from the page
 */
function extractPageLinks() {
  const links = new Set();

  // Get all anchor tags
  document.querySelectorAll('a[href]').forEach(anchor => {
    const href = anchor.href;
    if (isValidUrl(href)) {
      links.add(href);
    }
  });

  // Get links from onclick handlers (common in phishing)
  document.querySelectorAll('[onclick]').forEach(el => {
    const onclick = el.getAttribute('onclick');
    const urlMatch = onclick.match(/https?:\/\/[^\s'"<>]+/g);
    if (urlMatch) {
      urlMatch.forEach(url => {
        if (isValidUrl(url)) {
          links.add(url);
        }
      });
    }
  });

  // Get links from data attributes
  document.querySelectorAll('[data-href], [data-url], [data-link]').forEach(el => {
    const url = el.getAttribute('data-href') ||
                el.getAttribute('data-url') ||
                el.getAttribute('data-link');
    if (url && isValidUrl(url)) {
      links.add(url);
    }
  });

  return Array.from(links);
}

/**
 * Check if URL is valid and should be scanned
 */
function isValidUrl(url) {
  try {
    const parsed = new URL(url);
    // Only check http/https URLs
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return false;
    }
    // Skip same-origin links (usually safe)
    if (parsed.origin === window.location.origin) {
      return false;
    }
    // Skip common safe domains
    const safeDomains = [
      'google.com', 'googleapis.com', 'gstatic.com',
      'facebook.com', 'fbcdn.net',
      'twitter.com', 'twimg.com',
      'youtube.com', 'ytimg.com',
      'linkedin.com',
      'microsoft.com', 'windows.net', 'azure.com',
      'apple.com', 'icloud.com',
      'amazon.com', 'amazonaws.com', 'cloudfront.net',
      'github.com', 'githubusercontent.com'
    ];

    const hostname = parsed.hostname.toLowerCase();
    for (const safe of safeDomains) {
      if (hostname === safe || hostname.endsWith('.' + safe)) {
        return false;
      }
    }

    return true;
  } catch {
    return false;
  }
}

/**
 * Highlight dangerous links on the page
 */
function highlightLinks(results) {
  // Remove existing highlights
  document.querySelectorAll('.phishvision-warning').forEach(el => el.remove());

  // Create stylesheet if not exists
  if (!document.getElementById('phishvision-styles')) {
    const style = document.createElement('style');
    style.id = 'phishvision-styles';
    style.textContent = `
      .phishvision-warning {
        position: absolute;
        background: #ff3366;
        color: white;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 3px;
        z-index: 999999;
        font-family: system-ui, sans-serif;
        pointer-events: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      }
      .phishvision-warning.suspicious {
        background: #ffaa00;
        color: #1a1a2e;
      }
      .phishvision-link-danger {
        outline: 2px solid #ff3366 !important;
        outline-offset: 2px;
      }
      .phishvision-link-suspicious {
        outline: 2px solid #ffaa00 !important;
        outline-offset: 2px;
      }
    `;
    document.head.appendChild(style);
  }

  // Create map of URL -> result
  const resultMap = new Map();
  results.forEach(r => resultMap.set(r.url, r));

  // Find and highlight dangerous links
  document.querySelectorAll('a[href]').forEach(anchor => {
    const result = resultMap.get(anchor.href);
    if (!result) return;

    if (result.classification === 'malicious') {
      anchor.classList.add('phishvision-link-danger');
      addWarningBadge(anchor, 'DANGER', 'malicious');
    } else if (result.classification === 'suspicious') {
      anchor.classList.add('phishvision-link-suspicious');
      addWarningBadge(anchor, 'CAUTION', 'suspicious');
    }
  });
}

/**
 * Add warning badge next to a link
 */
function addWarningBadge(element, text, type) {
  const rect = element.getBoundingClientRect();
  const badge = document.createElement('div');
  badge.className = `phishvision-warning ${type === 'suspicious' ? 'suspicious' : ''}`;
  badge.textContent = text;
  badge.style.top = (window.scrollY + rect.top - 18) + 'px';
  badge.style.left = (window.scrollX + rect.left) + 'px';
  document.body.appendChild(badge);
}

// Log that content script is loaded (for debugging)
console.log('PhishVision content script loaded');
