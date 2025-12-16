"""
Threat Feed Routes - Community Threat Intelligence API
Public endpoints for viewing threats, authenticated endpoints for submission
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from database import db
from models import ThreatEntry, ThreatIOC, ThreatVote, EmailAnalysis, User
from services.ioc_extractor import IOCExtractor
import json
import hashlib

bp = Blueprint('threats', __name__, url_prefix='/api/threats')

# Initialize IOC extractor
ioc_extractor = IOCExtractor()


def auto_submit_to_threat_feed(analysis):
    """
    Automatically submit malicious email analysis to threat feed.
    Called internally - no user authentication required.
    Returns the created ThreatEntry or None if duplicate/error.
    """
    try:
        # Extract IOCs
        iocs = ioc_extractor.extract_all_iocs(
            email_from=analysis.email_from,
            email_subject=analysis.email_subject,
            email_body=analysis.email_body
        )

        # Detect brands and threat type
        full_text = f"{analysis.email_subject} {analysis.email_body}"
        detected_brands = ioc_extractor.detect_brands(full_text, analysis.email_from)
        threat_type = ioc_extractor.detect_threat_type(
            analysis.email_subject,
            analysis.email_body,
            detected_brands
        )
        detected_tactics = ioc_extractor.detect_tactics(full_text)

        # Generate threat hash for deduplication
        threat_hash = ioc_extractor.generate_threat_hash(iocs, detected_brands, threat_type)

        # Check for existing entry with same hash
        existing = ThreatEntry.query.filter_by(threat_hash=threat_hash).first()

        if existing:
            # Update existing entry
            existing.similar_submissions += 1
            existing.last_seen = datetime.utcnow()
            db.session.commit()
            return existing  # Return existing, it's a duplicate

        # Create new threat entry
        short_id = ioc_extractor.generate_short_id()

        # Ensure short_id is unique
        while ThreatEntry.query.filter_by(short_id=short_id).first():
            short_id = ioc_extractor.generate_short_id()

        # Sanitize subject
        sanitized_subject = ioc_extractor.sanitize_subject(analysis.email_subject, detected_brands)

        # Create threat entry (anonymous, auto-submitted)
        threat_entry = ThreatEntry(
            threat_hash=threat_hash,
            short_id=short_id,
            source_analysis_id=str(analysis.id),
            submitter_id=None,  # No user - auto submitted
            is_anonymous=True,
            submission_source='auto',
            risk_score=analysis.risk_score,
            classification=analysis.classification,
            sanitized_subject=sanitized_subject,
            detected_tactics=json.dumps(detected_tactics),
            detected_brands=json.dumps(detected_brands),
            threat_type=threat_type,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )

        db.session.add(threat_entry)
        db.session.flush()  # Get the ID

        # Create IOC records
        for ioc in iocs:
            ioc_hash = hashlib.sha256(ioc['value'].lower().encode()).hexdigest()

            # Check if this IOC already exists globally
            existing_ioc = ThreatIOC.query.filter_by(ioc_hash=ioc_hash).first()

            threat_ioc = ThreatIOC(
                threat_entry_id=threat_entry.id,
                ioc_type=ioc['type'],
                ioc_value=ioc['value'],
                ioc_hash=ioc_hash,
                context=ioc.get('context'),
                is_defanged=True,
                ioc_risk_score=ioc.get('risk_score'),
                global_occurrence_count=existing_ioc.global_occurrence_count + 1 if existing_ioc else 1
            )
            db.session.add(threat_ioc)

            # Update global count on existing IOCs with same hash
            if existing_ioc:
                ThreatIOC.query.filter_by(ioc_hash=ioc_hash).update({
                    'global_occurrence_count': ThreatIOC.global_occurrence_count + 1
                })

        db.session.commit()
        return threat_entry

    except Exception as e:
        db.session.rollback()
        print(f"[AutoSubmit] Error: {e}")
        return None


def get_current_user():
    """Helper to get current user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


# =============================================================================
# PUBLIC ENDPOINTS (No Authentication Required)
# =============================================================================

@bp.route('/feed', methods=['GET'])
def get_public_feed():
    """
    GET /api/threats/feed
    Public threat feed - paginated list of recent threats

    Query params:
    - page (default: 1)
    - per_page (default: 20, max: 50)
    - classification: safe|suspicious|malicious
    - threat_type: credential_theft|bec|delivery_scam|etc
    - days: 7|30|90 (default: 30)
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    classification = request.args.get('classification')
    threat_type = request.args.get('threat_type')
    days = request.args.get('days', 30, type=int)

    # Build query
    query = ThreatEntry.query

    # Filter by classification
    if classification:
        query = query.filter(ThreatEntry.classification == classification)

    # Filter by threat type
    if threat_type:
        query = query.filter(ThreatEntry.threat_type == threat_type)

    # Filter by date range
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(ThreatEntry.first_seen >= cutoff)

    # Order by most recent and paginate
    query = query.order_by(ThreatEntry.first_seen.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Check if user is authenticated for enhanced data
    user = get_current_user()
    is_authenticated = user is not None

    # Build response
    threats = []
    for entry in pagination.items:
        if is_authenticated:
            threats.append(entry.to_dict(include_iocs=False, include_submitter=True))
        else:
            threats.append(entry.to_public_dict())

    return jsonify({
        'threats': threats,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'is_authenticated': is_authenticated
    })


@bp.route('/entry/<short_id>', methods=['GET'])
def get_threat_entry(short_id):
    """
    GET /api/threats/entry/<short_id>

    Public view (no auth): Basic info, IOC counts only
    Authenticated view: Full IOC values, submitter info (if not anonymous)
    """
    entry = ThreatEntry.query.filter_by(short_id=short_id).first()

    if not entry:
        return jsonify({'error': 'Threat entry not found'}), 404

    # Increment view count
    entry.increment_view()
    db.session.commit()

    # Check authentication level
    user = get_current_user()
    is_authenticated = user is not None

    if is_authenticated:
        # Full details for authenticated users
        return jsonify({
            'threat': entry.to_dict(include_iocs=True, include_submitter=True),
            'is_authenticated': True,
            'can_vote': True,
            'user_vote': _get_user_vote(entry.id, user.id) if user else None
        })
    else:
        # Limited view for public
        return jsonify({
            'threat': entry.to_public_dict(),
            'is_authenticated': False,
            'ioc_types': _get_ioc_type_counts(entry),
            'message': 'Login to view full IOC details'
        })


@bp.route('/stats', methods=['GET'])
def get_feed_stats():
    """
    GET /api/threats/stats
    Public statistics about the threat feed
    """
    now = datetime.utcnow()

    # Total counts
    total_threats = ThreatEntry.query.count()
    total_iocs = ThreatIOC.query.count()

    # Counts by time period
    threats_24h = ThreatEntry.query.filter(
        ThreatEntry.first_seen >= now - timedelta(hours=24)
    ).count()

    threats_7d = ThreatEntry.query.filter(
        ThreatEntry.first_seen >= now - timedelta(days=7)
    ).count()

    threats_30d = ThreatEntry.query.filter(
        ThreatEntry.first_seen >= now - timedelta(days=30)
    ).count()

    # Classification breakdown
    classification_counts = db.session.query(
        ThreatEntry.classification,
        db.func.count(ThreatEntry.id)
    ).group_by(ThreatEntry.classification).all()

    classifications = {c: count for c, count in classification_counts}

    # Threat type breakdown
    type_counts = db.session.query(
        ThreatEntry.threat_type,
        db.func.count(ThreatEntry.id)
    ).filter(ThreatEntry.threat_type.isnot(None))\
     .group_by(ThreatEntry.threat_type)\
     .order_by(db.func.count(ThreatEntry.id).desc())\
     .limit(10).all()

    threat_types = [{'type': t, 'count': c} for t, c in type_counts]

    # Top impersonated brands (extract from JSON field)
    # Note: This is a simplified version - in production you might want to denormalize this
    recent_entries = ThreatEntry.query.filter(
        ThreatEntry.first_seen >= now - timedelta(days=30)
    ).limit(500).all()

    brand_counts = {}
    for entry in recent_entries:
        if entry.detected_brands:
            try:
                brands = json.loads(entry.detected_brands)
                for brand in brands:
                    brand_counts[brand] = brand_counts.get(brand, 0) + 1
            except:
                pass

    top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return jsonify({
        'total_threats': total_threats,
        'total_iocs': total_iocs,
        'threats_24h': threats_24h,
        'threats_7d': threats_7d,
        'threats_30d': threats_30d,
        'classifications': {
            'safe': classifications.get('safe', 0),
            'suspicious': classifications.get('suspicious', 0),
            'malicious': classifications.get('malicious', 0)
        },
        'threat_types': threat_types,
        'top_brands': [{'brand': b, 'count': c} for b, c in top_brands]
    })


@bp.route('/search', methods=['GET'])
def search_threats():
    """
    GET /api/threats/search?q=<query>

    Search IOCs
    - Public: Check if IOC exists, return yes/no + count
    - Authenticated: Full results with threat entry links
    """
    query = request.args.get('q', '').strip()

    if not query or len(query) < 3:
        return jsonify({'error': 'Query must be at least 3 characters'}), 400

    # Hash the query for IOC lookup
    query_hash = hashlib.sha256(query.lower().encode()).hexdigest()

    # Search in IOC values and hashes
    ioc_matches = ThreatIOC.query.filter(
        db.or_(
            ThreatIOC.ioc_value.ilike(f'%{query}%'),
            ThreatIOC.ioc_hash == query_hash
        )
    ).limit(100).all()

    # Get unique threat entries
    threat_ids = list(set(ioc.threat_entry_id for ioc in ioc_matches))
    threats = ThreatEntry.query.filter(ThreatEntry.id.in_(threat_ids)).all() if threat_ids else []

    user = get_current_user()
    is_authenticated = user is not None

    if is_authenticated:
        # Full results for authenticated users
        return jsonify({
            'query': query,
            'found': len(threats) > 0,
            'match_count': len(threats),
            'threats': [t.to_dict(include_iocs=False, include_submitter=True) for t in threats[:20]],
            'is_authenticated': True
        })
    else:
        # Limited results for public
        return jsonify({
            'query': query,
            'found': len(threats) > 0,
            'match_count': len(threats),
            'message': 'Login to view detailed results',
            'is_authenticated': False
        })


# =============================================================================
# AUTHENTICATED ENDPOINTS
# =============================================================================

@bp.route('/submit', methods=['POST'])
def submit_to_feed():
    """
    POST /api/threats/submit

    Submit an existing analysis to the public threat feed

    Body:
    {
        "analysis_id": "uuid",
        "anonymous": false
    }
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.json or {}
    analysis_id = data.get('analysis_id')
    is_anonymous = data.get('anonymous', False)

    if not analysis_id:
        return jsonify({'error': 'analysis_id is required'}), 400

    # Get the analysis
    analysis = EmailAnalysis.query.get(analysis_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404

    # Extract IOCs
    iocs = ioc_extractor.extract_all_iocs(
        email_from=analysis.email_from,
        email_subject=analysis.email_subject,
        email_body=analysis.email_body
    )

    # Detect brands and threat type
    full_text = f"{analysis.email_subject} {analysis.email_body}"
    detected_brands = ioc_extractor.detect_brands(full_text, analysis.email_from)
    threat_type = ioc_extractor.detect_threat_type(
        analysis.email_subject,
        analysis.email_body,
        detected_brands
    )
    detected_tactics = ioc_extractor.detect_tactics(full_text)

    # Generate threat hash for deduplication
    threat_hash = ioc_extractor.generate_threat_hash(iocs, detected_brands, threat_type)

    # Check for existing entry with same hash
    existing = ThreatEntry.query.filter_by(threat_hash=threat_hash).first()

    if existing:
        # Update existing entry
        existing.similar_submissions += 1
        existing.last_seen = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Similar threat already exists - updated submission count',
            'threat': existing.to_dict(include_iocs=True, include_submitter=not is_anonymous),
            'is_duplicate': True
        })

    # Create new threat entry
    short_id = ioc_extractor.generate_short_id()

    # Ensure short_id is unique
    while ThreatEntry.query.filter_by(short_id=short_id).first():
        short_id = ioc_extractor.generate_short_id()

    # Sanitize subject
    sanitized_subject = ioc_extractor.sanitize_subject(analysis.email_subject, detected_brands)

    # Create threat entry
    threat_entry = ThreatEntry(
        threat_hash=threat_hash,
        short_id=short_id,
        source_analysis_id=analysis_id,
        submitter_id=user.id,
        is_anonymous=is_anonymous,
        submission_source='web',
        risk_score=analysis.risk_score,
        classification=analysis.classification,
        sanitized_subject=sanitized_subject,
        detected_tactics=json.dumps(detected_tactics),
        detected_brands=json.dumps(detected_brands),
        threat_type=threat_type,
        first_seen=datetime.utcnow(),
        last_seen=datetime.utcnow()
    )

    db.session.add(threat_entry)
    db.session.flush()  # Get the ID

    # Create IOC records
    for ioc in iocs:
        ioc_hash = hashlib.sha256(ioc['value'].lower().encode()).hexdigest()

        # Check if this IOC already exists globally
        existing_ioc = ThreatIOC.query.filter_by(ioc_hash=ioc_hash).first()

        threat_ioc = ThreatIOC(
            threat_entry_id=threat_entry.id,
            ioc_type=ioc['type'],
            ioc_value=ioc['value'],
            ioc_hash=ioc_hash,
            context=ioc.get('context'),
            is_defanged=True,
            ioc_risk_score=ioc.get('risk_score'),
            global_occurrence_count=existing_ioc.global_occurrence_count + 1 if existing_ioc else 1
        )
        db.session.add(threat_ioc)

        # Update global count on existing IOCs with same hash
        if existing_ioc:
            ThreatIOC.query.filter_by(ioc_hash=ioc_hash).update({
                'global_occurrence_count': ThreatIOC.global_occurrence_count + 1
            })

    db.session.commit()

    return jsonify({
        'message': 'Successfully submitted to threat feed',
        'threat': threat_entry.to_dict(include_iocs=True, include_submitter=not is_anonymous),
        'short_id': short_id,
        'url': f'/threats/{short_id}',
        'is_duplicate': False
    }), 201


@bp.route('/entry/<short_id>/vote', methods=['POST'])
def vote_on_threat(short_id):
    """
    POST /api/threats/entry/<short_id>/vote
    Body: {"vote": "phishing|safe"}
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.json or {}
    vote_type = data.get('vote')

    if vote_type not in ('phishing', 'safe'):
        return jsonify({'error': 'Vote must be "phishing" or "safe"'}), 400

    # Get threat entry
    entry = ThreatEntry.query.filter_by(short_id=short_id).first()
    if not entry:
        return jsonify({'error': 'Threat entry not found'}), 404

    # Check for existing vote
    existing_vote = ThreatVote.query.filter_by(
        threat_entry_id=entry.id,
        user_id=user.id
    ).first()

    if existing_vote:
        # Update existing vote
        old_vote = existing_vote.vote_type

        if old_vote == vote_type:
            return jsonify({'message': 'Vote unchanged', 'vote': vote_type})

        # Update counts
        if old_vote == 'phishing':
            entry.community_votes_phishing -= 1
        else:
            entry.community_votes_safe -= 1

        if vote_type == 'phishing':
            entry.community_votes_phishing += 1
        else:
            entry.community_votes_safe += 1

        existing_vote.vote_type = vote_type
        existing_vote.created_at = datetime.utcnow()
    else:
        # Create new vote
        new_vote = ThreatVote(
            threat_entry_id=entry.id,
            user_id=user.id,
            vote_type=vote_type
        )
        db.session.add(new_vote)

        if vote_type == 'phishing':
            entry.community_votes_phishing += 1
        else:
            entry.community_votes_safe += 1

    db.session.commit()

    return jsonify({
        'message': 'Vote recorded',
        'vote': vote_type,
        'community_votes': {
            'phishing': entry.community_votes_phishing,
            'safe': entry.community_votes_safe
        }
    })


@bp.route('/my-submissions', methods=['GET'])
def get_my_submissions():
    """
    GET /api/threats/my-submissions
    Get current user's threat submissions
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)

    query = ThreatEntry.query.filter_by(submitter_id=user.id)\
        .order_by(ThreatEntry.first_seen.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'submissions': [t.to_dict(include_iocs=False, include_submitter=True) for t in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_ioc_type_counts(entry: ThreatEntry) -> dict:
    """Get counts of IOC types for an entry (for public view)"""
    counts = {}
    for ioc in entry.iocs:
        counts[ioc.ioc_type] = counts.get(ioc.ioc_type, 0) + 1
    return counts


def _get_user_vote(threat_entry_id: str, user_id: str) -> str:
    """Get user's vote on a threat entry"""
    vote = ThreatVote.query.filter_by(
        threat_entry_id=threat_entry_id,
        user_id=user_id
    ).first()
    return vote.vote_type if vote else None
