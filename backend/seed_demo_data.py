"""
Demo Data Seeder for PhishVision
Creates realistic sample data for hackathon demonstration
Now includes: Landing Pages, QR Campaigns, SMS Campaigns, Threat Feed,
Phishing Patterns, Vulnerability Profiles, and more!
"""

from app import app
from database import db
from models import (
    Campaign, CampaignTarget, EmailAnalysis, Employee, SecurityIncident,
    UserRiskScore, CustomTemplate, User, Settings, LandingPage, CredentialCapture,
    QRCodeCampaign, QRCodeScan, SMSCampaign, SMSTarget, ThreatEntry, ThreatIOC,
    ThreatVote, PhishingPattern, AnalysisFeedback, VulnerabilityProfile,
    ProfileDataPoint, DepartmentVulnerability, AgeGroupVulnerability,
    CampaignProgram, ProgramPhase, ScheduledCampaign
)
from datetime import datetime, timedelta
from builtin_templates import BUILTIN_TEMPLATES
import uuid
import json
import random
import hashlib

def seed_demo_data():
    with app.app_context():
        print("🌱 Starting demo data seeding...")

        # Seed Employees
        print("👥 Creating demo employees...")
        employees_data = [
            # Engineering Department
            {"email": "john.doe@company.com", "first_name": "John", "last_name": "Doe", "department": "Engineering", "job_title": "Senior Software Engineer"},
            {"email": "jane.smith@company.com", "first_name": "Jane", "last_name": "Smith", "department": "Engineering", "job_title": "Tech Lead"},
            {"email": "mike.wilson@company.com", "first_name": "Mike", "last_name": "Wilson", "department": "Engineering", "job_title": "Junior Developer"},
            {"email": "sarah.johnson@company.com", "first_name": "Sarah", "last_name": "Johnson", "department": "Engineering", "job_title": "DevOps Engineer"},
            {"email": "alex.chen@company.com", "first_name": "Alex", "last_name": "Chen", "department": "Engineering", "job_title": "Full Stack Developer"},

            # Finance Department
            {"email": "david.brown@company.com", "first_name": "David", "last_name": "Brown", "department": "Finance", "job_title": "Financial Analyst"},
            {"email": "emily.davis@company.com", "first_name": "Emily", "last_name": "Davis", "department": "Finance", "job_title": "Accountant"},
            {"email": "robert.miller@company.com", "first_name": "Robert", "last_name": "Miller", "department": "Finance", "job_title": "CFO"},

            # HR Department
            {"email": "lisa.garcia@company.com", "first_name": "Lisa", "last_name": "Garcia", "department": "HR", "job_title": "HR Manager"},
            {"email": "chris.anderson@company.com", "first_name": "Chris", "last_name": "Anderson", "department": "HR", "job_title": "Recruiter"},

            # Marketing Department
            {"email": "pat.thomas@company.com", "first_name": "Pat", "last_name": "Thomas", "department": "Marketing", "job_title": "Marketing Manager"},
            {"email": "morgan.jackson@company.com", "first_name": "Morgan", "last_name": "Jackson", "department": "Marketing", "job_title": "Content Writer"},
            {"email": "jordan.white@company.com", "first_name": "Jordan", "last_name": "White", "department": "Marketing", "job_title": "Social Media Specialist"},

            # Sales Department
            {"email": "casey.harris@company.com", "first_name": "Casey", "last_name": "Harris", "department": "Sales", "job_title": "Sales Representative"},
            {"email": "taylor.martin@company.com", "first_name": "Taylor", "last_name": "Martin", "department": "Sales", "job_title": "Account Executive"},
            {"email": "riley.thompson@company.com", "first_name": "Riley", "last_name": "Thompson", "department": "Sales", "job_title": "Sales Manager"},

            # IT Department
            {"email": "sam.robinson@company.com", "first_name": "Sam", "last_name": "Robinson", "department": "IT", "job_title": "IT Support Specialist"},
            {"email": "avery.clark@company.com", "first_name": "Avery", "last_name": "Clark", "department": "IT", "job_title": "Network Administrator"},
            {"email": "quinn.lewis@company.com", "first_name": "Quinn", "last_name": "Lewis", "department": "IT", "job_title": "Security Analyst"},

            # Executive
            {"email": "blake.walker@company.com", "first_name": "Blake", "last_name": "Walker", "department": "Executive", "job_title": "CEO"},
            {"email": "drew.hall@company.com", "first_name": "Drew", "last_name": "Hall", "department": "Executive", "job_title": "COO"},
        ]

        for emp_data in employees_data:
            existing = Employee.query.filter_by(email=emp_data['email']).first()
            if not existing:
                employee = Employee(
                    id=str(uuid.uuid4()),
                    email=emp_data['email'],
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name'],
                    department=emp_data['department'],
                    job_title=emp_data['job_title'],
                    is_active=True,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
                )
                db.session.add(employee)

        db.session.commit()
        print(f"   ✓ Created {len(employees_data)} employees")

        # Clear existing built-in templates for fresh reload
        print("🗑️ Clearing existing built-in templates...")
        CustomTemplate.query.filter_by(is_builtin=True).delete()
        db.session.commit()

        # Seed Templates from builtin_templates.py
        print("📝 Creating professional demo templates...")
        templates_data = BUILTIN_TEMPLATES

        for template_data in templates_data:
            existing = CustomTemplate.query.filter_by(name=template_data['name']).first()
            if not existing:
                template = CustomTemplate(
                    id=str(uuid.uuid4()),
                    name=template_data['name'],
                    category=template_data['category'],
                    subject=template_data['subject'],
                    html_content=template_data['html_content'],
                    difficulty=template_data['difficulty'],
                    description=template_data['description'],
                    language=template_data['language'],
                    is_builtin=template_data['is_builtin'],
                    is_active=True
                )
                db.session.add(template)

        db.session.commit()
        print(f"   ✓ Created {len(templates_data)} professional templates")

        # Seed Campaigns
        print("📧 Creating demo campaigns...")

        # Campaign 1: Bank Security Alert (High Success - Most Clicked)
        campaign1 = Campaign.query.filter_by(name="Q4 2024 Security Awareness - Banking").first()
        if not campaign1:
            campaign1 = Campaign(
                id=str(uuid.uuid4()),
                name="Q4 2024 Security Awareness - Banking",
                template_type="bank_alert",
                subject="Urgent: Suspicious Activity Detected on Your Account",
                target_emails=json.dumps([
                    "john.doe@company.com", "jane.smith@company.com", "mike.wilson@company.com",
                    "sarah.johnson@company.com", "david.brown@company.com", "emily.davis@company.com",
                    "robert.miller@company.com", "lisa.garcia@company.com"
                ]),
                created_at=datetime.utcnow() - timedelta(days=5),
                status="completed"
            )
            db.session.add(campaign1)
            db.session.flush()

            targets1 = [
                ("john.doe@company.com", True, True),
                ("jane.smith@company.com", True, True),
                ("mike.wilson@company.com", True, True),
                ("sarah.johnson@company.com", True, False),
                ("david.brown@company.com", True, False),
                ("emily.davis@company.com", False, False),
                ("robert.miller@company.com", True, False),
                ("lisa.garcia@company.com", False, False)
            ]

            for email, opened, clicked in targets1:
                target = CampaignTarget(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign1.id,
                    email=email,
                    tracking_token=str(uuid.uuid4()),
                    sent_at=campaign1.created_at,
                    opened_at=campaign1.created_at + timedelta(hours=random.randint(1, 48)) if opened else None,
                    clicked_at=campaign1.created_at + timedelta(hours=random.randint(2, 50)) if clicked else None,
                    ip_address=f"192.168.1.{random.randint(1, 254)}" if opened else None,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" if opened else None
                )
                db.session.add(target)

        # Campaign 2: Package Delivery
        campaign2 = Campaign.query.filter_by(name="November Phishing Simulation - Delivery").first()
        if not campaign2:
            campaign2 = Campaign(
                id=str(uuid.uuid4()),
                name="November Phishing Simulation - Delivery",
                template_type="package_delivery",
                subject="Your Package Delivery Failed - Action Required",
                target_emails=json.dumps([
                    "alex.chen@company.com", "chris.anderson@company.com", "pat.thomas@company.com",
                    "morgan.jackson@company.com", "jordan.white@company.com", "casey.harris@company.com"
                ]),
                created_at=datetime.utcnow() - timedelta(days=3),
                status="active"
            )
            db.session.add(campaign2)
            db.session.flush()

            targets2 = [
                ("alex.chen@company.com", True, True),
                ("chris.anderson@company.com", True, False),
                ("pat.thomas@company.com", True, False),
                ("morgan.jackson@company.com", False, False),
                ("jordan.white@company.com", False, False),
                ("casey.harris@company.com", False, False)
            ]

            for email, opened, clicked in targets2:
                target = CampaignTarget(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign2.id,
                    email=email,
                    tracking_token=str(uuid.uuid4()),
                    sent_at=campaign2.created_at,
                    opened_at=campaign2.created_at + timedelta(hours=random.randint(1, 36)) if opened else None,
                    clicked_at=campaign2.created_at + timedelta(hours=random.randint(2, 40)) if clicked else None,
                    ip_address=f"192.168.1.{random.randint(1, 254)}" if opened else None,
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" if opened else None
                )
                db.session.add(target)

        # Campaign 3: Microsoft 365
        campaign3 = Campaign.query.filter_by(name="IT Security Test - Microsoft 365").first()
        if not campaign3:
            campaign3 = Campaign(
                id=str(uuid.uuid4()),
                name="IT Security Test - Microsoft 365",
                template_type="microsoft_365",
                subject="Action Required: Your Microsoft 365 Password Expires Today",
                target_emails=json.dumps([
                    "taylor.martin@company.com", "riley.thompson@company.com", "sam.robinson@company.com",
                    "avery.clark@company.com", "quinn.lewis@company.com", "blake.walker@company.com"
                ]),
                created_at=datetime.utcnow() - timedelta(days=1),
                status="active"
            )
            db.session.add(campaign3)
            db.session.flush()

            targets3 = [
                ("taylor.martin@company.com", True, True),
                ("riley.thompson@company.com", True, True),
                ("sam.robinson@company.com", True, False),
                ("avery.clark@company.com", True, False),
                ("quinn.lewis@company.com", False, False),
                ("blake.walker@company.com", False, False)
            ]

            for email, opened, clicked in targets3:
                target = CampaignTarget(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign3.id,
                    email=email,
                    tracking_token=str(uuid.uuid4()),
                    sent_at=campaign3.created_at,
                    opened_at=campaign3.created_at + timedelta(hours=random.randint(1, 20)) if opened else None,
                    clicked_at=campaign3.created_at + timedelta(hours=random.randint(2, 22)) if clicked else None,
                    ip_address=f"192.168.1.{random.randint(1, 254)}" if opened else None,
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)" if opened else None
                )
                db.session.add(target)

        db.session.commit()
        print("   ✓ Created 3 campaigns with targets")

        # Seed User Risk Scores
        print("📊 Creating user risk scores...")
        risk_data = [
            {"email": "john.doe@company.com", "department": "Engineering", "score": 75, "received": 5, "opened": 4, "clicked": 3},
            {"email": "jane.smith@company.com", "department": "Engineering", "score": 68, "received": 5, "opened": 3, "clicked": 2},
            {"email": "mike.wilson@company.com", "department": "Engineering", "score": 82, "received": 4, "opened": 4, "clicked": 3},
            {"email": "david.brown@company.com", "department": "Finance", "score": 45, "received": 5, "opened": 3, "clicked": 1},
            {"email": "emily.davis@company.com", "department": "Finance", "score": 25, "received": 5, "opened": 1, "clicked": 0},
            {"email": "lisa.garcia@company.com", "department": "HR", "score": 30, "received": 4, "opened": 2, "clicked": 0},
            {"email": "chris.anderson@company.com", "department": "HR", "score": 55, "received": 4, "opened": 3, "clicked": 1},
            {"email": "pat.thomas@company.com", "department": "Marketing", "score": 48, "received": 3, "opened": 2, "clicked": 1},
            {"email": "taylor.martin@company.com", "department": "Sales", "score": 72, "received": 3, "opened": 3, "clicked": 2},
            {"email": "riley.thompson@company.com", "department": "Sales", "score": 78, "received": 3, "opened": 3, "clicked": 2},
            {"email": "sam.robinson@company.com", "department": "IT", "score": 38, "received": 3, "opened": 2, "clicked": 0},
            {"email": "quinn.lewis@company.com", "department": "IT", "score": 15, "received": 3, "opened": 0, "clicked": 0},
        ]

        for data in risk_data:
            existing = UserRiskScore.query.filter_by(email=data['email']).first()
            if not existing:
                risk_level = 'low' if data['score'] < 25 else ('medium' if data['score'] < 50 else ('high' if data['score'] < 75 else 'critical'))
                risk = UserRiskScore(
                    id=str(uuid.uuid4()),
                    email=data['email'],
                    department=data['department'],
                    risk_score=data['score'],
                    risk_level=risk_level,
                    campaigns_received=data['received'],
                    campaigns_opened=data['opened'],
                    campaigns_clicked=data['clicked'],
                    training_completed=random.randint(0, 3),
                    training_passed=random.randint(0, 2),
                    last_incident_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if data['clicked'] > 0 else None
                )
                db.session.add(risk)

        db.session.commit()
        print(f"   ✓ Created {len(risk_data)} user risk profiles")

        # Seed Security Incidents
        print("🛡️ Creating SOC incidents...")
        incidents_data = [
            {"type": "phishing_click", "severity": "high", "user": "john.doe@company.com", "desc": "User clicked on phishing link in Bank Security Alert campaign", "status": "resolved"},
            {"type": "phishing_click", "severity": "high", "user": "jane.smith@company.com", "desc": "User clicked on malicious link and entered credentials", "status": "resolved"},
            {"type": "credential_entered", "severity": "critical", "user": "mike.wilson@company.com", "desc": "User submitted credentials on fake Microsoft 365 login page", "status": "contained"},
            {"type": "reported_email", "severity": "low", "user": "emily.davis@company.com", "desc": "User correctly reported phishing email to IT security team", "status": "resolved"},
            {"type": "reported_email", "severity": "low", "user": "quinn.lewis@company.com", "desc": "User identified and reported suspicious email", "status": "resolved"},
            {"type": "phishing_click", "severity": "medium", "user": "taylor.martin@company.com", "desc": "User clicked package delivery phishing link", "status": "investigating"},
            {"type": "credential_entered", "severity": "critical", "user": "riley.thompson@company.com", "desc": "Credentials entered on phishing page - password reset initiated", "status": "contained"},
            {"type": "malware_download", "severity": "critical", "user": "alex.chen@company.com", "desc": "User attempted to download attachment from phishing email", "status": "detected"},
        ]

        for i, data in enumerate(incidents_data):
            existing = SecurityIncident.query.filter_by(user_email=data['user'], type=data['type']).first()
            if not existing:
                detected = datetime.utcnow() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                incident = SecurityIncident(
                    id=str(uuid.uuid4()),
                    type=data['type'],
                    severity=data['severity'],
                    description=data['desc'],
                    user_email=data['user'],
                    detected_at=detected,
                    acknowledged_at=detected + timedelta(minutes=random.randint(5, 60)) if data['status'] != 'detected' else None,
                    contained_at=detected + timedelta(hours=random.randint(1, 4)) if data['status'] in ['contained', 'resolved'] else None,
                    resolved_at=detected + timedelta(hours=random.randint(2, 24)) if data['status'] == 'resolved' else None,
                    status=data['status'],
                    assigned_to="security-team@company.com"
                )
                db.session.add(incident)

        db.session.commit()
        print(f"   ✓ Created {len(incidents_data)} security incidents")

        # Seed Email Analyses
        print("🔍 Creating email analyses...")
        analyses = [
            {"from": "security@paypa1-verify.com", "subject": "Your PayPal Account Has Been Limited", "score": 95, "class": "malicious"},
            {"from": "admin@company-portal.tk", "subject": "IT: Password Expiration Notice", "score": 88, "class": "malicious"},
            {"from": "prize@winner-notification.info", "subject": "Congratulations! You've Won $10,000", "score": 92, "class": "malicious"},
            {"from": "noreply@microsoft-update.com", "subject": "Microsoft Office Update Available", "score": 65, "class": "suspicious"},
            {"from": "hr@company.co", "subject": "Employee Benefits Survey", "score": 55, "class": "suspicious"},
            {"from": "notifications@github.com", "subject": "Your pull request was merged", "score": 15, "class": "safe"},
            {"from": "calendar@google.com", "subject": "Reminder: Team Meeting at 3 PM", "score": 10, "class": "safe"},
            {"from": "support@slack.com", "subject": "New message in #engineering", "score": 12, "class": "safe"},
        ]

        for data in analyses:
            existing = EmailAnalysis.query.filter_by(email_subject=data['subject']).first()
            if not existing:
                analysis = EmailAnalysis(
                    id=str(uuid.uuid4()),
                    email_from=data['from'],
                    email_subject=data['subject'],
                    email_body=f"Sample email body for {data['subject']}",
                    headers="",
                    risk_score=data['score'],
                    classification=data['class'],
                    spf_status="fail" if data['class'] == "malicious" else ("none" if data['class'] == "suspicious" else "pass"),
                    dkim_status="fail" if data['class'] == "malicious" else ("none" if data['class'] == "suspicious" else "pass"),
                    dmarc_status="fail" if data['class'] == "malicious" else ("none" if data['class'] == "suspicious" else "pass"),
                    urgency_score=0.9 if data['class'] == "malicious" else (0.5 if data['class'] == "suspicious" else 0.1),
                    explanation=f"Analysis for {data['class']} email from {data['from']}",
                    recommendations=json.dumps(["Report to IT", "Do not click links"]),
                    analyzed_at=datetime.utcnow() - timedelta(days=random.randint(0, 6))
                )
                db.session.add(analysis)

        db.session.commit()
        print(f"   ✓ Created {len(analyses)} email analyses")

        # Seed Demo Users
        print("👤 Creating demo users...")
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            demo_user = User(
                id=str(uuid.uuid4()),
                username='demo',
                email='demo@phishvision.com',
                first_name='Demo',
                last_name='User',
                role='admin',
                is_active=True
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
            print("   ✓ Created demo user (username: demo, password: demo123)")

        # Seed Landing Pages
        print("🎭 Creating landing pages...")
        landing_pages = [
            {
                "name": "Microsoft 365 Login Clone",
                "category": "microsoft",
                "description": "Realistic Microsoft 365 login page for phishing simulation",
                "html_content": """<!DOCTYPE html>
<html><head><title>Sign in to your Microsoft account</title></head>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f3f3f3; display: flex; justify-content: center; align-items: center; height: 100vh;">
<div style="background: white; padding: 40px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 400px;">
<img src="https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg" style="width: 120px; margin-bottom: 30px;">
<h2 style="margin-bottom: 20px;">Sign in</h2>
<form method="POST" action="/landing/submit">
<input type="email" name="username" placeholder="Email, phone, or Skype" required style="width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 2px;">
<input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 2px;">
<button type="submit" style="width: 100%; padding: 12px; background: #0067b8; color: white; border: none; border-radius: 2px; cursor: pointer;">Sign in</button>
</form>
</div></body></html>""",
                "redirect_url": "https://www.microsoft.com",
                "capture_fields": '["username", "password"]',
                "difficulty": "medium"
            },
            {
                "name": "Google Login Clone",
                "category": "google",
                "description": "Google account login page replica",
                "html_content": """<!DOCTYPE html>
<html><head><title>Sign in - Google Accounts</title></head>
<body style="font-family: 'Roboto', Arial, sans-serif; background: white; display: flex; justify-content: center; align-items: center; height: 100vh;">
<div style="border: 1px solid #dadce0; padding: 48px 40px; border-radius: 8px; width: 400px;">
<img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" style="width: 92px; margin-bottom: 20px;">
<h1 style="font-size: 24px; font-weight: 400; margin-bottom: 8px;">Sign in</h1>
<p style="color: #5f6368; margin-bottom: 30px;">to continue to Gmail</p>
<form method="POST" action="/landing/submit">
<input type="email" name="username" placeholder="Email or phone" required style="width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid #dadce0; border-radius: 4px;">
<input type="password" name="password" placeholder="Enter your password" required style="width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid #dadce0; border-radius: 4px;">
<button type="submit" style="width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500;">Next</button>
</form>
</div></body></html>""",
                "redirect_url": "https://www.google.com",
                "capture_fields": '["username", "password"]',
                "difficulty": "medium"
            },
            {
                "name": "Chase Bank Login",
                "category": "banking",
                "description": "Chase online banking login page",
                "html_content": """<!DOCTYPE html>
<html><head><title>Chase Online | Logon</title></head>
<body style="font-family: Arial, sans-serif; background: #f7f7f7; display: flex; justify-content: center; align-items: center; height: 100vh;">
<div style="background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); width: 380px;">
<h2 style="color: #117aca; margin-bottom: 30px;">Chase Online</h2>
<form method="POST" action="/landing/submit">
<label style="display: block; margin-bottom: 8px; font-weight: bold;">Username</label>
<input type="text" name="username" required style="width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 4px;">
<label style="display: block; margin-bottom: 8px; font-weight: bold;">Password</label>
<input type="password" name="password" required style="width: 100%; padding: 10px; margin-bottom: 25px; border: 1px solid #ccc; border-radius: 4px;">
<button type="submit" style="width: 100%; padding: 12px; background: #117aca; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Sign In</button>
</form>
</div></body></html>""",
                "redirect_url": "https://www.chase.com",
                "capture_fields": '["username", "password"]',
                "difficulty": "hard"
            }
        ]

        for lp_data in landing_pages:
            existing = LandingPage.query.filter_by(name=lp_data['name']).first()
            if not existing:
                landing_page = LandingPage(
                    id=str(uuid.uuid4()),
                    name=lp_data['name'],
                    category=lp_data['category'],
                    description=lp_data['description'],
                    html_content=lp_data['html_content'],
                    redirect_url=lp_data['redirect_url'],
                    capture_fields=lp_data['capture_fields'],
                    is_builtin=True,
                    is_active=True,
                    difficulty=lp_data['difficulty']
                )
                db.session.add(landing_page)

        db.session.commit()
        print(f"   ✓ Created {len(landing_pages)} landing pages")

        # Seed QR Code Campaigns
        print("📱 Creating QR code campaigns...")
        qr_campaigns = [
            {
                "name": "WiFi Password QR - Break Room",
                "description": "Fake WiFi password QR code placed in office break room",
                "target_url": "https://phishing.example.com/wifi-setup?token=abc123",
                "placement_location": "Break Room - Wall",
                "total_scans": 12,
                "unique_scans": 8
            },
            {
                "name": "Employee Survey QR",
                "description": "QR code directing to fake employee satisfaction survey",
                "target_url": "https://phishing.example.com/survey?id=emp2024",
                "placement_location": "Main Entrance Poster",
                "total_scans": 25,
                "unique_scans": 18
            }
        ]

        for qr_data in qr_campaigns:
            existing = QRCodeCampaign.query.filter_by(name=qr_data['name']).first()
            if not existing:
                qr_campaign = QRCodeCampaign(
                    id=str(uuid.uuid4()),
                    name=qr_data['name'],
                    description=qr_data['description'],
                    target_url=qr_data['target_url'],
                    placement_location=qr_data['placement_location'],
                    status='active',
                    total_scans=qr_data['total_scans'],
                    unique_scans=qr_data['unique_scans'],
                    created_at=datetime.utcnow() - timedelta(days=random.randint(7, 30)),
                    expires_at=datetime.utcnow() + timedelta(days=30)
                )
                db.session.add(qr_campaign)
                db.session.flush()

                # Add some scan records
                for i in range(qr_data['total_scans']):
                    scan = QRCodeScan(
                        id=str(uuid.uuid4()),
                        campaign_id=qr_campaign.id,
                        ip_address=f"192.168.1.{random.randint(1, 254)}",
                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)",
                        device_type=random.choice(['mobile', 'tablet']),
                        submitted_credentials=random.choice([True, False]),
                        scanned_at=qr_campaign.created_at + timedelta(days=random.randint(0, 20))
                    )
                    db.session.add(scan)

        db.session.commit()
        print(f"   ✓ Created {len(qr_campaigns)} QR code campaigns")

        # Seed SMS Campaigns
        print("💬 Creating SMS campaigns...")
        sms_campaigns = [
            {
                "name": "Package Delivery Alert",
                "description": "Fake package delivery SMS with tracking link",
                "message_template": "Your package will arrive today. Track here: {{url}}",
                "sender_id": "USPS",
                "target_url": "https://phishing.example.com/track/{{token}}",
                "status": "completed",
                "total_sent": 15,
                "total_delivered": 14,
                "total_clicked": 6
            },
            {
                "name": "IT Security Alert",
                "description": "Urgent IT security warning SMS",
                "message_template": "URGENT: Your company account will be locked in 24hrs. Verify now: {{url}}",
                "sender_id": "IT-Security",
                "target_url": "https://phishing.example.com/verify/{{token}}",
                "status": "active",
                "total_sent": 20,
                "total_delivered": 19,
                "total_clicked": 8
            }
        ]

        for sms_data in sms_campaigns:
            existing = SMSCampaign.query.filter_by(name=sms_data['name']).first()
            if not existing:
                sms_campaign = SMSCampaign(
                    id=str(uuid.uuid4()),
                    name=sms_data['name'],
                    description=sms_data['description'],
                    message_template=sms_data['message_template'],
                    sender_id=sms_data['sender_id'],
                    target_url=sms_data['target_url'],
                    status=sms_data['status'],
                    total_sent=sms_data['total_sent'],
                    total_delivered=sms_data['total_delivered'],
                    total_clicked=sms_data['total_clicked'],
                    created_at=datetime.utcnow() - timedelta(days=random.randint(3, 15))
                )
                db.session.add(sms_campaign)

        db.session.commit()
        print(f"   ✓ Created {len(sms_campaigns)} SMS campaigns")

        # Seed Phishing Patterns
        print("🧠 Creating phishing patterns for AI learning...")
        patterns = [
            {
                "pattern_type": "credential_theft",
                "example_subject": "Your account has been compromised - Verify now",
                "example_body_snippet": "We detected unusual activity. Click here to verify your identity.",
                "example_sender_pattern": "*@account-security-*.com",
                "indicators": '["urgency_language", "verify_credentials", "suspicious_domain", "threat_of_lockout"]',
                "tactics": '{"urgency": true, "fear": true, "authority": false}',
                "source": "threat_intel",
                "language": "en",
                "effectiveness_score": 85.0,
                "detection_count": 45
            },
            {
                "pattern_type": "delivery_scam",
                "example_subject": "Your package could not be delivered",
                "example_body_snippet": "Failed delivery attempt. Reschedule: [link]",
                "example_sender_pattern": "*@delivery-*.info",
                "indicators": '["delivery_urgency", "tracking_request", "shortened_url", "free_domain"]',
                "tactics": '{"urgency": true, "curiosity": true}',
                "source": "threat_intel",
                "language": "en",
                "effectiveness_score": 78.0,
                "detection_count": 32
            },
            {
                "pattern_type": "bec",
                "example_subject": "Urgent wire transfer needed",
                "example_body_snippet": "Please process this payment immediately. I'm in a meeting.",
                "example_sender_pattern": "ceo@*",
                "indicators": '["executive_impersonation", "urgent_payment", "meeting_excuse", "wire_transfer"]',
                "tactics": '{"authority": true, "urgency": true}',
                "source": "threat_intel",
                "language": "en",
                "effectiveness_score": 92.0,
                "detection_count": 18
            },
            {
                "pattern_type": "tech_support_scam",
                "example_subject": "Your Microsoft 365 subscription is expiring",
                "example_body_snippet": "Renew your subscription to avoid service interruption.",
                "example_sender_pattern": "*@microsoft-*.com",
                "indicators": '["brand_impersonation", "subscription_threat", "fake_renewal", "lookalike_domain"]',
                "tactics": '{"fear": true, "urgency": true}',
                "source": "ai_generated",
                "language": "en",
                "effectiveness_score": 71.0,
                "detection_count": 28
            }
        ]

        for pattern_data in patterns:
            existing = PhishingPattern.query.filter_by(
                pattern_type=pattern_data['pattern_type'],
                example_subject=pattern_data['example_subject']
            ).first()
            if not existing:
                pattern = PhishingPattern(
                    id=str(uuid.uuid4()),
                    pattern_type=pattern_data['pattern_type'],
                    example_subject=pattern_data['example_subject'],
                    example_body_snippet=pattern_data['example_body_snippet'],
                    example_sender_pattern=pattern_data['example_sender_pattern'],
                    indicators=pattern_data['indicators'],
                    tactics=pattern_data['tactics'],
                    source=pattern_data['source'],
                    language=pattern_data['language'],
                    effectiveness_score=pattern_data['effectiveness_score'],
                    detection_count=pattern_data['detection_count'],
                    is_active=True,
                    confidence_level='high'
                )
                db.session.add(pattern)

        db.session.commit()
        print(f"   ✓ Created {len(patterns)} phishing patterns")

        # Seed Threat Feed Entries
        print("🌐 Creating threat intelligence entries...")
        threat_entries = [
            {
                "sanitized_subject": "Urgent: Your PayPal account has been limited",
                "risk_score": 95.0,
                "classification": "malicious",
                "threat_type": "credential_theft",
                "detected_brands": '["PayPal"]',
                "detected_tactics": '["urgency", "fear", "account_threat"]',
                "iocs": [
                    {"type": "domain", "value": "paypa1-verify[.]com", "context": "sender domain"},
                    {"type": "url", "value": "hxxp://paypa1-verify[.]com/secure/login", "context": "phishing link"},
                    {"type": "email_pattern", "value": "*@paypa1-verify.com", "context": "sender pattern"}
                ]
            },
            {
                "sanitized_subject": "Your Microsoft 365 password expires today",
                "risk_score": 88.0,
                "classification": "malicious",
                "threat_type": "credential_theft",
                "detected_brands": '["Microsoft"]',
                "detected_tactics": '["urgency", "authority", "deadline"]',
                "iocs": [
                    {"type": "domain", "value": "microsoft-update[.]tk", "context": "sender domain"},
                    {"type": "url", "value": "hxxp://microsoft-update[.]tk/renew", "context": "phishing link"},
                    {"type": "ip", "value": "185[.]234[.]219[.]45", "context": "hosting server"}
                ]
            },
            {
                "sanitized_subject": "Package delivery failure - Action required",
                "risk_score": 82.0,
                "classification": "malicious",
                "threat_type": "delivery_scam",
                "detected_brands": '["FedEx", "UPS"]',
                "detected_tactics": '["urgency", "curiosity"]',
                "iocs": [
                    {"type": "domain", "value": "fedex-tracking[.]info", "context": "sender domain"},
                    {"type": "url", "value": "hxxp://bit[.]ly/3xYz123", "context": "shortened tracking link"},
                    {"type": "sender_domain", "value": "delivery-tracking[.]info", "context": "From header"}
                ]
            }
        ]

        for threat_data in threat_entries:
            # Create unique hash
            threat_hash = hashlib.sha256(
                (threat_data['sanitized_subject'] + str(threat_data['risk_score'])).encode()
            ).hexdigest()
            short_id = str(uuid.uuid4())[:12]

            existing = ThreatEntry.query.filter_by(threat_hash=threat_hash).first()
            if not existing:
                threat_entry = ThreatEntry(
                    id=str(uuid.uuid4()),
                    threat_hash=threat_hash,
                    short_id=short_id,
                    sanitized_subject=threat_data['sanitized_subject'],
                    risk_score=threat_data['risk_score'],
                    classification=threat_data['classification'],
                    threat_type=threat_data['threat_type'],
                    detected_brands=threat_data['detected_brands'],
                    detected_tactics=threat_data['detected_tactics'],
                    is_anonymous=True,
                    submission_source='web',
                    view_count=random.randint(10, 100),
                    community_votes_phishing=random.randint(5, 25),
                    community_votes_safe=random.randint(0, 3),
                    similar_submissions=random.randint(1, 5),
                    first_seen=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    last_seen=datetime.utcnow() - timedelta(days=random.randint(0, 5))
                )
                db.session.add(threat_entry)
                db.session.flush()

                # Add IOCs
                for ioc_data in threat_data['iocs']:
                    ioc_hash = hashlib.sha256(ioc_data['value'].encode()).hexdigest()
                    ioc = ThreatIOC(
                        id=str(uuid.uuid4()),
                        threat_entry_id=threat_entry.id,
                        ioc_type=ioc_data['type'],
                        ioc_value=ioc_data['value'],
                        ioc_hash=ioc_hash,
                        context=ioc_data['context'],
                        is_defanged=True,
                        ioc_risk_score=threat_data['risk_score'],
                        global_occurrence_count=random.randint(1, 10)
                    )
                    db.session.add(ioc)

        db.session.commit()
        print(f"   ✓ Created {len(threat_entries)} threat intelligence entries")

        # Seed Vulnerability Profiles
        print("📊 Creating vulnerability profiles...")
        employees = Employee.query.limit(10).all()
        for employee in employees:
            existing = VulnerabilityProfile.query.filter_by(employee_id=employee.id).first()
            if not existing:
                profile = VulnerabilityProfile(
                    id=str(uuid.uuid4()),
                    employee_id=employee.id,
                    overall_vulnerability_score=random.uniform(20, 80),
                    email_phishing_score=random.uniform(30, 90),
                    spear_phishing_score=random.uniform(35, 85),
                    qr_phishing_score=random.uniform(25, 75),
                    sms_phishing_score=random.uniform(30, 80),
                    urgency_susceptibility=random.uniform(40, 90),
                    authority_susceptibility=random.uniform(35, 85),
                    curiosity_susceptibility=random.uniform(30, 80),
                    fear_susceptibility=random.uniform(45, 95),
                    reward_susceptibility=random.uniform(25, 70),
                    social_proof_susceptibility=random.uniform(30, 75),
                    total_campaigns_received=random.randint(5, 15),
                    total_emails_opened=random.randint(2, 10),
                    total_links_clicked=random.randint(0, 5),
                    total_credentials_submitted=random.randint(0, 2),
                    total_reported_correctly=random.randint(0, 3),
                    data_points_count=random.randint(5, 20),
                    profile_confidence=random.uniform(50, 95)
                )
                profile.calculate_risk_level()
                profile.find_weakest_areas()
                db.session.add(profile)

        db.session.commit()
        print(f"   ✓ Created vulnerability profiles for employees")

        # Seed Department Vulnerabilities
        print("🏢 Creating department vulnerability analytics...")
        departments = ['Engineering', 'Finance', 'HR', 'Marketing', 'Sales', 'IT', 'Executive']
        for dept in departments:
            existing = DepartmentVulnerability.query.filter_by(department=dept).first()
            if not existing:
                dept_vuln = DepartmentVulnerability(
                    id=str(uuid.uuid4()),
                    department=dept,
                    avg_vulnerability_score=random.uniform(35, 75),
                    employee_count=Employee.query.filter_by(department=dept).count(),
                    profiled_employee_count=Employee.query.filter_by(department=dept).count(),
                    high_risk_count=random.randint(0, 3),
                    email_phishing_avg=random.uniform(40, 80),
                    spear_phishing_avg=random.uniform(45, 85),
                    qr_phishing_avg=random.uniform(30, 70),
                    sms_phishing_avg=random.uniform(35, 75),
                    urgency_avg=random.uniform(45, 90),
                    authority_avg=random.uniform(40, 85),
                    curiosity_avg=random.uniform(35, 75),
                    fear_avg=random.uniform(50, 95),
                    reward_avg=random.uniform(30, 70),
                    social_proof_avg=random.uniform(35, 75),
                    total_campaigns=random.randint(3, 10),
                    overall_click_rate=random.uniform(15, 45),
                    overall_submission_rate=random.uniform(5, 20),
                    trend=random.choice(['improving', 'stable', 'declining'])
                )
                db.session.add(dept_vuln)

        db.session.commit()
        print(f"   ✓ Created {len(departments)} department vulnerability profiles")

        # Seed Age Group Vulnerabilities
        print("👥 Creating age group vulnerability analytics...")
        age_groups = ['18-25', '26-35', '36-45', '46-55', '56+']
        for age_group in age_groups:
            existing = AgeGroupVulnerability.query.filter_by(age_group=age_group).first()
            if not existing:
                age_vuln = AgeGroupVulnerability(
                    id=str(uuid.uuid4()),
                    age_group=age_group,
                    employee_count=random.randint(3, 8),
                    avg_vulnerability_score=random.uniform(30, 80),
                    email_susceptibility=random.uniform(35, 85),
                    qr_susceptibility=random.uniform(25, 75),
                    sms_susceptibility=random.uniform(30, 80),
                    urgency_effectiveness=random.uniform(40, 90),
                    authority_effectiveness=random.uniform(35, 85),
                    curiosity_effectiveness=random.uniform(30, 80),
                    fear_effectiveness=random.uniform(45, 95),
                    reward_effectiveness=random.uniform(25, 70),
                    social_proof_effectiveness=random.uniform(30, 75),
                    avg_response_time_seconds=random.uniform(300, 3600),
                    click_rate=random.uniform(10, 50),
                    credential_submission_rate=random.uniform(5, 25)
                )
                db.session.add(age_vuln)

        db.session.commit()
        print(f"   ✓ Created {len(age_groups)} age group vulnerability profiles")

        print("\n✅ Demo data seeding complete!")
        print("=" * 60)
        print("Summary:")
        print(f"  👥 Employees: {Employee.query.count()}")
        print(f"  📝 Templates: {CustomTemplate.query.count()}")
        print(f"  📧 Email Campaigns: {Campaign.query.count()}")
        print(f"  🎯 Campaign Targets: {CampaignTarget.query.count()}")
        print(f"  🎭 Landing Pages: {LandingPage.query.count()}")
        print(f"  📱 QR Code Campaigns: {QRCodeCampaign.query.count()}")
        print(f"  💬 SMS Campaigns: {SMSCampaign.query.count()}")
        print(f"  📊 User Risk Profiles: {UserRiskScore.query.count()}")
        print(f"  🧠 Phishing Patterns: {PhishingPattern.query.count()}")
        print(f"  🌐 Threat Entries: {ThreatEntry.query.count()}")
        print(f"  🔍 Threat IOCs: {ThreatIOC.query.count()}")
        print(f"  👤 Vulnerability Profiles: {VulnerabilityProfile.query.count()}")
        print(f"  🏢 Department Vulnerabilities: {DepartmentVulnerability.query.count()}")
        print(f"  👥 Age Group Vulnerabilities: {AgeGroupVulnerability.query.count()}")
        print(f"  🛡️ Security Incidents: {SecurityIncident.query.count()}")
        print(f"  🔍 Email Analyses: {EmailAnalysis.query.count()}")
        print("=" * 60)
        print("\n🎯 Your PhishVision demo environment is fully loaded!")
        print("\n📌 Demo Login Credentials:")
        print("   Username: demo")
        print("   Password: demo123")
        print("\n💡 You now have:")
        print("   ✓ Complete employee database")
        print("   ✓ Active phishing campaigns")
        print("   ✓ Landing pages for credential harvesting")
        print("   ✓ QR and SMS phishing campaigns")
        print("   ✓ Threat intelligence feed")
        print("   ✓ Vulnerability profiles and analytics")
        print("   ✓ Security incidents timeline")
        print("=" * 60)

if __name__ == '__main__':
    seed_demo_data()
