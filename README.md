# PhishVision 🎣

**Phishing Campaign Generator & Email Security Analysis Platform**

PhishVision is a comprehensive security training tool that generates realistic phishing simulations and analyzes incoming emails for phishing indicators. Built for SOC teams, security researchers, and organizations looking to improve their security awareness.

## Features

### 24-Hour Hackathon MVP ✅

- ✅ **2 Phishing Templates**: Bank Security Alert & Package Delivery
- ✅ **Email Tracking**: Track email opens and link clicks in real-time
- ✅ **Email Classification**: NLP-based analysis (safe, suspicious, malicious)
- ✅ **Basic Statistics**: Dashboard with campaign performance metrics

### Full Project Features

- **Phishing Campaign Generator**
  - Create realistic phishing simulations
  - Multiple pre-built templates
  - Track opens, clicks, and user behavior
  - Comprehensive campaign analytics

- **Email Analyzer**
  - NLP-based content analysis
  - SPF/DKIM/DMARC header validation
  - Suspicious keyword detection
  - URL analysis and risk scoring
  - Detailed explanations for each classification

- **SOC Dashboard**
  - Real-time statistics and metrics
  - Campaign performance tracking
  - Threat distribution visualization
  - Recent activity timeline

## Tech Stack

### Backend
- **Python 3.10+** with Flask
- **SQLAlchemy** for database management
- **Regex-based NLP** for text analysis
- **dnspython** for DNS/email header validation

### Frontend
- **React 18** with React Router
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Axios** for API communication

### Database
- SQLite (development)
- PostgreSQL/MySQL ready (production)

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 16+ and npm
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Set up environment variables
cp ../.env.example .env
# Edit .env file with your configuration

# Initialize database
python app.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```
Backend will run on `http://localhost:5000`

### Start Frontend (Terminal 2)
```bash
cd frontend
npm start
```
Frontend will run on `http://localhost:3000`

## Usage

### 1. Create a Phishing Campaign

1. Navigate to **Campaigns** tab
2. Click **"+ New Campaign"**
3. Fill in campaign details:
   - Campaign name
   - Template type (Bank Alert or Package Delivery)
   - Target emails (comma-separated)
4. Click **"Create Campaign"**

The system will automatically send emails and start tracking opens/clicks.

### 2. Analyze Email for Phishing

1. Navigate to **Email Analyzer** tab
2. Enter email details:
   - Sender email address
   - Subject line
   - Email body
   - Headers (optional)
3. Click **"Analyze Email"**

The system will provide:
- Risk classification (safe/suspicious/malicious)
- Risk score (0-100)
- SPF/DKIM/DMARC validation results
- Detailed explanation
- Security recommendations

### 3. View Dashboard

The dashboard provides:
- Total campaigns and emails sent
- Open and click rates
- Threat detection statistics
- Recent activity timeline
- Threat distribution chart

## API Documentation

### Campaigns

- `GET /api/campaigns/` - Get all campaigns
- `GET /api/campaigns/:id` - Get campaign details
- `POST /api/campaigns/` - Create new campaign
- `PUT /api/campaigns/:id/status` - Update campaign status
- `DELETE /api/campaigns/:id` - Delete campaign

### Email Analyzer

- `POST /api/analyzer/analyze` - Analyze email
- `GET /api/analyzer/history` - Get analysis history
- `GET /api/analyzer/:id` - Get specific analysis
- `GET /api/analyzer/stats` - Get analyzer statistics

### Dashboard

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent activity
- `GET /api/dashboard/campaign-performance` - Get campaign performance
- `GET /api/dashboard/threat-distribution` - Get threat distribution

### Tracking

- `GET /track/open/:token` - Track email open (returns 1x1 pixel)
- `GET /track/click/:token` - Track link click (redirects to education page)

## Email Configuration (Optional)

To send real emails instead of mock mode, configure SMTP settings in `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@phishvision.com
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in SMTP_PASSWORD

## Project Structure

```
phishvision/
├── backend/
│   ├── app.py                 # Flask application
│   ├── models.py              # Database models
│   ├── routes/
│   │   ├── campaign_routes.py # Campaign API endpoints
│   │   ├── analyzer_routes.py # Email analyzer endpoints
│   │   ├── tracking_routes.py # Tracking endpoints
│   │   └── dashboard_routes.py# Dashboard endpoints
│   ├── services/
│   │   ├── email_service.py   # Email sending service
│   │   ├── nlp_analyzer.py    # NLP analysis engine
│   │   └── header_validator.py# Email header validation
│   └── templates/
│       └── phishing_templates.py # Email templates
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js
│   │   │   ├── CampaignManager.js
│   │   │   ├── CampaignDetails.js
│   │   │   └── EmailAnalyzer.js
│   │   ├── api/
│   │   │   └── api.js         # API client
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── requirements.txt
├── .env.example
└── README.md
```

## Security & Ethics

⚠️ **IMPORTANT**: This tool is designed for:
- Authorized security training and awareness programs
- Educational purposes in controlled environments
- Security research with proper authorization
- Internal organizational testing with approval

**DO NOT:**
- Use this tool for malicious purposes
- Send phishing emails without explicit authorization
- Target individuals or organizations without consent
- Violate any laws or regulations

Always ensure:
1. Written authorization before launching campaigns
2. Clear communication about security training exercises
3. Proper data handling and privacy compliance
4. Immediate user education after campaign completion

## Future Enhancements

### For Final Project MVP:
- [ ] Template builder with drag-and-drop interface
- [ ] SOC response timeline and incident tracking
- [ ] Advanced NLP with ML-based classification
- [ ] Enhanced dashboard with more visualizations
- [ ] User management and role-based access
- [ ] Reporting and export functionality
- [ ] Integration with SIEM systems
- [ ] Multi-language support

## Troubleshooting

### Backend won't start
- Ensure Python 3.10+ is installed: `python --version`
- Activate virtual environment
- Install all dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Ensure Node.js 16+ is installed: `node --version`
- Delete `node_modules` and `package-lock.json`, then run `npm install`
- Clear npm cache: `npm cache clean --force`

### Database errors
- Delete `phishvision.db` and restart backend to recreate database
- Check file permissions

### Email not sending
- Check SMTP configuration in `.env`
- Verify credentials and network connectivity
- Check if using mock mode (default if no SMTP configured)

## Contributing

This is a hackathon project. Contributions and improvements are welcome!

## License

MIT License - See LICENSE file for details

## Team

Built with ❤️ for security awareness training

---

**Happy Phishing Detection!** 🎣🔒


