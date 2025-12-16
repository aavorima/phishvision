import React, { useState } from 'react';
import { useTheme } from '../ThemeContext';

const guideContent = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: 'M13 10V3L4 14h7v7l9-11h-7z',
    content: `
## Welcome to PhishVision

PhishVision is a comprehensive phishing simulation and security awareness training platform designed for authorized organizational security testing.

### First Steps

1. **Create an Account**: Register a new account to get started
2. **Configure SMTP**: Set up your mail server in Settings to send phishing emails
3. **Add Employees**: Import your organization's employees as campaign targets
4. **Create Templates**: Design or use AI to generate phishing email templates
5. **Launch Campaigns**: Start your first phishing simulation

### Important Notes

- Always obtain proper authorization before running phishing simulations
- This tool is for educational and security testing purposes only
- Ensure compliance with your organization's policies
    `
  },
  {
    id: 'campaigns',
    title: 'Email Campaigns',
    icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    content: `
## Email Phishing Campaigns

Create and manage email phishing campaigns to test employee awareness.

### Creating a Campaign

1. Navigate to **Campaigns > Email Campaigns**
2. Click "New Campaign"
3. Select a template or create custom content
4. Choose target employees
5. Optionally attach a landing page for credential harvesting
6. Launch the campaign

### Tracking Results

- **Sent**: Email was delivered
- **Opened**: Recipient opened the email (tracked via pixel)
- **Clicked**: Recipient clicked a link
- **Submitted**: Recipient entered credentials on landing page

### Best Practices

- Start with a small pilot group
- Vary difficulty levels
- Schedule campaigns during normal business hours
- Follow up failed tests with training
    `
  },
  {
    id: 'templates',
    title: 'Email Templates',
    icon: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6z',
    content: `
## Email Templates

Create realistic phishing templates for your campaigns.

### Template Categories

- **IT Support**: Password resets, system updates
- **HR**: Policy updates, benefits, surveys
- **Finance**: Invoice, payment, expense reports
- **Banking**: Account alerts, security notices
- **Delivery**: Package tracking, shipping updates

### Using Variables

Templates support dynamic variables:
- \`{{first_name}}\` - Recipient's first name
- \`{{last_name}}\` - Recipient's last name
- \`{{email}}\` - Recipient's email
- \`{{department}}\` - Recipient's department
- \`{{company}}\` - Company name

### AI Template Generation

Use the AI generator to create realistic templates:
1. Select category and difficulty
2. Provide context or scenario
3. Let AI generate the template
4. Review and customize as needed
    `
  },
  {
    id: 'landing-pages',
    title: 'Credential Harvesting',
    icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z',
    content: `
## Landing Pages (Credential Harvesting)

Create fake login pages to test if employees submit credentials.

### Creating Landing Pages

1. Go to **Campaigns > Credential Harvest**
2. Choose from built-in templates or clone a website
3. Customize the appearance
4. Set a redirect URL for after submission

### Website Cloning

Clone any website to create a realistic login page:
1. Enter the target URL
2. PhishVision will scrape and replicate the page
3. Forms are automatically configured to capture input
4. Original form actions are replaced with tracking

### Ethical Considerations

- Credentials are NOT stored - only the submission event is logged
- Use this feature responsibly
- Notify IT security team before testing
- Follow your organization's data handling policies
    `
  },
  {
    id: 'qr-phishing',
    title: 'QR Code Phishing',
    icon: 'M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z',
    content: `
## QR Code Phishing (Quishing)

Test employee awareness against QR code-based attacks.

### How It Works

1. Create a QR campaign with a target URL
2. Generate QR codes for printing/sharing
3. Track scans and subsequent actions
4. Measure vulnerability to physical attacks

### Placement Strategies

- Office bulletin boards
- Fake promotional posters
- "Free WiFi" signs
- Parking lot flyers
- Conference room notices

### Tracking

- Total scans
- Unique devices
- Device types (mobile/tablet/desktop)
- Credential submissions if linked to landing page
    `
  },
  {
    id: 'sms-phishing',
    title: 'SMS Phishing',
    icon: 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z',
    content: `
## SMS Phishing (Smishing)

Test employee awareness against SMS-based attacks.

### Creating SMS Campaigns

1. Navigate to **Campaigns > SMS Phishing**
2. Write your SMS message (160 characters recommended)
3. Add target phone numbers
4. Include a tracking link
5. Schedule or send immediately

### Message Templates

Use these common smishing scenarios:
- Bank alerts
- Package delivery
- IT support requests
- Prize/reward notifications
- Urgent account issues

### Character Limits

- Standard SMS: 160 characters
- Consider URL shortening for tracking links
- Keep messages concise and urgent
    `
  },
  {
    id: 'risk-scoring',
    title: 'User Risk Scoring',
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    content: `
## User Risk Scoring

Track and manage employee phishing susceptibility.

### Risk Levels

- **Low (0-25)**: Minimal risk, passes most tests
- **Medium (25-50)**: Moderate risk, occasional failures
- **High (50-75)**: High risk, frequent failures
- **Critical (75-100)**: Very high risk, requires immediate training

### Repeat Offender Detection

Users are flagged as repeat offenders if:
- Clicked on 3+ phishing links
- Submitted credentials 2+ times
- Failed consecutive tests

### Training Integration

- Automatic training assignment for high-risk users
- Manager notifications for repeat offenders
- Risk score reduction after successful training
- Progress tracking and reporting
    `
  },
  {
    id: 'soc-timeline',
    title: 'SOC Timeline',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    content: `
## SOC Timeline & Incidents

Track security incidents and response times.

### Incident Types

- **Phishing Click**: User clicked a phishing link
- **Credential Entered**: User submitted credentials
- **Malware Download**: User downloaded malicious file
- **Reported Email**: User reported suspicious email

### Incident Workflow

1. **Detected**: Incident automatically created
2. **Investigating**: SOC analyst reviewing
3. **Contained**: Threat contained/isolated
4. **Resolved**: Incident closed

### Metrics Tracked

- Mean Time to Detect (MTTD)
- Mean Time to Respond (MTTR)
- Incident volume by type
- Resolution rates
- Response time trends
    `
  }
];

function UserGuide() {
  const { isDark } = useTheme();
  const [activeSection, setActiveSection] = useState('getting-started');

  const bgColor = isDark ? 'bg-slate-900' : 'bg-slate-50';
  const cardBg = isDark ? 'bg-slate-800' : 'bg-white';
  const borderColor = isDark ? 'border-slate-700' : 'border-slate-200';
  const textColor = isDark ? 'text-white' : 'text-slate-900';
  const textMuted = isDark ? 'text-slate-400' : 'text-slate-500';

  const activeContent = guideContent.find(g => g.id === activeSection);

  const renderMarkdown = (content) => {
    return content
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('## ')) {
          return <h2 key={i} className={`text-xl font-bold ${textColor} mt-6 mb-4`}>{line.slice(3)}</h2>;
        }
        if (line.startsWith('### ')) {
          return <h3 key={i} className={`text-lg font-semibold ${textColor} mt-4 mb-2`}>{line.slice(4)}</h3>;
        }
        if (line.startsWith('- ')) {
          return (
            <li key={i} className={`${textMuted} ml-4 mb-1`}>
              {line.slice(2).split('**').map((part, j) =>
                j % 2 === 1 ? <strong key={j} className={textColor}>{part}</strong> : part
              )}
            </li>
          );
        }
        if (line.match(/^\d+\. /)) {
          return (
            <li key={i} className={`${textMuted} ml-4 mb-1 list-decimal`}>
              {line.slice(line.indexOf(' ') + 1).split('**').map((part, j) =>
                j % 2 === 1 ? <strong key={j} className={textColor}>{part}</strong> : part
              )}
            </li>
          );
        }
        if (line.trim() === '') {
          return <div key={i} className="h-2" />;
        }
        return (
          <p key={i} className={`${textMuted} mb-2`}>
            {line.split('`').map((part, j) =>
              j % 2 === 1 ? (
                <code key={j} className={`${isDark ? 'bg-slate-700' : 'bg-slate-200'} px-1.5 py-0.5 rounded text-sm ${textColor}`}>
                  {part}
                </code>
              ) : part
            )}
          </p>
        );
      });
  };

  return (
    <div className={`min-h-screen ${bgColor} p-6`}>
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className={`text-2xl font-bold ${textColor}`}>User Guide</h1>
          <p className={`${textMuted} mt-2`}>
            Learn how to use PhishVision for security awareness training and phishing simulations.
          </p>
        </div>

        <div className="flex gap-6">
          {/* Sidebar */}
          <div className={`w-64 ${cardBg} rounded-xl p-3 h-fit sticky top-6`}>
            <nav className="space-y-1">
              {guideContent.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                    activeSection === section.id
                      ? 'bg-blue-600 text-white'
                      : `${textColor} hover:bg-slate-700/50`
                  }`}
                >
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={section.icon} />
                  </svg>
                  <span className="text-sm font-medium">{section.title}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className={`flex-1 ${cardBg} rounded-xl p-8`}>
            {activeContent && (
              <div className="prose prose-invert max-w-none">
                {renderMarkdown(activeContent.content)}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserGuide;
