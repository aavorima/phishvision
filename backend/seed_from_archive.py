"""
Seed PhishingPatterns from Archive Dataset
Loads phishing samples from CSV files and creates patterns for few-shot learning.
"""

import csv
import re
import json
import hashlib
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import db
from models import PhishingPattern


ARCHIVE_PATH = '/home/morpho/Desktop/archive'


def extract_indicators(text, subject=''):
    """Extract phishing indicators from email text."""
    indicators = []
    text_lower = text.lower()
    subject_lower = subject.lower()

    # Urgency indicators
    if any(w in text_lower for w in ['urgent', 'immediately', 'asap', '24 hours', '48 hours', 'expire', 'suspended']):
        indicators.append('urgency_tactics')

    # Credential requests
    if any(w in text_lower for w in ['password', 'verify your account', 'confirm your', 'update your account', 'validate']):
        indicators.append('credential_request')

    # Financial
    if any(w in text_lower for w in ['bank', 'account', 'payment', 'transaction', 'wire transfer', 'million dollars']):
        indicators.append('financial_theme')

    # Authority impersonation
    if any(w in text_lower for w in ['security team', 'security department', 'administrator', 'official']):
        indicators.append('authority_impersonation')

    # Threat language
    if any(w in text_lower for w in ['locked', 'suspended', 'terminated', 'compromised', 'unauthorized']):
        indicators.append('threat_language')

    # Brand mentions in subject
    brands = ['amazon', 'paypal', 'apple', 'microsoft', 'google', 'bank of america', 'chase', 'wells fargo', 'netflix', 'facebook']
    for brand in brands:
        if brand in subject_lower or brand in text_lower:
            indicators.append(f'brand_mention:{brand}')
            break

    # URL presence
    if 'click here' in text_lower or 'http' in text_lower:
        indicators.append('contains_url')

    return indicators[:10]  # Limit to 10 indicators


def detect_tactics(text):
    """Detect social engineering tactics."""
    text_lower = text.lower()
    tactics = {
        'authority': any(w in text_lower for w in ['official', 'security', 'administrator', 'team', 'department']),
        'urgency': any(w in text_lower for w in ['urgent', 'immediately', 'now', 'expire', 'hours']),
        'scarcity': any(w in text_lower for w in ['limited', 'only', 'last chance', 'expire']),
        'fear': any(w in text_lower for w in ['suspended', 'locked', 'compromised', 'unauthorized', 'fraud']),
        'greed': any(w in text_lower for w in ['winner', 'million', 'prize', 'lottery', 'inheritance']),
        'trust': any(w in text_lower for w in ['dear customer', 'valued', 'thank you for'])
    }
    return tactics


def detect_pattern_type(text, subject=''):
    """Detect the type of phishing pattern."""
    text_lower = (text + ' ' + subject).lower()

    if any(w in text_lower for w in ['password', 'verify', 'confirm account', 'update account', 'login']):
        return 'credential_theft'
    elif any(w in text_lower for w in ['inheritance', 'million dollars', 'lottery', 'winner', 'nigerian']):
        return 'reward_scam'
    elif any(w in text_lower for w in ['invoice', 'payment due', 'overdue']):
        return 'invoice_scam'
    elif any(w in text_lower for w in ['package', 'delivery', 'shipment', 'fedex', 'ups', 'usps']):
        return 'delivery_scam'
    elif any(w in text_lower for w in ['apple', 'itunes', 'amazon', 'paypal', 'netflix']):
        return 'brand_impersonation'
    elif any(w in text_lower for w in ['ceo', 'wire transfer', 'urgent payment']):
        return 'bec'
    else:
        return 'social_engineering'


def extract_sender_pattern(sender):
    """Extract a pattern from sender email."""
    if not sender or '@' not in sender:
        return None

    # Extract domain
    match = re.search(r'@([a-zA-Z0-9.-]+)', sender)
    if match:
        domain = match.group(1)
        return f'*@{domain}'
    return None


def sanitize_text(text, max_length=500):
    """Sanitize and truncate text for storage."""
    if not text:
        return ''

    # Remove email addresses (PII)
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)

    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

    # Truncate
    if len(text) > max_length:
        text = text[:max_length] + '...'

    return text.strip()


def load_nazario_dataset(limit=500):
    """Load patterns from Nazario phishing corpus."""
    patterns_created = 0
    filepath = os.path.join(ARCHIVE_PATH, 'Nazario.csv')

    print(f"Loading Nazario dataset from {filepath}...")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader):
                if i >= limit:
                    break

                subject = row.get('subject', '')
                body = row.get('body', '')
                sender = row.get('sender', '')

                if not subject and not body:
                    continue

                # Check for duplicate
                text_hash = hashlib.sha256((subject + body[:200]).encode()).hexdigest()[:16]
                existing = PhishingPattern.query.filter(
                    PhishingPattern.example_subject == subject[:200]
                ).first()

                if existing:
                    continue

                # Create pattern
                pattern = PhishingPattern(
                    pattern_type=detect_pattern_type(body, subject),
                    example_subject=sanitize_text(subject, 200),
                    example_body_snippet=sanitize_text(body, 500),
                    example_sender_pattern=extract_sender_pattern(sender),
                    indicators=json.dumps(extract_indicators(body, subject)),
                    tactics=json.dumps(detect_tactics(body)),
                    classification_hints=json.dumps({'source': 'nazario_corpus', 'confirmed_phishing': True}),
                    effectiveness_score=75.0,  # High confidence - known phishing
                    source='threat_intel',
                    language='en',
                    is_active=True,
                    confidence_level='high'
                )

                db.session.add(pattern)
                patterns_created += 1

                if patterns_created % 100 == 0:
                    db.session.commit()
                    print(f"  Created {patterns_created} patterns...")

        db.session.commit()
        print(f"Nazario: Created {patterns_created} patterns")

    except Exception as e:
        print(f"Error loading Nazario: {e}")
        db.session.rollback()

    return patterns_created


def load_nigerian_fraud_dataset(limit=300):
    """Load patterns from Nigerian fraud corpus."""
    patterns_created = 0
    filepath = os.path.join(ARCHIVE_PATH, 'Nigerian_Fraud.csv')

    print(f"Loading Nigerian Fraud dataset from {filepath}...")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader):
                if i >= limit:
                    break

                subject = row.get('subject', '')
                body = row.get('body', '')
                sender = row.get('sender', '')

                if not subject and not body:
                    continue

                # Check for duplicate
                existing = PhishingPattern.query.filter(
                    PhishingPattern.example_subject == subject[:200]
                ).first()

                if existing:
                    continue

                # Create pattern
                pattern = PhishingPattern(
                    pattern_type='reward_scam',  # Nigerian fraud is typically reward scam
                    example_subject=sanitize_text(subject, 200),
                    example_body_snippet=sanitize_text(body, 500),
                    example_sender_pattern=extract_sender_pattern(sender),
                    indicators=json.dumps(extract_indicators(body, subject) + ['nigerian_419', 'advance_fee']),
                    tactics=json.dumps(detect_tactics(body)),
                    classification_hints=json.dumps({'source': 'nigerian_fraud_corpus', 'scam_type': '419'}),
                    effectiveness_score=80.0,  # High confidence
                    source='threat_intel',
                    language='en',
                    is_active=True,
                    confidence_level='high'
                )

                db.session.add(pattern)
                patterns_created += 1

                if patterns_created % 100 == 0:
                    db.session.commit()
                    print(f"  Created {patterns_created} patterns...")

        db.session.commit()
        print(f"Nigerian Fraud: Created {patterns_created} patterns")

    except Exception as e:
        print(f"Error loading Nigerian Fraud: {e}")
        db.session.rollback()

    return patterns_created


def load_phishing_email_dataset(limit=1000):
    """Load patterns from main phishing_email.csv (only phishing samples)."""
    patterns_created = 0
    filepath = os.path.join(ARCHIVE_PATH, 'phishing_email.csv')

    print(f"Loading phishing_email dataset from {filepath}...")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)

            phishing_count = 0
            for row in reader:
                # Only load phishing emails (label=1)
                if row.get('label', '0') != '1':
                    continue

                phishing_count += 1
                if phishing_count > limit:
                    break

                text = row.get('text_combined', '')
                if not text or len(text) < 50:
                    continue

                # Extract subject-like content (first line or first 100 chars)
                lines = text.split('\n')
                subject = lines[0][:100] if lines else text[:100]
                body = text[:1000]

                # Check for duplicate
                existing = PhishingPattern.query.filter(
                    PhishingPattern.example_body_snippet.like(body[:100] + '%')
                ).first()

                if existing:
                    continue

                # Create pattern
                pattern = PhishingPattern(
                    pattern_type=detect_pattern_type(body, subject),
                    example_subject=sanitize_text(subject, 200),
                    example_body_snippet=sanitize_text(body, 500),
                    example_sender_pattern=None,
                    indicators=json.dumps(extract_indicators(body, subject)),
                    tactics=json.dumps(detect_tactics(body)),
                    classification_hints=json.dumps({'source': 'phishing_email_dataset', 'label': 1}),
                    effectiveness_score=70.0,
                    source='threat_intel',
                    language='en',
                    is_active=True,
                    confidence_level='medium'
                )

                db.session.add(pattern)
                patterns_created += 1

                if patterns_created % 100 == 0:
                    db.session.commit()
                    print(f"  Created {patterns_created} patterns...")

        db.session.commit()
        print(f"phishing_email.csv: Created {patterns_created} patterns")

    except Exception as e:
        print(f"Error loading phishing_email: {e}")
        db.session.rollback()

    return patterns_created


def main():
    """Main function to seed patterns from archive."""
    print("=" * 60)
    print("PhishVision - Seeding Patterns from Archive")
    print("=" * 60)

    with app.app_context():
        # Check current pattern count
        existing_count = PhishingPattern.query.count()
        print(f"Current patterns in database: {existing_count}")

        total_created = 0

        # Load from each dataset
        total_created += load_nazario_dataset(limit=500)
        total_created += load_nigerian_fraud_dataset(limit=300)
        total_created += load_phishing_email_dataset(limit=1000)

        # Final count
        final_count = PhishingPattern.query.count()

        print("=" * 60)
        print(f"Seeding complete!")
        print(f"  Patterns before: {existing_count}")
        print(f"  Patterns created: {total_created}")
        print(f"  Patterns after: {final_count}")
        print("=" * 60)


if __name__ == '__main__':
    main()
