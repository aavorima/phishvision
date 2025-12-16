# PhishVision Demo Data Setup

This guide will help you populate your PhishVision database with realistic demo data for testing and demonstration purposes.

## What's Included

The demo data seeder creates a complete, realistic PhishVision environment with:

### 👥 Users & Employees
- **21 Employees** across 7 departments (Engineering, Finance, HR, Marketing, Sales, IT, Executive)
- **1 Demo Admin User** (username: `demo`, password: `demo123`)

### 📧 Phishing Campaigns
- **3 Active Email Campaigns** with realistic targeting and tracking
- **Campaign Targets** with open/click tracking data
- Templates for various attack types (banking, delivery, Microsoft 365)

### 🎭 Landing Pages
- **Microsoft 365 Login Clone** - Medium difficulty
- **Google Login Clone** - Medium difficulty
- **Chase Bank Login** - Hard difficulty

### 📱 Multi-Vector Campaigns
- **2 QR Code Campaigns** (Quishing) with scan tracking
- **2 SMS Campaigns** (Smishing) with delivery stats

### 🧠 AI & Intelligence
- **4 Phishing Patterns** for AI learning (credential theft, BEC, delivery scams, tech support)
- **3 Threat Feed Entries** with defanged IOCs
- **9+ Threat IOCs** (domains, URLs, IPs)

### 📊 Analytics & Profiling
- **12 User Risk Scores** with realistic click/open rates
- **10 Vulnerability Profiles** with technique susceptibility scores
- **7 Department Vulnerability** profiles
- **5 Age Group Vulnerability** profiles

### 🛡️ Security Operations
- **8 Security Incidents** (various types: clicks, credential submission, malware)
- **8 Email Analyses** (mix of malicious, suspicious, and safe)

## How to Run

### Prerequisites
1. Make sure your backend database is set up
2. Ensure all dependencies are installed

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Run the Seeder
```bash
python seed_demo_data.py
```

### Expected Output
You should see progress messages like:
```
🌱 Starting demo data seeding...
👥 Creating demo employees...
   ✓ Created 21 employees
📝 Creating professional demo templates...
   ✓ Created X professional templates
📧 Creating demo campaigns...
   ✓ Created 3 campaigns with targets
...
✅ Demo data seeding complete!
```

## Demo Login Credentials

After seeding, you can log in with:
- **Username:** `demo`
- **Password:** `demo123`
- **Role:** Admin (full access)

## What You Can Demo

### 1. Dashboard
- View overall statistics
- See recent security incidents
- Check campaign performance

### 2. Email Analyzer
- Test with pre-populated email analyses
- View AI + NLP analysis results
- See threat classifications

### 3. Threat Feed
- Browse community threat intelligence
- View IOCs from malicious emails
- See threat voting and statistics

### 4. Campaign Manager
- View active/completed campaigns
- Check open rates and click rates
- Analyze target interactions

### 5. Employee Risk Dashboard
- See employee vulnerability scores
- Identify high-risk users
- View repeat offenders

### 6. Landing Pages
- See realistic login page clones
- Track credential submission attempts

### 7. QR/SMS Campaigns
- View Quishing campaigns with scan data
- Check Smishing delivery and click stats

### 8. Vulnerability Profiling
- Department-level risk analysis
- Age group susceptibility patterns
- Technique effectiveness scores

## Data Reset

To reset and re-seed the data:
1. Delete your database file (usually `phishvision.db`)
2. Re-run the Flask app to recreate tables
3. Run `python seed_demo_data.py` again

## Sample Employee Emails

Use these emails to test campaigns:
- `john.doe@company.com` - Engineering (High Risk)
- `jane.smith@company.com` - Engineering (High Risk)
- `mike.wilson@company.com` - Engineering (Critical Risk)
- `emily.davis@company.com` - Finance (Low Risk)
- `quinn.lewis@company.com` - IT (Very Low Risk)
- `blake.walker@company.com` - Executive (CEO)

## Customization

Edit `seed_demo_data.py` to:
- Add more employees
- Create custom campaigns
- Add new landing pages
- Adjust risk scores
- Create more threat entries

## Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'builtin_templates'
```
**Solution:** Make sure `builtin_templates.py` exists in the backend directory.

### Database Lock Error
**Solution:** Stop any running Flask instances and try again.

### Missing Fields Error
**Solution:** Ensure your database schema is up to date. Drop and recreate if needed.

## Next Steps

1. ✅ Run the seeder
2. ✅ Log in with demo credentials
3. ✅ Explore the dashboard
4. ✅ Test email analysis
5. ✅ View threat feed
6. ✅ Check campaign stats
7. ✅ Review vulnerability profiles

Enjoy your fully populated PhishVision demo environment! 🎉
