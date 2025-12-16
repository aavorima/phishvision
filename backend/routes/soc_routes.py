from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from database import db
from models import SecurityIncident, Campaign, CampaignTarget

bp = Blueprint('soc', __name__, url_prefix='/api/soc')


@bp.route('/incidents', methods=['GET'])
def get_incidents():
    """Get all security incidents with optional filters"""
    status = request.args.get('status')
    severity = request.args.get('severity')
    incident_type = request.args.get('type')
    days = request.args.get('days', type=int, default=30)

    query = SecurityIncident.query

    if status:
        query = query.filter(SecurityIncident.status == status)
    if severity:
        query = query.filter(SecurityIncident.severity == severity)
    if incident_type:
        query = query.filter(SecurityIncident.type == incident_type)
    if days:
        since = datetime.utcnow() - timedelta(days=days)
        query = query.filter(SecurityIncident.detected_at >= since)

    incidents = query.order_by(SecurityIncident.detected_at.desc()).all()

    return jsonify({
        'incidents': [i.to_dict() for i in incidents],
        'total': len(incidents)
    })


@bp.route('/incidents/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Get a single incident by ID"""
    incident = SecurityIncident.query.get_or_404(incident_id)
    return jsonify(incident.to_dict())


@bp.route('/incidents', methods=['POST'])
def create_incident():
    """Create a new security incident"""
    data = request.get_json()

    if not data.get('type') or not data.get('description'):
        return jsonify({'error': 'type and description are required'}), 400

    incident = SecurityIncident(
        type=data['type'],
        severity=data.get('severity', 'medium'),
        description=data['description'],
        user_email=data.get('user_email'),
        campaign_id=data.get('campaign_id'),
        assigned_to=data.get('assigned_to')
    )

    db.session.add(incident)
    db.session.commit()

    return jsonify(incident.to_dict()), 201


@bp.route('/incidents/<incident_id>/status', methods=['PUT'])
def update_incident_status(incident_id):
    """Update incident status and timeline"""
    incident = SecurityIncident.query.get_or_404(incident_id)
    data = request.get_json()

    new_status = data.get('status')
    valid_statuses = ['detected', 'investigating', 'contained', 'resolved']

    if new_status and new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

    if new_status:
        incident.status = new_status
        now = datetime.utcnow()

        # Update timeline based on status
        if new_status == 'investigating' and not incident.acknowledged_at:
            incident.acknowledged_at = now
        elif new_status == 'contained' and not incident.contained_at:
            incident.contained_at = now
        elif new_status == 'resolved' and not incident.resolved_at:
            incident.resolved_at = now

    if data.get('response_notes'):
        incident.response_notes = data['response_notes']

    if data.get('assigned_to'):
        incident.assigned_to = data['assigned_to']

    if data.get('severity'):
        incident.severity = data['severity']

    db.session.commit()

    return jsonify(incident.to_dict())


@bp.route('/incidents/<incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    """Delete an incident"""
    incident = SecurityIncident.query.get_or_404(incident_id)
    db.session.delete(incident)
    db.session.commit()

    return jsonify({'message': 'Incident deleted successfully'})


@bp.route('/timeline', methods=['GET'])
def get_timeline():
    """Get incidents formatted for timeline visualization"""
    days = request.args.get('days', type=int, default=30)
    since = datetime.utcnow() - timedelta(days=days)

    incidents = SecurityIncident.query.filter(
        SecurityIncident.detected_at >= since
    ).order_by(SecurityIncident.detected_at.desc()).all()

    timeline = []
    for incident in incidents:
        timeline.append({
            'id': incident.id,
            'type': incident.type,
            'severity': incident.severity,
            'status': incident.status,
            'description': incident.description,
            'user_email': incident.user_email,
            'detected_at': incident.detected_at.isoformat() if incident.detected_at else None,
            'acknowledged_at': incident.acknowledged_at.isoformat() if incident.acknowledged_at else None,
            'contained_at': incident.contained_at.isoformat() if incident.contained_at else None,
            'resolved_at': incident.resolved_at.isoformat() if incident.resolved_at else None,
            'response_time_minutes': incident._calculate_response_time()
        })

    return jsonify({
        'timeline': timeline,
        'total': len(timeline)
    })


@bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get SOC metrics: MTTD, MTTR, incident counts, etc."""
    days = request.args.get('days', type=int, default=30)
    since = datetime.utcnow() - timedelta(days=days)

    # Get all incidents in timeframe
    incidents = SecurityIncident.query.filter(
        SecurityIncident.detected_at >= since
    ).all()

    total_incidents = len(incidents)
    resolved_incidents = [i for i in incidents if i.resolved_at]
    active_incidents = [i for i in incidents if i.status != 'resolved']

    # Calculate MTTR (Mean Time to Resolve)
    mttr = 0
    if resolved_incidents:
        total_response_time = sum(
            (i.resolved_at - i.detected_at).total_seconds() / 60
            for i in resolved_incidents
        )
        mttr = round(total_response_time / len(resolved_incidents), 2)

    # Calculate MTTD (Mean Time to Detect) - using acknowledged_at as proxy
    mttd = 0
    acknowledged = [i for i in incidents if i.acknowledged_at]
    if acknowledged:
        total_detect_time = sum(
            (i.acknowledged_at - i.detected_at).total_seconds() / 60
            for i in acknowledged
        )
        mttd = round(total_detect_time / len(acknowledged), 2)

    # Count by severity
    severity_counts = {
        'critical': len([i for i in incidents if i.severity == 'critical']),
        'high': len([i for i in incidents if i.severity == 'high']),
        'medium': len([i for i in incidents if i.severity == 'medium']),
        'low': len([i for i in incidents if i.severity == 'low'])
    }

    # Count by status
    status_counts = {
        'detected': len([i for i in incidents if i.status == 'detected']),
        'investigating': len([i for i in incidents if i.status == 'investigating']),
        'contained': len([i for i in incidents if i.status == 'contained']),
        'resolved': len([i for i in incidents if i.status == 'resolved'])
    }

    # Count by type
    type_counts = {}
    for incident in incidents:
        type_counts[incident.type] = type_counts.get(incident.type, 0) + 1

    # Resolution rate
    resolution_rate = round((len(resolved_incidents) / total_incidents * 100), 1) if total_incidents > 0 else 0

    # Security posture score (inverse of incident severity weighted average)
    if total_incidents > 0:
        severity_weights = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        weighted_sum = sum(severity_weights.get(i.severity, 2) for i in active_incidents)
        max_possible = len(active_incidents) * 4 if active_incidents else 1
        posture_score = round(100 - (weighted_sum / max_possible * 100), 1)
    else:
        posture_score = 100  # Perfect score if no incidents

    return jsonify({
        'total_incidents': total_incidents,
        'active_incidents': len(active_incidents),
        'resolved_incidents': len(resolved_incidents),
        'mttr_minutes': mttr,
        'mttd_minutes': mttd,
        'resolution_rate': resolution_rate,
        'security_posture_score': posture_score,
        'severity_counts': severity_counts,
        'status_counts': status_counts,
        'type_counts': type_counts,
        'period_days': days
    })


@bp.route('/auto-create-from-click', methods=['POST'])
def auto_create_from_click():
    """Automatically create incident when a phishing link is clicked (called from tracking)"""
    data = request.get_json()

    campaign_id = data.get('campaign_id')
    user_email = data.get('user_email')
    ip_address = data.get('ip_address')

    # Determine severity based on context
    severity = 'high'  # Clicking a phishing link is serious

    incident = SecurityIncident(
        type='phishing_click',
        severity=severity,
        description=f'User clicked on phishing link from campaign',
        user_email=user_email,
        campaign_id=campaign_id
    )

    db.session.add(incident)
    db.session.commit()

    return jsonify(incident.to_dict()), 201
