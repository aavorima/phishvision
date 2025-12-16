# PhishVision - Project Documentation

> AI Context Document for understanding the full project

---

## Project Overview

**PhishVision** is an enterprise phishing awareness and threat intelligence platform that helps organizations:
- Simulate phishing attacks (Email, QR codes, SMS)
- Analyze emails for phishing using AI + NLP
- Build community threat intelligence
- Track employee security risk scores
- Learn from user feedback to improve detection

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         PhishVision                              │
├────────────────────┬────────────────────┬────────────────────────┤
│     Frontend       │      Backend       │   Browser Extension    │
│     (React)        │      (Flask)       │    (Chrome MV3)        │
│    Port 3000       │     Port 5000      │                        │
│                    │                    │                        │
│  - Dashboard       │  - REST API        │  - Email detection     │
│  - Campaigns       │  - SQLite DB       │  - URL checking        │
│  - Analyzer        │  - Gemini AI       │  - Page scanning       │
│  - Threat Feed     │  - NLP Engine      │  - Real-time alerts    │
└────────────────────┴────────────────────┴────────────────────────┘
```

---

## Directory Structure

```
/home/morpho/Desktop/Hackathon/
├── phishvision/
│   ├── backend/
│   │   ├── app.py                 # Flask app entry point
│   │   ├── database.py            # SQLAlchemy setup
│   │   ├── models.py              # 21 database models
│   │   ├── routes/                # 15 API route modules
│   │   │   ├── analyzer_routes.py      # Email analysis
│   │   │   ├── auth_routes.py          # Authentication
│   │   │   ├── campaign_routes.py      # Email campaigns
│   │   │   ├── threat_feed_routes.py   # Threat intelligence
│   │   │   ├── feedback_routes.py      # User feedback/learning
│   │   │   ├── employee_routes.py      # Employee management
│   │   │   ├── risk_routes.py          # Risk scoring
│   │   │   ├── soc_routes.py           # Security incidents
│   │   │   ├── template_routes.py      # Email templates
│   │   │   ├── landing_routes.py       # Credential harvesting
│   │   │   ├── qrcode_routes.py        # QR phishing
│   │   │   ├── sms_routes.py           # SMS phishing
│   │   │   ├── dashboard_routes.py     # Analytics
│   │   │   ├── tracking_routes.py      # Email open/click tracking
│   │   │   ├── extension_routes.py     # Browser extension API
│   │   │   └── settings_routes.py      # User settings
│   │   ├── services/              # 8 core services
│   │   │   ├── nlp_analyzer.py         # Rule-based detection (84KB)
│   │   │   ├── gemini_analyzer.py      # Google Gemini AI
│   │   │   ├── hybrid_analyzer.py      # NLP + AI combined
│   │   │   ├── ioc_extractor.py        # IOC extraction
│   │   │   ├── feedback_learner.py     # Pattern learning
│   │   │   ├── header_validator.py     # SPF/DKIM/DMARC
│   │   │   ├── email_service.py        # SMTP sending
│   │   │   └── email_parser.py         # Email parsing
│   │   ├── seed_from_archive.py   # Import phishing patterns
│   │   ├── seed_threat_feed.py    # Populate threat feed
│   │   └── phishvision.db         # SQLite database
│   │
│   └── frontend/
│       ├── src/
│       │   ├── App.js             # Main router
│       │   ├── AuthContext.js     # Auth state
│       │   ├── ThemeContext.js    # Dark/light mode
│       │   ├── api/api.js         # API client
│       │   └── components/        # 25+ React components
│       │       ├── Dashboard.js        # Main dashboard
│       │       ├── EmailAnalyzer.js    # Email analysis UI
│       │       ├── ThreatFeed.js       # Threat intel feed
│       │       ├── ThreatDetail.js     # Threat details
│       │       ├── CampaignManager.js  # Campaign management
│       │       ├── TemplateManager.js  # Email templates
│       │       ├── EmployeeManager.js  # Employee database
│       │       ├── UserRiskDashboard.js # Risk scores
│       │       ├── SOCTimeline.js      # Incident tracking
│       │       ├── QRPhishing.js       # Quishing campaigns
│       │       ├── SMSPhishing.js      # Smishing campaigns
│       │       ├── LandingPagesManager.js # Credential pages
│       │       ├── Settings.js         # User settings
│       │       └── ...
│       └── package.json
│
└── phishvision-extension/
    ├── manifest.json              # Chrome MV3 manifest
    └── src/
        ├── background/background.js    # Service worker
        ├── content/content.js          # DOM injection
        ├── popup/                      # Extension popup UI
        └── options/                    # Extension settings
```

---

## Core Features

### 1. Email Analysis (Hybrid AI + NLP)
- **NLP Engine**: Rule-based detection with 100+ keywords, typosquatting, URL analysis
- **Gemini AI**: Semantic understanding for zero-day threats
- **Hybrid Routing**: NLP first (fast), AI for uncertain cases (15-80 score range)
- **Multi-language**: English, Turkish, Azerbaijani support
- **Header Validation**: SPF, DKIM, DMARC checking
- **Trusted Domain Bypass**: Authenticated emails from Amazon, Google, etc. marked safe

### 2. Community Threat Intelligence
- **Auto-submission**: Malicious emails automatically added to threat feed
- **IOC Extraction**: Domains, URLs, IPs, sender patterns
- **Deduplication**: Hash-based duplicate detection
- **Public Feed**: Browse threats without login
- **Community Voting**: Phishing/safe votes
- **Defanging**: hxxp:// and [.] for safe display

### 3. Phishing Simulation Campaigns
- **Email Campaigns**: Templates, tracking, landing pages
- **QR Phishing (Quishing)**: Generate malicious QR codes
- **SMS Phishing (Smishing)**: SMS campaigns (Twilio optional)
- **Credential Harvesting**: Fake login pages
- **Tracking**: Open rates, click rates, device info

### 4. User Risk Scoring
- **Risk Levels**: Low (0-25), Medium (26-50), High (51-75), Critical (76-100)
- **Repeat Offenders**: 3+ clicks flagged
- **Training Assignment**: Auto-assign mandatory training
- **Department Analytics**: Risk heatmaps

### 5. Self-Learning System
- **Feedback Collection**: Users report false positives/negatives
- **Pattern Creation**: Auto-create PhishingPattern from corrections
- **Effectiveness Scoring**: Track pattern accuracy
- **Few-shot Learning**: Feed patterns to Gemini AI

### 6. SOC Integration
- **Incident Tracking**: Create/manage security incidents
- **Severity Levels**: Critical, High, Medium, Low
- **Status Flow**: Detected -> Investigating -> Contained -> Resolved
- **MTTR Tracking**: Mean time to response

---

## Key Backend Services

| Service | File | Purpose |
|---------|------|---------|
| NLP Analyzer | services/nlp_analyzer.py | Rule-based phishing detection with keywords, URL analysis, urgency scoring |
| Gemini Analyzer | services/gemini_analyzer.py | AI semantic analysis via Google Gemini API |
| Hybrid Analyzer | services/hybrid_analyzer.py | Combines NLP + AI with smart routing and weighted scoring |
| IOC Extractor | services/ioc_extractor.py | Extract and defang domains, URLs, IPs from threats |
| Feedback Learner | services/feedback_learner.py | Create patterns from user corrections |
| Header Validator | services/header_validator.py | Parse SPF, DKIM, DMARC results |
| Email Service | services/email_service.py | SMTP email sending with tracking |

---

## Key API Endpoints

### Analysis
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/analyzer/analyze | Analyze email for phishing (returns AI + NLP results) |
| GET | /api/analyzer/history | Get analysis history |
| GET | /api/analyzer/stats | Get analyzer statistics |

### Threat Intelligence
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/threats/feed | Public threat feed (paginated) |
| GET | /api/threats/entry/<short_id> | Get threat details |
| GET | /api/threats/stats | Threat statistics |
| POST | /api/threats/submit | Submit analysis to feed |
| POST | /api/threats/entry/<id>/vote | Vote phishing/safe |

### Campaigns
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET/POST | /api/campaigns/ | List/create campaigns |
| POST | /api/campaigns/<id>/launch | Launch campaign |
| GET | /api/campaigns/<id>/stats | Campaign statistics |

### User Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login |
| GET | /api/auth/me | Current user |
| GET/POST | /api/employees/ | Employee management |
| GET | /api/risk/users | Risk scores |

### Dashboard
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/dashboard/stats | Overall statistics |
| GET | /api/dashboard/recent-activity | Recent activity feed |

---

## Database Models

### Core Models
| Model | Purpose |
|-------|---------|
| User | Authentication, roles (admin/user) |
| Settings | Per-user SMTP, API keys, timezone |
| EmailAnalysis | Analysis results with NLP + AI fields |
| AnalysisFeedback | User corrections for learning |
| PhishingPattern | Learned patterns for few-shot |

### Threat Intelligence
| Model | Purpose |
|-------|---------|
| ThreatEntry | Public threat feed entries |
| ThreatIOC | Indicators of compromise |
| ThreatVote | Community votes |

### Campaigns
| Model | Purpose |
|-------|---------|
| Campaign | Email phishing campaigns |
| CampaignTarget | Individual recipients |
| CustomTemplate | Email templates |
| LandingPage | Credential harvesting pages |
| CredentialCapture | Credential submission events |
| QRCodeCampaign | QR phishing campaigns |
| SMSCampaign | SMS phishing campaigns |

### Risk & SOC
| Model | Purpose |
|-------|---------|
| Employee | Organization employees |
| UserRiskScore | Risk assessment |
| SecurityIncident | SOC incidents |

---

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite + SQLAlchemy ORM
- **AI**: Google Gemini API (gemini-2.5-flash-lite)
- **Auth**: Session-based with werkzeug password hashing

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP**: Axios
- **Routing**: React Router

### Browser Extension
- **Manifest**: Chrome Manifest V3
- **Permissions**: activeTab, storage, contextMenus

---

## Environment Setup

### Required Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key    # Required for AI analysis
SECRET_KEY=your_flask_secret          # Flask session key
```

### Start Backend
```bash
cd /home/morpho/Desktop/Hackathon/phishvision/backend
python3 app.py
# Runs on http://localhost:5000
```

### Start Frontend
```bash
cd /home/morpho/Desktop/Hackathon/phishvision/frontend
npm start
# Runs on http://localhost:3000
```

### Seed Data (optional)
```bash
cd /home/morpho/Desktop/Hackathon/phishvision/backend
python3 seed_from_archive.py     # Load phishing patterns
python3 seed_threat_feed.py      # Populate threat feed
```

---

## Analysis Flow

```
Email Input
    |
    v
+---------------------+
|  Header Validation  |  <- SPF, DKIM, DMARC check
+---------------------+
    |
    v
+---------------------+
| Trusted Domain?     |  <- Amazon, Google, Microsoft, etc.
| + Auth Pass?        |
+---------------------+
    |
    +-- YES -> Score: 5, Classification: SAFE (skip AI)
    |
    +-- NO --v
             +---------------------+
             |    NLP Analysis     |  <- Fast, free, rule-based
             |  (nlp_analyzer.py)  |
             +---------------------+
                  |
                  | Score 15-80? (uncertain)
                  |
                  v
             +---------------------+
             |   Gemini AI Analysis|  <- Semantic understanding
             | (gemini_analyzer.py)|
             +---------------------+
                  |
                  v
             +---------------------+
             |   Hybrid Scoring    |  <- Weighted combination
             | (hybrid_analyzer.py)|
             +---------------------+
                  |
                  v
             +---------------------+
             |  Store in Database  |
             +---------------------+
                  |
                  | Classification = MALICIOUS?
                  |
                  v
             +---------------------+
             | Auto-submit to      |  <- Extract IOCs, create ThreatEntry
             | Threat Feed         |
             +---------------------+
```

---

## Current State (as of Dec 2024)

- AI integration complete (Hybrid analyzer connected to routes)
- Malicious emails auto-submit to threat feed
- 1,200+ phishing patterns loaded for few-shot learning
- 68 threats in community feed with 225+ IOCs
- Trusted domain bypass working (Amazon, Google, etc.)
- Browser extension functional with backend integration

---

## Key Files to Understand

| Priority | File | Why |
|----------|------|-----|
| 1 | backend/routes/analyzer_routes.py | Main email analysis endpoint |
| 2 | backend/services/hybrid_analyzer.py | Core analysis logic |
| 3 | backend/services/nlp_analyzer.py | Rule-based detection (largest file) |
| 4 | backend/models.py | All database models |
| 5 | backend/routes/threat_feed_routes.py | Threat intelligence API |
| 6 | frontend/src/components/EmailAnalyzer.js | Email analysis UI |
| 7 | frontend/src/components/ThreatFeed.js | Threat feed UI |
| 8 | frontend/src/api/api.js | All API endpoints |

---

## Common Tasks

### Analyze an email programmatically
```
POST /api/analyzer/analyze
{
    "email_from": "sender@example.com",
    "email_subject": "Subject line",
    "email_body": "Email body content",
    "headers": "Optional raw headers"
}
```

### Get threat feed
```
GET /api/threats/feed?page=1&per_page=20&classification=malicious
```

### Submit feedback on analysis
```
POST /api/feedback/submit
{
    "analysis_id": "uuid",
    "feedback_type": "false_positive|false_negative|correct",
    "user_classification": "safe|suspicious|malicious",
    "comments": "Optional notes"
}
```

---

## Notes for AI Assistants

1. **Working Directory**: Usually /home/morpho/Desktop/Hackathon/phishvision/backend
2. **Database**: SQLite at phishvision.db - use SQLAlchemy models
3. **API Base**: http://localhost:5000/api
4. **Frontend**: http://localhost:3000
5. **AI Key**: Set GEMINI_API_KEY in environment or user Settings
6. **Patterns**: Check PhishingPattern table for learned detection rules
7. **Threats**: Check ThreatEntry and ThreatIOC for intelligence data
