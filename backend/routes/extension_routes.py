"""
Browser Extension API Routes
Lightweight endpoints for the PhishVision browser extension
Supports hybrid NLP + AI analysis and user feedback learning
"""
from flask import Blueprint, request, jsonify, session
from services.nlp_analyzer import NLPAnalyzer
from services.hybrid_analyzer import HybridAnalyzer, create_hybrid_analyzer
from models import db, EmailAnalysis, AnalysisFeedback
from datetime import datetime

bp = Blueprint('extension', __name__, url_prefix='/api/extension')
nlp_analyzer = NLPAnalyzer()

# Initialize hybrid analyzer (lazy loading)
_hybrid_analyzer = None

def get_hybrid_analyzer():
    """Lazy initialize hybrid analyzer."""
    global _hybrid_analyzer
    if _hybrid_analyzer is None:
        _hybrid_analyzer = create_hybrid_analyzer()
    return _hybrid_analyzer


def require_auth(f):
    """Decorator to require authentication for extension endpoints"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@bp.route('/check-url', methods=['POST'])
@require_auth
def check_url():
    """
    Lightweight URL-only check for browser extension
    Fast endpoint that doesn't store results in database
    """
    data = request.json
    url = data.get('url', '')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if len(url) > 2000:
        return jsonify({'error': 'URL too long'}), 400

    # Use existing URL analysis from NLP analyzer
    urls = [url]
    url_analysis = nlp_analyzer._analyze_urls(urls, url.lower())

    # Calculate risk score based on URL alone
    risk_score = 0
    reasons = []

    # Check suspicious URLs
    if url_analysis['suspicious_urls']:
        for suspicious in url_analysis['suspicious_urls']:
            url_reasons = suspicious.get('reasons', [])
            reasons.extend(url_reasons)
            # Weight different reasons
            for reason in url_reasons:
                if 'IP address' in reason:
                    risk_score += 25
                elif 'TLD' in reason:
                    risk_score += 20
                elif 'shortener' in reason:
                    risk_score += 15
                elif 'Typosquatting' in reason:
                    risk_score += 35
                elif 'subdomain' in reason:
                    risk_score += 20
                elif 'encoding' in reason:
                    risk_score += 15
                elif '@' in reason:
                    risk_score += 30
                else:
                    risk_score += 10

    # Typosquatting is very serious
    if url_analysis.get('typosquatting_detected'):
        risk_score = max(risk_score, 70)
        if 'Possible typosquatting detected' not in reasons:
            reasons.append('Possible typosquatting detected')

    # URL shorteners are suspicious but not critical
    if url_analysis.get('url_shortener_detected'):
        risk_score = max(risk_score, 30)

    # Cap score at 100
    risk_score = min(risk_score, 100)

    # Classify based on score
    if risk_score < 20:
        classification = 'safe'
    elif risk_score < 45:
        classification = 'suspicious'
    else:
        classification = 'malicious'

    return jsonify({
        'url': url,
        'risk_score': round(risk_score, 1),
        'classification': classification,
        'reasons': list(set(reasons))[:10],  # Dedupe and limit
        'details': {
            'typosquatting_detected': url_analysis.get('typosquatting_detected', False),
            'url_shortener_detected': url_analysis.get('url_shortener_detected', False),
            'suspicious_patterns': url_analysis.get('suspicious_patterns', [])[:5]
        }
    })


@bp.route('/check-urls', methods=['POST'])
@require_auth
def check_urls_batch():
    """
    Batch URL check for page scanning
    Checks multiple URLs at once for efficiency
    """
    data = request.json
    urls = data.get('urls', [])

    if not urls:
        return jsonify({'error': 'URLs array is required'}), 400

    if len(urls) > 50:
        return jsonify({'error': 'Maximum 50 URLs per request'}), 400

    results = []

    for url in urls:
        if not url or len(url) > 2000:
            results.append({
                'url': url[:100] if url else '',
                'risk_score': 0,
                'classification': 'error',
                'reasons': ['Invalid URL']
            })
            continue

        # Analyze URL
        url_analysis = nlp_analyzer._analyze_urls([url], url.lower())

        risk_score = 0
        reasons = []

        if url_analysis['suspicious_urls']:
            for suspicious in url_analysis['suspicious_urls']:
                url_reasons = suspicious.get('reasons', [])
                reasons.extend(url_reasons)
                risk_score += len(url_reasons) * 12

        if url_analysis.get('typosquatting_detected'):
            risk_score = max(risk_score, 70)

        if url_analysis.get('url_shortener_detected'):
            risk_score = max(risk_score, 25)

        risk_score = min(risk_score, 100)

        if risk_score < 20:
            classification = 'safe'
        elif risk_score < 45:
            classification = 'suspicious'
        else:
            classification = 'malicious'

        results.append({
            'url': url[:200],
            'risk_score': round(risk_score, 1),
            'classification': classification,
            'reasons': list(set(reasons))[:3]  # Limit reasons per URL
        })

    # Summary statistics
    safe_count = sum(1 for r in results if r['classification'] == 'safe')
    suspicious_count = sum(1 for r in results if r['classification'] == 'suspicious')
    malicious_count = sum(1 for r in results if r['classification'] == 'malicious')

    return jsonify({
        'results': results,
        'summary': {
            'total': len(results),
            'safe': safe_count,
            'suspicious': suspicious_count,
            'malicious': malicious_count
        }
    })


@bp.route('/analyze-quick', methods=['POST'])
@require_auth
def analyze_quick():
    """
    Hybrid content analysis using NLP + AI when needed.
    Stores results in database for feedback learning.
    """
    data = request.json
    content = data.get('content', '')
    subject = data.get('subject', '')
    sender = data.get('sender', 'unknown@unknown.com')
    store_result = data.get('store', True)  # Store for feedback learning

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    if len(content) < 10:
        return jsonify({'error': 'Content too short (min 10 characters)'}), 400

    if len(content) > 50000:
        return jsonify({'error': 'Content too long (max 50000 characters)'}), 400

    # Run hybrid analysis (NLP + AI when needed)
    try:
        hybrid = get_hybrid_analyzer()
        results = hybrid.analyze_email(
            subject=subject,
            body=content,
            sender=sender,
            attachments=[],
            headers='',
            user_id=session.get('user_id')
        )

        analysis_id = None

        # Store result for feedback learning
        if store_result:
            try:
                analysis = EmailAnalysis(
                    user_id=session.get('user_id'),
                    subject=subject[:500] if subject else None,
                    body_text=content[:10000],
                    sender_email=sender[:255] if sender else None,
                    risk_score=results.get('hybrid_risk_score', results.get('risk_score', 50)),
                    classification=results.get('hybrid_classification', results.get('classification')),
                    explanation=results.get('explanation', ''),
                    recommendations=results.get('recommendations', '[]'),
                    # AI fields
                    ai_risk_score=results.get('ai_risk_score'),
                    ai_classification=results.get('ai_classification'),
                    ai_reasoning=results.get('ai_reasoning'),
                    ai_tactics_detected=results.get('ai_tactics_detected'),
                    ai_confidence=results.get('ai_confidence'),
                    hybrid_risk_score=results.get('hybrid_risk_score'),
                    hybrid_classification=results.get('hybrid_classification'),
                    analysis_method=results.get('analysis_method', 'nlp'),
                    is_novel_pattern=results.get('is_novel_pattern', False),
                    novel_pattern_description=results.get('novel_pattern_description'),
                    detected_language=results.get('detected_language'),
                    # NLP fields
                    suspicious_keywords=results.get('suspicious_keywords', '{}'),
                    url_analysis=results.get('url_analysis', '{}'),
                    urgency_score=results.get('urgency_score', 0),
                    phishing_phrases_detected=results.get('phishing_phrases_detected', '[]')
                )
                db.session.add(analysis)
                db.session.commit()
                analysis_id = analysis.id
            except Exception as e:
                print(f"[WARNING] Failed to store analysis: {e}")
                db.session.rollback()

        return jsonify({
            'analysis_id': analysis_id,
            'risk_score': results.get('hybrid_risk_score', results.get('risk_score', 50)),
            'classification': results.get('hybrid_classification', results.get('classification')),
            'urgency_score': results.get('urgency_score', 0),
            'explanation': results.get('explanation', ''),
            'recommendations': results.get('recommendations', '[]'),
            'analysis_method': results.get('analysis_method', 'nlp'),
            'ai_used': results.get('analysis_method') == 'hybrid',
            'ai_confidence': results.get('ai_confidence'),
            'ai_reasoning': results.get('ai_reasoning'),
            'is_novel_pattern': results.get('is_novel_pattern', False),
            'detected_language': results.get('detected_language'),
            'details': {
                'suspicious_keywords': results.get('suspicious_keywords', '{}'),
                'url_analysis': results.get('url_analysis', '{}'),
                'phishing_phrases': results.get('phishing_phrases_detected', '[]'),
                'ai_tactics': results.get('ai_tactics_detected'),
                'ai_indicators': results.get('ai_indicators')
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@bp.route('/analyze-ai', methods=['POST'])
@require_auth
def analyze_ai():
    """
    Force AI-powered analysis regardless of NLP score.
    Use when user wants deep AI analysis.
    """
    data = request.json
    content = data.get('content', '')
    subject = data.get('subject', '')
    sender = data.get('sender', 'unknown@unknown.com')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    if len(content) < 10:
        return jsonify({'error': 'Content too short'}), 400

    if len(content) > 50000:
        return jsonify({'error': 'Content too long'}), 400

    try:
        hybrid = get_hybrid_analyzer()
        results = hybrid.analyze_email(
            subject=subject,
            body=content,
            sender=sender,
            force_ai=True,  # Force AI analysis
            user_id=session.get('user_id')
        )

        # Store result
        try:
            analysis = EmailAnalysis(
                user_id=session.get('user_id'),
                subject=subject[:500] if subject else None,
                body_text=content[:10000],
                sender_email=sender[:255] if sender else None,
                risk_score=results.get('hybrid_risk_score', results.get('risk_score', 50)),
                classification=results.get('hybrid_classification', results.get('classification')),
                explanation=results.get('explanation', ''),
                recommendations=results.get('recommendations', '[]'),
                ai_risk_score=results.get('ai_risk_score'),
                ai_classification=results.get('ai_classification'),
                ai_reasoning=results.get('ai_reasoning'),
                ai_tactics_detected=results.get('ai_tactics_detected'),
                ai_confidence=results.get('ai_confidence'),
                hybrid_risk_score=results.get('hybrid_risk_score'),
                hybrid_classification=results.get('hybrid_classification'),
                analysis_method=results.get('analysis_method', 'hybrid'),
                is_novel_pattern=results.get('is_novel_pattern', False),
                novel_pattern_description=results.get('novel_pattern_description'),
                detected_language=results.get('detected_language')
            )
            db.session.add(analysis)
            db.session.commit()
            analysis_id = analysis.id
        except Exception as e:
            print(f"[WARNING] Failed to store analysis: {e}")
            db.session.rollback()
            analysis_id = None

        return jsonify({
            'analysis_id': analysis_id,
            'risk_score': results.get('hybrid_risk_score', results.get('risk_score', 50)),
            'classification': results.get('hybrid_classification', results.get('classification')),
            'explanation': results.get('explanation', ''),
            'recommendations': results.get('recommendations', '[]'),
            'analysis_method': results.get('analysis_method'),
            'ai_confidence': results.get('ai_confidence'),
            'ai_reasoning': results.get('ai_reasoning'),
            'ai_tactics': results.get('ai_tactics_detected'),
            'is_novel_pattern': results.get('is_novel_pattern', False),
            'novel_pattern_description': results.get('novel_pattern_description'),
            'detected_language': results.get('detected_language')
        })
    except Exception as e:
        return jsonify({'error': f'AI analysis failed: {str(e)}'}), 500


@bp.route('/status', methods=['GET'])
def extension_status():
    """
    Health check endpoint for extension
    Returns authentication status, server info, and AI status
    """
    user_id = session.get('user_id')

    # Check AI availability
    try:
        hybrid = get_hybrid_analyzer()
        ai_enabled = hybrid.ai_enabled
    except:
        ai_enabled = False

    return jsonify({
        'status': 'online',
        'authenticated': user_id is not None,
        'version': '2.0.0',
        'ai_enabled': ai_enabled,
        'endpoints': {
            'check_url': '/api/extension/check-url',
            'check_urls': '/api/extension/check-urls',
            'analyze_quick': '/api/extension/analyze-quick',
            'analyze_ai': '/api/extension/analyze-ai',
            'feedback': '/api/feedback/submit'
        }
    })
