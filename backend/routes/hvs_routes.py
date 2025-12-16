"""
Human Vulnerability Score (HVS) Routes
Track and manage employee vulnerability scores
"""

from flask import Blueprint, request, jsonify
from database import db
from models import Employee, HVSEvent
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('hvs', __name__, url_prefix='/api/hvs')


@bp.route('/employees', methods=['GET'])
def get_employee_hvs_scores():
    """Get HVS scores for all employees"""
    department = request.args.get('department')
    min_score = request.args.get('min_score', type=int)
    max_score = request.args.get('max_score', type=int)
    level = request.args.get('level')  # low, medium, high, critical

    query = Employee.query.filter_by(is_active=True)

    if department:
        query = query.filter_by(department=department)

    if min_score is not None:
        query = query.filter(Employee.hvs_score >= min_score)

    if max_score is not None:
        query = query.filter(Employee.hvs_score <= max_score)

    employees = query.order_by(Employee.hvs_score.desc()).all()

    # Filter by level if specified
    if level:
        employees = [e for e in employees if e.get_hvs_level() == level]

    results = []
    for emp in employees:
        results.append({
            'id': emp.id,
            'email': emp.email,
            'full_name': f"{emp.first_name} {emp.last_name}",
            'department': emp.department,
            'job_title': emp.job_title,
            'hvs_score': emp.hvs_score,
            'hvs_level': emp.get_hvs_level(),
            'hvs_last_updated': emp.hvs_last_updated.isoformat() if emp.hvs_last_updated else None
        })

    return jsonify(results)


@bp.route('/employees/<employee_id>', methods=['GET'])
def get_employee_hvs_detail(employee_id):
    """Get detailed HVS information for a specific employee"""
    employee = Employee.query.get_or_404(employee_id)

    # Get recent HVS events
    recent_events = HVSEvent.query.filter_by(
        employee_id=employee_id
    ).order_by(HVSEvent.event_time.desc()).limit(20).all()

    return jsonify({
        'employee': employee.to_dict(),
        'hvs_score': employee.hvs_score,
        'hvs_level': employee.get_hvs_level(),
        'hvs_last_updated': employee.hvs_last_updated.isoformat() if employee.hvs_last_updated else None,
        'recent_events': [event.to_dict() for event in recent_events]
    })


@bp.route('/employees/<employee_id>/events', methods=['GET'])
def get_employee_hvs_events(employee_id):
    """Get all HVS events for an employee"""
    employee = Employee.query.get_or_404(employee_id)

    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    events = HVSEvent.query.filter_by(
        employee_id=employee_id
    ).order_by(HVSEvent.event_time.desc()).limit(limit).offset(offset).all()

    total_count = HVSEvent.query.filter_by(employee_id=employee_id).count()

    return jsonify({
        'events': [event.to_dict() for event in events],
        'total': total_count,
        'limit': limit,
        'offset': offset
    })


@bp.route('/employees/<employee_id>/manual-update', methods=['POST'])
def manual_hvs_update(employee_id):
    """Manually update HVS score (for training completion, reporting, etc.)"""
    employee = Employee.query.get_or_404(employee_id)
    data = request.json

    event_type = data.get('event_type')
    notes = data.get('notes')

    # Validate event_type
    valid_events = ['watched_training', 'reported_phishing', 'clicked_link',
                    'submitted_credentials', 'clicked_sms', 'opened_email']

    if event_type not in valid_events:
        return jsonify({'error': f'Invalid event_type. Must be one of: {", ".join(valid_events)}'}), 400

    # Update HVS
    old_score = employee.hvs_score
    employee.update_hvs(event_type)

    # Add notes to the latest event
    if notes:
        latest_event = HVSEvent.query.filter_by(
            employee_id=employee_id
        ).order_by(HVSEvent.event_time.desc()).first()
        if latest_event:
            latest_event.notes = notes

    db.session.commit()

    return jsonify({
        'success': True,
        'employee_id': employee.id,
        'event_type': event_type,
        'old_score': old_score,
        'new_score': employee.hvs_score,
        'score_change': employee.hvs_score - old_score,
        'hvs_level': employee.get_hvs_level()
    })


@bp.route('/departments', methods=['GET'])
def get_department_hvs_scores():
    """Get HVS scores aggregated by department"""
    # Get all departments with active employees
    departments = db.session.query(
        Employee.department,
        func.count(Employee.id).label('employee_count'),
        func.avg(Employee.hvs_score).label('avg_hvs_score'),
        func.min(Employee.hvs_score).label('min_hvs_score'),
        func.max(Employee.hvs_score).label('max_hvs_score')
    ).filter(
        Employee.is_active == True,
        Employee.department.isnot(None)
    ).group_by(Employee.department).all()

    results = []
    for dept in departments:
        avg_score = round(dept.avg_hvs_score, 1) if dept.avg_hvs_score else 0

        # Determine level based on average score
        if avg_score >= 75:
            level = 'critical'
        elif avg_score >= 50:
            level = 'high'
        elif avg_score >= 25:
            level = 'medium'
        else:
            level = 'low'

        results.append({
            'department': dept.department,
            'employee_count': dept.employee_count,
            'avg_hvs_score': avg_score,
            'min_hvs_score': int(dept.min_hvs_score) if dept.min_hvs_score else 0,
            'max_hvs_score': int(dept.max_hvs_score) if dept.max_hvs_score else 0,
            'hvs_level': level
        })

    # Sort by average score (highest risk first)
    results.sort(key=lambda x: x['avg_hvs_score'], reverse=True)

    return jsonify(results)


@bp.route('/departments/<department_name>', methods=['GET'])
def get_department_hvs_detail(department_name):
    """Get detailed HVS information for a specific department"""
    employees = Employee.query.filter_by(
        department=department_name,
        is_active=True
    ).order_by(Employee.hvs_score.desc()).all()

    if not employees:
        return jsonify({'error': 'Department not found or has no active employees'}), 404

    # Calculate department statistics
    scores = [e.hvs_score for e in employees]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Count by level
    levels = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    for emp in employees:
        levels[emp.get_hvs_level()] += 1

    return jsonify({
        'department': department_name,
        'employee_count': len(employees),
        'avg_hvs_score': round(avg_score, 1),
        'min_hvs_score': min(scores) if scores else 0,
        'max_hvs_score': max(scores) if scores else 0,
        'level_distribution': levels,
        'employees': [
            {
                'id': e.id,
                'email': e.email,
                'full_name': f"{e.first_name} {e.last_name}",
                'job_title': e.job_title,
                'hvs_score': e.hvs_score,
                'hvs_level': e.get_hvs_level(),
                'hvs_last_updated': e.hvs_last_updated.isoformat() if e.hvs_last_updated else None
            }
            for e in employees
        ]
    })


@bp.route('/stats', methods=['GET'])
def get_hvs_stats():
    """Get overall HVS statistics"""
    # Total employees
    total_employees = Employee.query.filter_by(is_active=True).count()

    # Average score
    avg_score_result = db.session.query(func.avg(Employee.hvs_score)).filter(
        Employee.is_active == True
    ).scalar()
    avg_score = round(avg_score_result, 1) if avg_score_result else 0

    # Count by level
    employees = Employee.query.filter_by(is_active=True).all()
    levels = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    for emp in employees:
        levels[emp.get_hvs_level()] += 1

    # Recent events (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_events = HVSEvent.query.filter(
        HVSEvent.event_time >= week_ago
    ).count()

    # Top 5 highest risk employees
    high_risk_employees = Employee.query.filter_by(
        is_active=True
    ).order_by(Employee.hvs_score.desc()).limit(5).all()

    return jsonify({
        'total_employees': total_employees,
        'avg_hvs_score': avg_score,
        'level_distribution': levels,
        'recent_events_7d': recent_events,
        'high_risk_employees': [
            {
                'id': e.id,
                'email': e.email,
                'full_name': f"{e.first_name} {e.last_name}",
                'department': e.department,
                'hvs_score': e.hvs_score,
                'hvs_level': e.get_hvs_level()
            }
            for e in high_risk_employees
        ]
    })


@bp.route('/events/recent', methods=['GET'])
def get_recent_hvs_events():
    """Get recent HVS events across all employees"""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    event_type = request.args.get('event_type')

    query = HVSEvent.query

    if event_type:
        query = query.filter_by(event_type=event_type)

    events = query.order_by(HVSEvent.event_time.desc()).limit(limit).offset(offset).all()
    total_count = query.count()

    # Include employee info
    results = []
    for event in events:
        event_dict = event.to_dict()
        if event.employee:
            event_dict['employee'] = {
                'email': event.employee.email,
                'full_name': f"{event.employee.first_name} {event.employee.last_name}",
                'department': event.employee.department
            }
        results.append(event_dict)

    return jsonify({
        'events': results,
        'total': total_count,
        'limit': limit,
        'offset': offset
    })
