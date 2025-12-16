"""
Feedback API Routes
Endpoints for user feedback submission and learning system management
"""
from flask import Blueprint, request, jsonify, session
from models import db, AnalysisFeedback, PhishingPattern, EmailAnalysis
from services.feedback_learner import FeedbackLearner, create_feedback_learner
from datetime import datetime

bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

# Lazy load feedback learner
_feedback_learner = None

def get_feedback_learner():
    """Lazy initialize feedback learner."""
    global _feedback_learner
    if _feedback_learner is None:
        _feedback_learner = create_feedback_learner()
    return _feedback_learner


def require_auth(f):
    """Decorator to require authentication."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


@bp.route('/submit', methods=['POST'])
@require_auth
def submit_feedback():
    """
    Submit user feedback on analysis results.

    Expected JSON:
    {
        "analysis_id": 123,
        "user_classification": "malicious|safe|suspicious",
        "comment": "Optional user comment"
    }
    """
    data = request.json
    user_id = session.get('user_id')

    analysis_id = data.get('analysis_id')
    user_classification = data.get('user_classification', '').lower()
    comment = data.get('comment', '')

    # Validate inputs
    if not analysis_id:
        return jsonify({'error': 'analysis_id is required'}), 400

    if user_classification not in ['malicious', 'safe', 'suspicious']:
        return jsonify({'error': 'user_classification must be: malicious, safe, or suspicious'}), 400

    # Get original analysis
    analysis = EmailAnalysis.query.get(analysis_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404

    # Determine feedback type
    original_classification = analysis.hybrid_classification or analysis.classification
    if not original_classification:
        original_classification = 'unknown'

    if original_classification == user_classification:
        feedback_type = 'correct'
    elif user_classification == 'malicious' and original_classification in ['safe', 'suspicious']:
        feedback_type = 'false_negative'  # We missed a phishing email
    elif user_classification == 'safe' and original_classification in ['malicious', 'suspicious']:
        feedback_type = 'false_positive'  # We incorrectly flagged a safe email
    else:
        feedback_type = 'correction'  # Other classification change

    # Check for duplicate feedback
    existing = AnalysisFeedback.query.filter_by(
        analysis_id=analysis_id,
        user_id=user_id
    ).first()

    if existing:
        # Update existing feedback
        existing.user_classification = user_classification
        existing.feedback_type = feedback_type
        existing.comment = comment
        existing.is_processed = False  # Mark for re-processing
        existing.updated_at = datetime.utcnow()
        db.session.commit()
        feedback_id = existing.id
    else:
        # Create new feedback
        feedback = AnalysisFeedback(
            analysis_id=analysis_id,
            user_id=user_id,
            original_classification=original_classification,
            user_classification=user_classification,
            feedback_type=feedback_type,
            comment=comment,
            is_processed=False
        )
        db.session.add(feedback)
        db.session.commit()
        feedback_id = feedback.id

    # Process feedback immediately for fast learning
    try:
        learner = get_feedback_learner()
        feedback_obj = AnalysisFeedback.query.get(feedback_id)
        result = learner.process_feedback(feedback_obj)

        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'feedback_type': feedback_type,
            'learning_result': {
                'pattern_created': result.get('pattern_created', False),
                'pattern_updated': result.get('pattern_updated', False),
                'action': result.get('action'),
                'details': result.get('details')
            },
            'message': _get_feedback_message(feedback_type, result)
        })
    except Exception as e:
        print(f"[WARNING] Feedback processing failed: {e}")
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'feedback_type': feedback_type,
            'learning_result': None,
            'message': 'Thank you! Your feedback has been recorded and will be processed.'
        })


def _get_feedback_message(feedback_type: str, result: dict) -> str:
    """Generate user-friendly message based on feedback result."""
    if feedback_type == 'correct':
        return 'Thank you for confirming! This helps improve our detection accuracy.'

    if feedback_type == 'false_negative':
        if result.get('pattern_created'):
            return 'Thank you! We\'ve created a new detection pattern from your feedback. Similar phishing attempts will be caught in the future.'
        return 'Thank you for reporting this phishing email! We\'re learning from this to improve detection.'

    if feedback_type == 'false_positive':
        if result.get('pattern_updated'):
            return 'Thank you! We\'ve adjusted our detection patterns to reduce false positives like this.'
        return 'Thank you for letting us know this was safe. We\'ll use this to improve accuracy.'

    return 'Thank you for your feedback!'


@bp.route('/stats', methods=['GET'])
@require_auth
def feedback_stats():
    """
    Get feedback and learning statistics.
    """
    try:
        learner = get_feedback_learner()
        stats = learner.get_learning_stats()

        # Add user-specific stats
        user_id = session.get('user_id')
        user_feedback_count = AnalysisFeedback.query.filter_by(user_id=user_id).count()

        stats['user_feedback_count'] = user_feedback_count

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500


@bp.route('/patterns', methods=['GET'])
@require_auth
def list_patterns():
    """
    List learned phishing patterns.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    active_only = request.args.get('active_only', 'true').lower() == 'true'

    query = PhishingPattern.query

    if active_only:
        query = query.filter_by(is_active=True)

    query = query.order_by(PhishingPattern.effectiveness_score.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    patterns = [{
        'id': p.id,
        'pattern_type': p.pattern_type,
        'effectiveness_score': p.effectiveness_score,
        'detection_count': p.detection_count,
        'false_positive_count': p.false_positive_count,
        'source': p.source,
        'language': p.language,
        'is_active': p.is_active,
        'created_at': p.created_at.isoformat() if p.created_at else None,
        'example_subject': p.example_subject[:100] if p.example_subject else None
    } for p in pagination.items]

    return jsonify({
        'patterns': patterns,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/patterns/<int:pattern_id>', methods=['GET'])
@require_auth
def get_pattern(pattern_id):
    """
    Get details of a specific pattern.
    """
    pattern = PhishingPattern.query.get(pattern_id)

    if not pattern:
        return jsonify({'error': 'Pattern not found'}), 404

    return jsonify({
        'id': pattern.id,
        'pattern_type': pattern.pattern_type,
        'indicators': pattern.indicators,
        'tactics': pattern.tactics,
        'example_subject': pattern.example_subject,
        'example_body_snippet': pattern.example_body_snippet,
        'effectiveness_score': pattern.effectiveness_score,
        'detection_count': pattern.detection_count,
        'false_positive_count': pattern.false_positive_count,
        'source': pattern.source,
        'language': pattern.language,
        'is_active': pattern.is_active,
        'created_at': pattern.created_at.isoformat() if pattern.created_at else None,
        'updated_at': pattern.updated_at.isoformat() if pattern.updated_at else None
    })


@bp.route('/history', methods=['GET'])
@require_auth
def feedback_history():
    """
    Get user's feedback history.
    """
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = AnalysisFeedback.query.filter_by(user_id=user_id)\
        .order_by(AnalysisFeedback.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for fb in pagination.items:
        # Get associated analysis
        analysis = EmailAnalysis.query.get(fb.analysis_id)
        items.append({
            'id': fb.id,
            'analysis_id': fb.analysis_id,
            'original_classification': fb.original_classification,
            'user_classification': fb.user_classification,
            'feedback_type': fb.feedback_type,
            'is_processed': fb.is_processed,
            'learned_pattern_id': fb.learned_pattern_id,
            'created_at': fb.created_at.isoformat() if fb.created_at else None,
            'analysis_subject': analysis.subject[:50] if analysis and analysis.subject else None
        })

    return jsonify({
        'feedback': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/process-batch', methods=['POST'])
@require_auth
def process_batch():
    """
    Process unprocessed feedback in batch.
    Admin endpoint for manual triggering.
    """
    limit = request.json.get('limit', 100) if request.json else 100

    try:
        learner = get_feedback_learner()
        result = learner.batch_process_feedback(limit=limit)

        return jsonify({
            'success': True,
            'results': result
        })
    except Exception as e:
        return jsonify({'error': f'Batch processing failed: {str(e)}'}), 500
