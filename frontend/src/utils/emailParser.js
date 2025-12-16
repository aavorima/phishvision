/**
 * Email Parser Utility
 * Automatically extracts email components from pasted raw email content
 * Supports: RFC822, Forwarded emails, Gmail/Outlook copy-paste
 */

export function parseEmail(rawEmail) {
  if (!rawEmail || typeof rawEmail !== 'string') {
    return {
      email_from: '',
      email_subject: '',
      email_body: '',
      headers: '',
      success: false,
      error: 'Invalid email content'
    };
  }

  const lines = rawEmail.split('\n');
  let email_from = '';
  let email_subject = '';
  let headers = '';
  let email_body = '';
  let headerEndIndex = -1;

  // Extract From address
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Match "From:", "from:", "Sender:", etc.
    const fromMatch = line.match(/^(From|from|Sender|sender|FROM):\s*(.+)/i);
    if (fromMatch && !email_from) {
      let fromValue = fromMatch[2].trim();
      // Extract email from formats like "Name <email@domain.com>" or just "email@domain.com"
      const emailMatch = fromValue.match(/<([^>]+)>/) || fromValue.match(/([^\s]+@[^\s]+)/);
      email_from = emailMatch ? emailMatch[1] : fromValue;
    }

    // Match "Subject:"
    const subjectMatch = line.match(/^(Subject|subject|SUBJECT):\s*(.+)/i);
    if (subjectMatch && !email_subject) {
      email_subject = subjectMatch[2].trim();
      // Handle multi-line subjects (continuation lines start with space/tab)
      let j = i + 1;
      while (j < lines.length && lines[j].match(/^\s+/)) {
        email_subject += ' ' + lines[j].trim();
        j++;
      }
    }

    // Detect header section end (double newline or specific markers)
    if (line.trim() === '' && i > 0 && headerEndIndex === -1) {
      // Check if we've seen some headers
      const hasHeaders = email_from || email_subject ||
                        lines.slice(0, i).some(l =>
                          l.match(/^(Received|DKIM|SPF|Return-Path|Message-ID|Date|To|Cc):/i)
                        );
      if (hasHeaders) {
        headerEndIndex = i;
      }
    }
  }

  // Extract headers (everything before body)
  if (headerEndIndex > 0) {
    headers = lines.slice(0, headerEndIndex).join('\n');
  } else {
    // Try to detect header block heuristically
    for (let i = 0; i < Math.min(50, lines.length); i++) {
      const line = lines[i];
      // Stop at first line that doesn't look like a header
      if (line.trim() === '') {
        headerEndIndex = i;
        break;
      }
      if (!line.match(/^[\w-]+:/) && !line.match(/^\s+/)) {
        headerEndIndex = i;
        break;
      }
    }
    if (headerEndIndex > 0) {
      headers = lines.slice(0, headerEndIndex).join('\n');
    }
  }

  // Extract body (everything after headers)
  if (headerEndIndex > 0) {
    email_body = lines.slice(headerEndIndex + 1).join('\n').trim();
  } else {
    // Fallback: try to find body after common markers
    const bodyStartMarkers = [
      /^-+\s*Original Message\s*-+/i,
      /^-+\s*Forwarded message\s*-+/i,
      /^On .+ wrote:/i,
      /^Begin forwarded message:/i
    ];

    let bodyStartIndex = -1;
    for (let i = 0; i < lines.length; i++) {
      for (const marker of bodyStartMarkers) {
        if (lines[i].match(marker)) {
          bodyStartIndex = i + 1;
          break;
        }
      }
      if (bodyStartIndex > 0) break;
    }

    if (bodyStartIndex > 0) {
      email_body = lines.slice(bodyStartIndex).join('\n').trim();
    } else {
      // Ultimate fallback: everything after subject
      const subjectIndex = lines.findIndex(l => l.match(/^Subject:/i));
      if (subjectIndex >= 0) {
        email_body = lines.slice(subjectIndex + 1).join('\n').trim();
      } else {
        email_body = rawEmail.trim();
      }
    }
  }

  // Clean up body - remove excessive whitespace
  email_body = email_body.replace(/\n{3,}/g, '\n\n').trim();

  // If we didn't find From or Subject, try alternative patterns
  if (!email_from) {
    // Try to find email address anywhere in first 20 lines
    for (let i = 0; i < Math.min(20, lines.length); i++) {
      const emailMatch = lines[i].match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/);
      if (emailMatch) {
        email_from = emailMatch[1];
        break;
      }
    }
  }

  // Validate that we extracted something useful
  const success = !!(email_from || email_subject || (email_body && email_body.length > 10));

  return {
    email_from: email_from || '',
    email_subject: email_subject || '',
    email_body: email_body || rawEmail.trim(),
    headers: headers || '',
    success: success,
    error: success ? null : 'Could not parse email. Please check the format.'
  };
}

/**
 * Validate parsed email data
 */
export function validateParsedEmail(parsedData) {
  const errors = [];

  if (!parsedData.email_from) {
    errors.push('Email sender not found');
  } else if (!parsedData.email_from.includes('@')) {
    errors.push('Invalid email format for sender');
  }

  if (!parsedData.email_subject || parsedData.email_subject.length < 3) {
    errors.push('Subject line too short or missing');
  }

  if (!parsedData.email_body || parsedData.email_body.length < 10) {
    errors.push('Email body too short or missing');
  }

  return {
    isValid: errors.length === 0,
    errors: errors
  };
}

/**
 * Format preview text for display
 */
export function formatPreview(text, maxLength = 100) {
  if (!text) return '(empty)';
  const trimmed = text.trim();
  if (trimmed.length <= maxLength) return trimmed;
  return trimmed.substring(0, maxLength) + '...';
}
