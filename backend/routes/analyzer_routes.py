from flask import Blueprint, request, jsonify
from database import db
from models import EmailAnalysis
from services.hybrid_analyzer import create_hybrid_analyzer
from services.header_validator import HeaderValidator
from routes.threat_feed_routes import auto_submit_to_threat_feed

bp = Blueprint('analyzer', __name__, url_prefix='/api/analyzer')
hybrid_analyzer = create_hybrid_analyzer()
header_validator = HeaderValidator()

@bp.route('/analyze', methods=['POST'])
def analyze_email():
    """Analyze email for phishing indicators using AI + NLP hybrid analysis"""
    data = request.json

    # Validate input
    required_fields = ['email_from', 'email_subject', 'email_body']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    email_from = data['email_from']
    email_subject = data['email_subject']
    email_body = data['email_body']
    headers = data.get('headers', '')

    # Perform header validation FIRST
    header_results = header_validator.validate_headers(headers, email_from)

    # Trusted domains - emails from these with auth pass = SAFE (skip AI to save cost)
    trusted_domains = [
        'amazon.com', 'amazon.co.uk', 'amazon.de', 'amazon.fr', 'amazon.es',
        'amazon.it', 'amazon.ca', 'amazon.co.jp', 'amazonses.com',
        'google.com', 'gmail.com', 'youtube.com', 'googlemail.com',
        'microsoft.com', 'outlook.com', 'hotmail.com', 'live.com', 'office365.com',
        'apple.com', 'icloud.com', 'me.com',
        'facebook.com', 'fb.com', 'meta.com', 'instagram.com', 'whatsapp.com',
        'paypal.com', 'ebay.com', 'netflix.com', 'spotify.com',
        'chase.com', 'jpmorgan.com', 'bankofamerica.com', 'bofa.com',
        'wellsfargo.com', 'citibank.com', 'citi.com', 'capitalone.com',
        'americanexpress.com', 'discover.com',
        'fedex.com', 'ups.com', 'usps.com', 'usps.gov', 'dhl.com',
        'linkedin.com', 'twitter.com', 'x.com', 'tiktok.com',
        'adobe.com', 'dropbox.com', 'zoom.us', 'zoom.com', 'slack.com',
        'walmart.com', 'target.com', 'bestbuy.com', 'etsy.com', 'shopify.com',
        'stripe.com', 'square.com', 'squareup.com', 'venmo.com',
        'github.com', 'gitlab.com', 'atlassian.com', 'bitbucket.org',
        'salesforce.com', 'hubspot.com', 'mailchimp.com', 'sendgrid.net'
    ]

    sender_domain = email_from.lower().split('@')[-1].split('>')[0] if '@' in email_from else ''
    is_trusted_domain = any(sender_domain.endswith(td) for td in trusted_domains)

    # Check authentication status
    all_auth_pass = (
        header_results['dkim_status'] == 'pass' and
        header_results['spf_status'] == 'pass' and
        header_results['dmarc_status'] == 'pass'
    )
    dkim_pass = header_results['dkim_status'] == 'pass'

    # SIMPLE RULE: Trusted domain + authentication = SAFE (skip expensive AI)
    if is_trusted_domain and all_auth_pass:
        analysis_results = {
            'risk_score': 5.0,
            'classification': 'safe',
            'suspicious_keywords': '{}',
            'url_analysis': '{}',
            'urgency_score': 0,
            'explanation': f'VERIFIED SENDER: Email authenticated from trusted domain ({sender_domain}). DKIM, SPF, and DMARC all passed.',
            'recommendations': '["Email is from a verified trusted sender", "Authentication fully passed", "Safe to interact with"]',
            'ai_risk_score': None,
            'ai_classification': None,
            'ai_reasoning': None,
            'ai_tactics_detected': None,
            'ai_confidence': None,
            'hybrid_risk_score': 5.0,
            'hybrid_classification': 'safe',
            'analysis_method': 'trusted_bypass',
            'is_novel_pattern': False,
            'novel_pattern_description': None,
            'detected_language': None
        }
    elif is_trusted_domain and dkim_pass:
        analysis_results = {
            'risk_score': 15.0,
            'classification': 'safe',
            'suspicious_keywords': '{}',
            'url_analysis': '{}',
            'urgency_score': 0,
            'explanation': f'VERIFIED SENDER: Email from trusted domain ({sender_domain}) with DKIM authentication passed.',
            'recommendations': '["Email is from a known trusted sender", "DKIM signature verified", "Likely safe to interact with"]',
            'ai_risk_score': None,
            'ai_classification': None,
            'ai_reasoning': None,
            'ai_tactics_detected': None,
            'ai_confidence': None,
            'hybrid_risk_score': 15.0,
            'hybrid_classification': 'safe',
            'analysis_method': 'trusted_bypass',
            'is_novel_pattern': False,
            'novel_pattern_description': None,
            'detected_language': None
        }
    else:
        # Run full HYBRID analysis (NLP + Gemini AI) for non-trusted emails
        analysis_results = hybrid_analyzer.analyze_email(
            subject=email_subject,
            body=email_body,
            sender=email_from,
            headers=headers
        )

    # Use hybrid score/classification as final result (or fallback to NLP)
    final_score = analysis_results.get('hybrid_risk_score') or analysis_results.get('risk_score', 50)
    final_classification = analysis_results.get('hybrid_classification') or analysis_results.get('classification', 'suspicious')

    # Create analysis record with all fields
    analysis = EmailAnalysis(
        email_from=email_from,
        email_subject=email_subject,
        email_body=email_body,
        headers=headers,
        # Final results
        risk_score=round(final_score, 2),
        classification=final_classification,
        # Auth status
        spf_status=header_results['spf_status'],
        dkim_status=header_results['dkim_status'],
        dmarc_status=header_results['dmarc_status'],
        # NLP details
        suspicious_keywords=analysis_results.get('suspicious_keywords', '{}'),
        url_analysis=analysis_results.get('url_analysis', '{}'),
        urgency_score=analysis_results.get('urgency_score', 0),
        explanation=analysis_results.get('explanation', ''),
        recommendations=analysis_results.get('recommendations', '[]'),
        # AI Analysis fields
        ai_risk_score=analysis_results.get('ai_risk_score'),
        ai_classification=analysis_results.get('ai_classification'),
        ai_reasoning=analysis_results.get('ai_reasoning'),
        ai_tactics_detected=analysis_results.get('ai_tactics_detected'),
        ai_confidence=analysis_results.get('ai_confidence'),
        # Hybrid results
        hybrid_risk_score=analysis_results.get('hybrid_risk_score'),
        hybrid_classification=analysis_results.get('hybrid_classification'),
        analysis_method=analysis_results.get('analysis_method', 'nlp'),
        # Novel pattern detection
        is_novel_pattern=analysis_results.get('is_novel_pattern', False),
        novel_pattern_description=analysis_results.get('novel_pattern_description'),
        # Language
        detected_language=analysis_results.get('detected_language')
    )

    db.session.add(analysis)
    db.session.commit()

    # Auto-submit malicious emails to threat feed
    threat_entry = None
    if final_classification == 'malicious':
        threat_entry = auto_submit_to_threat_feed(analysis)

    response = analysis.to_dict()
    if threat_entry:
        response['threat_feed'] = {
            'submitted': True,
            'short_id': threat_entry.short_id,
            'url': f'/threats/{threat_entry.short_id}'
        }

    return jsonify(response), 201

@bp.route('/history', methods=['GET'])
def get_analysis_history():
    """Get analysis history"""
    limit = request.args.get('limit', 50, type=int)
    analyses = EmailAnalysis.query.order_by(EmailAnalysis.analyzed_at.desc()).limit(limit).all()
    return jsonify([a.to_dict() for a in analyses])

@bp.route('/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Get specific analysis"""
    analysis = EmailAnalysis.query.get_or_404(analysis_id)
    return jsonify(analysis.to_dict())

@bp.route('/stats', methods=['GET'])
def get_analyzer_stats():
    """Get analyzer statistics"""
    total = EmailAnalysis.query.count()
    safe = EmailAnalysis.query.filter_by(classification='safe').count()
    suspicious = EmailAnalysis.query.filter_by(classification='suspicious').count()
    malicious = EmailAnalysis.query.filter_by(classification='malicious').count()

    return jsonify({
        'total_analyzed': total,
        'safe': safe,
        'suspicious': suspicious,
        'malicious': malicious,
        'safe_percentage': round((safe / total * 100) if total > 0 else 0, 2),
        'suspicious_percentage': round((suspicious / total * 100) if total > 0 else 0, 2),
        'malicious_percentage': round((malicious / total * 100) if total > 0 else 0, 2)
    })

@bp.route('/history', methods=['DELETE'])
def clear_analysis_history():
    """Clear all analysis history"""
    try:
        EmailAnalysis.query.delete()
        db.session.commit()
        return jsonify({'message': 'Analysis history cleared successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
