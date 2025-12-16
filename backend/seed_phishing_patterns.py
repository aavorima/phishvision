"""
Phishing Pattern Seeder
Extracts patterns from real phishing emails and seeds the database
"""

import mailbox
import re
import json
import uuid
from collections import Counter, defaultdict
from email.utils import parseaddr
from html import unescape
from datetime import datetime

# Import app context
from app import app
from database import db
from models import PhishingPattern


def extract_text_from_html(html):
    """Extract plain text from HTML"""
    if not html:
        return ""
    text = re.sub(r'<[^>]+>', ' ', str(html))
    text = unescape(text)
    return re.sub(r'\s+', ' ', text).strip()[:500]  # Limit to 500 chars


def detect_pattern_type(subject, body):
    """Detect the type of phishing attack"""
    text = f"{subject} {body}".lower()

    if any(word in text for word in ['password', 'login', 'credential', 'sign in', 'verify your account']):
        return 'credential_theft'
    elif any(word in text for word in ['wire transfer', 'ceo', 'cfo', 'urgent payment', 'invoice']):
        return 'bec'
    elif any(word in text for word in ['ebay', 'paypal', 'amazon', 'netflix', 'microsoft', 'apple', 'google']):
        return 'brand_impersonation'
    elif any(word in text for word in ['package', 'delivery', 'shipment', 'ups', 'fedex', 'dhl']):
        return 'delivery_scam'
    elif any(word in text for word in ['winner', 'lottery', 'prize', 'inheritance', 'million']):
        return 'reward_scam'
    elif any(word in text for word in ['virus', 'infected', 'tech support', 'call us']):
        return 'tech_support_scam'
    elif any(word in text for word in ['bank', 'account', 'suspended', 'limited']):
        return 'credential_theft'
    else:
        return 'social_engineering'


def detect_tactics(text):
    """Detect social engineering tactics used"""
    text_lower = text.lower()
    return {
        'authority': any(w in text_lower for w in ['official', 'security team', 'admin', 'support team', 'department']),
        'urgency': any(w in text_lower for w in ['urgent', 'immediately', 'asap', '24 hours', '48 hours', 'expire']),
        'fear': any(w in text_lower for w in ['suspended', 'blocked', 'unauthorized', 'fraud', 'compromised', 'limited']),
        'greed': any(w in text_lower for w in ['winner', 'prize', 'reward', 'free', 'bonus', 'refund']),
        'curiosity': any(w in text_lower for w in ['click here', 'find out', 'see attachment', 'view details']),
        'trust': any(w in text_lower for w in ['dear customer', 'valued member', 'trusted', 'secure'])
    }


def extract_indicators(text):
    """Extract phishing indicators from text"""
    text_lower = text.lower()
    indicators = []

    if any(w in text_lower for w in ['urgent', 'immediately', 'asap', 'right away']):
        indicators.append('urgency_language')
    if any(w in text_lower for w in ['suspended', 'blocked', 'terminated', 'closed']):
        indicators.append('threat_language')
    if any(w in text_lower for w in ['click here', 'click below', 'click the link']):
        indicators.append('action_request')
    if any(w in text_lower for w in ['password', 'ssn', 'credit card', 'bank account']):
        indicators.append('credential_request')
    if any(w in text_lower for w in ['dear customer', 'dear user', 'dear member', 'valued customer']):
        indicators.append('generic_greeting')
    if any(w in text_lower for w in ['verify', 'confirm', 'update', 'validate']):
        indicators.append('verification_request')
    if any(w in text_lower for w in ['limited access', 'account suspended', 'access restricted']):
        indicators.append('access_threat')
    if re.search(r'within \d+ (hours?|days?)', text_lower):
        indicators.append('deadline_pressure')
    if re.search(r'https?://\d+\.\d+\.\d+\.\d+', text_lower):
        indicators.append('ip_based_url')

    return indicators


def parse_mbox(mbox_path):
    """Parse mbox file and extract email data"""
    mbox = mailbox.mbox(mbox_path)
    emails = []

    print(f"Parsing {len(mbox)} emails...")

    for i, msg in enumerate(mbox):
        try:
            # Get sender
            from_header = msg.get('From', '')
            name, email_addr = parseaddr(str(from_header))
            sender_domain = email_addr.split('@')[-1].lower() if '@' in email_addr else ''

            # Get subject
            subject = str(msg.get('Subject', ''))[:200]

            # Get body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() in ['text/plain', 'text/html']:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = extract_text_from_html(payload)
                            break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = extract_text_from_html(payload)

            if subject or body:
                emails.append({
                    'sender': email_addr,
                    'sender_domain': sender_domain,
                    'subject': subject,
                    'body': body[:500]
                })

        except Exception as e:
            continue

    print(f"Successfully parsed {len(emails)} emails")
    return emails


def cluster_emails(emails):
    """Cluster similar emails to find patterns"""
    clusters = defaultdict(list)

    for email in emails:
        # Create a simple cluster key based on sender domain and subject keywords
        subject_lower = email['subject'].lower()

        # Determine brand
        brand = 'generic'
        brands = ['ebay', 'paypal', 'amazon', 'chase', 'bank of america', 'wells fargo',
                  'citibank', 'capital one', 'regions', 'fifth third', 'national city',
                  'suntrust', 'keybank', 'southtrust', 'citizens', 'microsoft', 'apple']
        for b in brands:
            if b in subject_lower or b in email['sender_domain']:
                brand = b.replace(' ', '_')
                break

        # Determine type
        if 'verify' in subject_lower or 'confirm' in subject_lower:
            ptype = 'verification'
        elif 'suspended' in subject_lower or 'limited' in subject_lower:
            ptype = 'suspension'
        elif 'security' in subject_lower or 'alert' in subject_lower:
            ptype = 'security_alert'
        elif 'update' in subject_lower:
            ptype = 'update_request'
        else:
            ptype = 'general'

        cluster_key = f"{brand}_{ptype}"
        clusters[cluster_key].append(email)

    return clusters


def create_patterns(clusters, min_cluster_size=3):
    """Create PhishingPattern records from clusters"""
    patterns = []

    for cluster_key, emails in clusters.items():
        if len(emails) < min_cluster_size:
            continue

        # Use first email as example
        example = emails[0]
        full_text = f"{example['subject']} {example['body']}"

        # Detect pattern characteristics
        pattern_type = detect_pattern_type(example['subject'], example['body'])
        tactics = detect_tactics(full_text)
        indicators = extract_indicators(full_text)

        # Create sender pattern
        sender_pattern = f"*@{example['sender_domain']}" if example['sender_domain'] else None

        pattern = {
            'pattern_type': pattern_type,
            'example_subject': example['subject'][:200],
            'example_body_snippet': example['body'][:300],
            'example_sender_pattern': sender_pattern,
            'indicators': indicators,
            'tactics': tactics,
            'cluster_size': len(emails),
            'cluster_key': cluster_key
        }

        patterns.append(pattern)

    return patterns


def seed_database(patterns):
    """Insert patterns into database"""
    with app.app_context():
        created = 0
        skipped = 0

        for p in patterns:
            # Check if similar pattern exists
            existing = PhishingPattern.query.filter_by(
                pattern_type=p['pattern_type'],
                example_subject=p['example_subject'][:200]
            ).first()

            if existing:
                skipped += 1
                continue

            pattern = PhishingPattern(
                id=str(uuid.uuid4()),
                pattern_type=p['pattern_type'],
                example_subject=p['example_subject'][:200],
                example_body_snippet=p['example_body_snippet'][:500],
                example_sender_pattern=p['example_sender_pattern'],
                indicators=json.dumps(p['indicators']),
                tactics=json.dumps(p['tactics']),
                source='threat_intel',
                effectiveness_score=65.0,  # Conservative start
                confidence_level='medium',
                language='en',
                is_active=True,
                detection_count=p['cluster_size'],  # Use cluster size as initial count
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.session.add(pattern)
            created += 1

        db.session.commit()
        return created, skipped


def main():
    mbox_path = '/home/morpho/Desktop/emails-phishing.mbox'

    print("=" * 60)
    print("PhishVision - Phishing Pattern Seeder")
    print("=" * 60)

    # Parse emails
    emails = parse_mbox(mbox_path)

    # Cluster similar emails
    print("\nClustering emails...")
    clusters = cluster_emails(emails)
    print(f"Found {len(clusters)} unique clusters")

    # Show cluster summary
    print("\nTop clusters by size:")
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
    for key, emails in sorted_clusters[:20]:
        print(f"  {key}: {len(emails)} emails")

    # Create patterns
    print("\nCreating patterns...")
    patterns = create_patterns(clusters, min_cluster_size=2)
    print(f"Created {len(patterns)} pattern definitions")

    # Seed database
    print("\nSeeding database...")
    created, skipped = seed_database(patterns)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"  Emails parsed: {len(emails)}")
    print(f"  Clusters found: {len(clusters)}")
    print(f"  Patterns created: {created}")
    print(f"  Patterns skipped (duplicates): {skipped}")
    print("=" * 60)

    # Show some created patterns
    with app.app_context():
        recent = PhishingPattern.query.filter_by(source='threat_intel').order_by(
            PhishingPattern.created_at.desc()
        ).limit(10).all()

        print("\nRecent patterns added:")
        for p in recent:
            print(f"  - {p.pattern_type}: {p.example_subject[:60]}...")


if __name__ == '__main__':
    main()
