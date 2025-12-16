"""
Seed Threat Feed with sample phishing threats
Creates ThreatEntry records from archive data and existing analyses
"""

import csv
import re
import json
import hashlib
import uuid
import random
import string
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import ThreatEntry, ThreatIOC, EmailAnalysis

ARCHIVE_PATH = '/home/morpho/Desktop/archive'


def generate_short_id(length=10):
    """Generate URL-friendly short ID like 'abc123def'"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_threat_hash(subject, body, sender=''):
    """Generate unique hash for deduplication"""
    content = f"{subject}{body[:500]}{sender}".lower()
    return hashlib.sha256(content.encode()).hexdigest()


def extract_urls(text):
    """Extract URLs from text"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return list(set(re.findall(url_pattern, text, re.IGNORECASE)))[:10]


def extract_domains(text):
    """Extract domains from text"""
    # From URLs
    urls = extract_urls(text)
    domains = set()
    for url in urls:
        match = re.search(r'https?://([^/]+)', url)
        if match:
            domains.add(match.group(1).lower())

    # From email addresses
    emails = re.findall(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    domains.update(e.lower() for e in emails)

    return list(domains)[:10]


def extract_ips(text):
    """Extract IP addresses from text"""
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ips = re.findall(ip_pattern, text)
    # Filter out obvious non-IPs
    valid_ips = [ip for ip in ips if all(0 <= int(octet) <= 255 for octet in ip.split('.'))]
    return list(set(valid_ips))[:5]


def defang_url(url):
    """Defang URL for safe display"""
    return url.replace('http://', 'hxxp://').replace('https://', 'hxxps://').replace('.', '[.]')


def defang_domain(domain):
    """Defang domain for safe display"""
    return domain.replace('.', '[.]')


def sanitize_subject(subject):
    """Remove PII from subject but keep brand names"""
    if not subject:
        return "Suspicious Email"

    # Remove email addresses
    subject = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', subject)
    # Remove names (simple pattern - words before common patterns)
    subject = re.sub(r'^(Dear|Hello|Hi)\s+[A-Z][a-z]+,?\s*', '', subject)

    return subject[:200].strip() or "Suspicious Email"


def detect_brands(text):
    """Detect impersonated brands"""
    text_lower = text.lower()
    brands = []

    brand_keywords = {
        'amazon': ['amazon', 'aws', 'prime'],
        'paypal': ['paypal'],
        'apple': ['apple', 'itunes', 'icloud', 'app store'],
        'microsoft': ['microsoft', 'outlook', 'office365', 'azure'],
        'google': ['google', 'gmail', 'youtube'],
        'netflix': ['netflix'],
        'facebook': ['facebook', 'meta', 'instagram'],
        'bank_of_america': ['bank of america', 'bofa'],
        'chase': ['chase', 'jpmorgan'],
        'wells_fargo': ['wells fargo'],
        'usps': ['usps', 'postal service'],
        'fedex': ['fedex'],
        'ups': ['ups'],
        'dhl': ['dhl']
    }

    for brand, keywords in brand_keywords.items():
        if any(kw in text_lower for kw in keywords):
            brands.append(brand)

    return brands[:5]


def detect_tactics(text):
    """Detect social engineering tactics"""
    text_lower = text.lower()
    tactics = []

    if any(w in text_lower for w in ['urgent', 'immediately', 'now', '24 hours', '48 hours']):
        tactics.append('urgency')
    if any(w in text_lower for w in ['suspended', 'locked', 'compromised', 'unauthorized']):
        tactics.append('fear')
    if any(w in text_lower for w in ['official', 'security', 'team', 'department']):
        tactics.append('authority')
    if any(w in text_lower for w in ['winner', 'prize', 'million', 'inheritance']):
        tactics.append('greed')
    if any(w in text_lower for w in ['verify', 'confirm', 'update account']):
        tactics.append('trust')

    return tactics


def detect_threat_type(text, subject=''):
    """Detect threat type"""
    combined = (text + ' ' + subject).lower()

    if any(w in combined for w in ['password', 'verify', 'confirm account', 'login', 'credentials']):
        return 'credential_theft'
    elif any(w in combined for w in ['inheritance', 'million', 'lottery', 'winner']):
        return 'advance_fee_fraud'
    elif any(w in combined for w in ['invoice', 'payment', 'wire transfer']):
        return 'bec'
    elif any(w in combined for w in ['package', 'delivery', 'shipment']):
        return 'delivery_scam'
    else:
        return 'phishing'


def create_threat_from_data(subject, body, sender='', risk_score=75.0):
    """Create a ThreatEntry from email data"""

    threat_hash = generate_threat_hash(subject, body, sender)

    # Check for duplicate
    existing = ThreatEntry.query.filter_by(threat_hash=threat_hash).first()
    if existing:
        existing.similar_submissions += 1
        existing.last_seen = datetime.utcnow()
        return None

    # Extract IOCs
    urls = extract_urls(body)
    domains = extract_domains(body + ' ' + sender)
    ips = extract_ips(body)

    # Create threat entry
    threat = ThreatEntry(
        threat_hash=threat_hash,
        short_id=generate_short_id(),
        is_anonymous=random.choice([True, False]),
        submission_source='threat_intel',
        risk_score=risk_score,
        classification='malicious' if risk_score >= 70 else 'suspicious',
        sanitized_subject=sanitize_subject(subject),
        detected_tactics=json.dumps(detect_tactics(body)),
        detected_brands=json.dumps(detect_brands(body + ' ' + subject)),
        threat_type=detect_threat_type(body, subject),
        view_count=random.randint(5, 100),
        community_votes_phishing=random.randint(3, 20),
        community_votes_safe=random.randint(0, 2),
        similar_submissions=random.randint(1, 5),
        first_seen=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        last_seen=datetime.utcnow() - timedelta(hours=random.randint(0, 48))
    )

    db.session.add(threat)
    db.session.flush()  # Get the ID

    # Create IOCs
    for url in urls[:3]:
        ioc = ThreatIOC(
            threat_entry_id=threat.id,
            ioc_type='url',
            ioc_value=defang_url(url),
            ioc_hash=hashlib.sha256(url.encode()).hexdigest(),
            context='found in body',
            is_defanged=True,
            global_occurrence_count=random.randint(1, 50)
        )
        db.session.add(ioc)

    for domain in domains[:3]:
        ioc = ThreatIOC(
            threat_entry_id=threat.id,
            ioc_type='domain',
            ioc_value=defang_domain(domain),
            ioc_hash=hashlib.sha256(domain.encode()).hexdigest(),
            context='extracted from email',
            is_defanged=True,
            global_occurrence_count=random.randint(1, 100)
        )
        db.session.add(ioc)

    for ip in ips[:2]:
        ioc = ThreatIOC(
            threat_entry_id=threat.id,
            ioc_type='ip',
            ioc_value=ip,
            ioc_hash=hashlib.sha256(ip.encode()).hexdigest(),
            context='found in headers',
            is_defanged=False,
            global_occurrence_count=random.randint(1, 30)
        )
        db.session.add(ioc)

    # Add sender domain as IOC
    if sender and '@' in sender:
        sender_domain = sender.split('@')[-1].split('>')[0]
        if sender_domain:
            ioc = ThreatIOC(
                threat_entry_id=threat.id,
                ioc_type='sender_domain',
                ioc_value=f'*@{defang_domain(sender_domain)}',
                ioc_hash=hashlib.sha256(sender_domain.encode()).hexdigest(),
                context='sender domain',
                is_defanged=True,
                global_occurrence_count=random.randint(1, 20)
            )
            db.session.add(ioc)

    return threat


def seed_from_existing_analyses():
    """Create threats from existing EmailAnalysis records"""
    print("Creating threats from existing analyses...")

    analyses = EmailAnalysis.query.filter(
        EmailAnalysis.classification.in_(['malicious', 'suspicious'])
    ).limit(20).all()

    created = 0
    for analysis in analyses:
        threat = create_threat_from_data(
            subject=analysis.email_subject,
            body=analysis.email_body,
            sender=analysis.email_from,
            risk_score=analysis.risk_score
        )
        if threat:
            threat.source_analysis_id = analysis.id
            created += 1

    db.session.commit()
    print(f"  Created {created} threats from existing analyses")
    return created


def seed_from_nigerian_fraud():
    """Create threats from Nigerian fraud dataset"""
    print("Creating threats from Nigerian Fraud dataset...")

    filepath = os.path.join(ARCHIVE_PATH, 'Nigerian_Fraud.csv')
    created = 0

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader):
                if i >= 50:  # Limit to 50
                    break

                subject = row.get('subject', '')
                body = row.get('body', '')
                sender = row.get('sender', '')

                if not subject or not body:
                    continue

                threat = create_threat_from_data(
                    subject=subject,
                    body=body,
                    sender=sender,
                    risk_score=random.uniform(80, 95)
                )

                if threat:
                    created += 1

                if created % 10 == 0:
                    db.session.commit()

        db.session.commit()
        print(f"  Created {created} threats from Nigerian Fraud")

    except Exception as e:
        print(f"  Error: {e}")
        db.session.rollback()

    return created


def seed_sample_threats():
    """Create some hand-crafted sample threats for demo"""
    print("Creating sample threats for demo...")

    samples = [
        {
            'subject': 'Your Amazon Account Has Been Suspended',
            'body': '''Dear Valued Customer,

We have detected unusual activity on your Amazon account. Your account has been temporarily suspended.

To restore access, please verify your information immediately by clicking the link below:

http://amaz0n-verify.suspicious-domain.tk/login

You have 24 hours to complete this verification or your account will be permanently closed.

Amazon Security Team''',
            'sender': 'security@amaz0n-alerts.tk',
            'risk_score': 92.0
        },
        {
            'subject': 'PayPal: Confirm Your Identity',
            'body': '''Hello,

We noticed someone tried to access your PayPal account from a new device.

If this wasn't you, please secure your account immediately:
https://paypa1-secure.phishing-site.ru/verify

Failure to verify within 48 hours will result in account limitations.

PayPal Security''',
            'sender': 'noreply@paypa1-service.ru',
            'risk_score': 88.5
        },
        {
            'subject': 'URGENT: Wire Transfer Request',
            'body': '''Hi,

I need you to process an urgent wire transfer today. I'm in a meeting and can't call.

Please wire $15,000 to the following account:
Bank: First National
Account: 1234567890
Routing: 021000021

This is time-sensitive. Let me know when done.

Thanks,
CEO''',
            'sender': 'ceo.name@company-mail.net',
            'risk_score': 85.0
        },
        {
            'subject': 'Apple ID Locked - Action Required',
            'body': '''Dear Apple Customer,

Your Apple ID has been locked for security reasons.

Someone attempted to sign in to your account from an unrecognized device.

Verify your identity now: http://appleid-verify.suspicious.com/unlock

If you don't verify within 24 hours, your account will be disabled.

Apple Support''',
            'sender': 'support@apple-id-verify.net',
            'risk_score': 90.0
        },
        {
            'subject': 'FedEx: Your Package Could Not Be Delivered',
            'body': '''Dear Customer,

We attempted to deliver your package but no one was available.

Track your package and schedule redelivery:
http://fedex-tracking.malware-site.xyz/track?id=123456

Package ID: FX789012345
Delivery Fee: $2.99

FedEx Delivery Team''',
            'sender': 'delivery@fedex-notifications.xyz',
            'risk_score': 78.0
        },
        {
            'subject': 'Netflix: Payment Failed',
            'body': '''Your Netflix membership is on hold.

We were unable to process your payment. Update your payment information to continue watching.

Update Payment: http://netflix-billing.fake-site.tk/update

Your account will be canceled if not updated within 7 days.

Netflix Team''',
            'sender': 'billing@netflix-support.tk',
            'risk_score': 82.0
        },
        {
            'subject': 'Microsoft 365: Password Expiring',
            'body': '''Your Microsoft 365 password will expire in 24 hours.

To avoid losing access to your email and files, update your password now:

https://microsoft365-login.phishing.com/password-reset

IT Department''',
            'sender': 'admin@microsoft365-it.com',
            'risk_score': 86.0
        },
        {
            'subject': 'Bank of America: Suspicious Transaction Alert',
            'body': '''ALERT: Unusual Activity Detected

A transaction of $2,499.00 was attempted from your account.

If you did not authorize this, click below to secure your account:
http://bofa-secure.malicious-bank.net/verify

Bank of America Security''',
            'sender': 'alerts@bankofamerica-security.net',
            'risk_score': 91.0
        }
    ]

    created = 0
    for sample in samples:
        threat = create_threat_from_data(
            subject=sample['subject'],
            body=sample['body'],
            sender=sample['sender'],
            risk_score=sample['risk_score']
        )
        if threat:
            created += 1

    db.session.commit()
    print(f"  Created {created} sample threats")
    return created


def main():
    print("=" * 60)
    print("PhishVision - Seeding Threat Feed")
    print("=" * 60)

    with app.app_context():
        existing = ThreatEntry.query.count()
        print(f"Current threats: {existing}")

        total = 0
        total += seed_sample_threats()
        total += seed_from_existing_analyses()
        total += seed_from_nigerian_fraud()

        final = ThreatEntry.query.count()
        iocs = ThreatIOC.query.count()

        print("=" * 60)
        print(f"Seeding complete!")
        print(f"  Threats before: {existing}")
        print(f"  Threats created: {total}")
        print(f"  Threats after: {final}")
        print(f"  Total IOCs: {iocs}")
        print("=" * 60)


if __name__ == '__main__':
    main()
