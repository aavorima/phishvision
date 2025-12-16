from flask import Blueprint, request, jsonify
from datetime import datetime
from database import db
from models import UserRiskScore, CampaignTarget

bp = Blueprint('risk', __name__, url_prefix='/api/risk')


@bp.route('/users', methods=['GET'])
def get_all_risk_scores():
    """Get all users with their risk scores"""
    department = request.args.get('department')
    risk_level = request.args.get('risk_level')
    sort_by = request.args.get('sort_by', 'risk_score')
    order = request.args.get('order', 'desc')

    query = UserRiskScore.query

    if department:
        query = query.filter(UserRiskScore.department == department)
    if risk_level:
        query = query.filter(UserRiskScore.risk_level == risk_level)

    # Sorting
    if sort_by == 'risk_score':
        query = query.order_by(UserRiskScore.risk_score.desc() if order == 'desc' else UserRiskScore.risk_score.asc())
    elif sort_by == 'email':
        query = query.order_by(UserRiskScore.email.desc() if order == 'desc' else UserRiskScore.email.asc())
    elif sort_by == 'updated_at':
        query = query.order_by(UserRiskScore.updated_at.desc() if order == 'desc' else UserRiskScore.updated_at.asc())

    users = query.all()

    return jsonify({
        'users': [u.to_dict() for u in users],
        'total': len(users)
    })


@bp.route('/users/<user_id>', methods=['GET'])
def get_user_risk(user_id):
    """Get risk score for a specific user"""
    user = UserRiskScore.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@bp.route('/users/email/<email>', methods=['GET'])
def get_user_risk_by_email(email):
    """Get risk score by email address"""
    user = UserRiskScore.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


@bp.route('/users', methods=['POST'])
def create_or_update_user():
    """Create or update a user's risk profile"""
    data = request.get_json()

    if not data.get('email'):
        return jsonify({'error': 'email is required'}), 400

    user = UserRiskScore.query.filter_by(email=data['email']).first()

    if not user:
        user = UserRiskScore(email=data['email'])
        db.session.add(user)

    if data.get('department'):
        user.department = data['department']

    db.session.commit()

    return jsonify(user.to_dict()), 201


@bp.route('/users/<user_id>', methods=['PUT'])
def update_user_risk(user_id):
    """Update user risk profile"""
    user = UserRiskScore.query.get_or_404(user_id)
    data = request.get_json()

    if data.get('department'):
        user.department = data['department']
    if data.get('campaigns_received') is not None:
        user.campaigns_received = data['campaigns_received']
    if data.get('campaigns_opened') is not None:
        user.campaigns_opened = data['campaigns_opened']
    if data.get('campaigns_clicked') is not None:
        user.campaigns_clicked = data['campaigns_clicked']
    if data.get('training_completed') is not None:
        user.training_completed = data['training_completed']
    if data.get('training_passed') is not None:
        user.training_passed = data['training_passed']

    # Recalculate risk score
    user.calculate_risk_score()

    db.session.commit()

    return jsonify(user.to_dict())


@bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user's risk profile"""
    user = UserRiskScore.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})


@bp.route('/recalculate-all', methods=['POST'])
def recalculate_all_scores():
    """Recalculate risk scores for all users based on campaign data"""
    # Get all unique emails from campaign targets
    targets = CampaignTarget.query.all()

    # Group by email
    email_stats = {}
    for target in targets:
        if target.email not in email_stats:
            email_stats[target.email] = {
                'received': 0,
                'opened': 0,
                'clicked': 0
            }
        email_stats[target.email]['received'] += 1
        if target.opened_at:
            email_stats[target.email]['opened'] += 1
        if target.clicked_at:
            email_stats[target.email]['clicked'] += 1

    # Update or create UserRiskScore for each email
    updated_count = 0
    for email, stats in email_stats.items():
        user = UserRiskScore.query.filter_by(email=email).first()
        if not user:
            user = UserRiskScore(email=email)
            db.session.add(user)

        user.campaigns_received = stats['received']
        user.campaigns_opened = stats['opened']
        user.campaigns_clicked = stats['clicked']
        user.calculate_risk_score()
        updated_count += 1

    db.session.commit()

    return jsonify({
        'message': f'Recalculated risk scores for {updated_count} users',
        'users_updated': updated_count
    })


@bp.route('/stats', methods=['GET'])
def get_risk_stats():
    """Get overall risk statistics"""
    users = UserRiskScore.query.all()

    if not users:
        return jsonify({
            'total_users': 0,
            'average_risk_score': 0,
            'risk_level_distribution': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
            'department_stats': {},
            'top_risk_users': [],
            'total_campaigns_sent': 0,
            'total_opens': 0,
            'total_clicks': 0
        })

    total_users = len(users)
    avg_risk = round(sum(u.risk_score for u in users) / total_users, 2)

    # Risk level distribution
    risk_distribution = {
        'low': len([u for u in users if u.risk_level == 'low']),
        'medium': len([u for u in users if u.risk_level == 'medium']),
        'high': len([u for u in users if u.risk_level == 'high']),
        'critical': len([u for u in users if u.risk_level == 'critical'])
    }

    # Department statistics
    department_stats = {}
    for user in users:
        dept = user.department or 'Unknown'
        if dept not in department_stats:
            department_stats[dept] = {
                'count': 0,
                'total_risk': 0,
                'risk_levels': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            }
        department_stats[dept]['count'] += 1
        department_stats[dept]['total_risk'] += user.risk_score
        department_stats[dept]['risk_levels'][user.risk_level] += 1

    # Calculate average risk per department
    for dept in department_stats:
        count = department_stats[dept]['count']
        department_stats[dept]['average_risk'] = round(department_stats[dept]['total_risk'] / count, 2)

    # Top 10 highest risk users
    top_risk_users = sorted(users, key=lambda u: u.risk_score, reverse=True)[:10]

    # Totals
    total_sent = sum(u.campaigns_received for u in users)
    total_opens = sum(u.campaigns_opened for u in users)
    total_clicks = sum(u.campaigns_clicked for u in users)

    return jsonify({
        'total_users': total_users,
        'average_risk_score': avg_risk,
        'risk_level_distribution': risk_distribution,
        'department_stats': department_stats,
        'top_risk_users': [u.to_dict() for u in top_risk_users],
        'total_campaigns_sent': total_sent,
        'total_opens': total_opens,
        'total_clicks': total_clicks,
        'overall_open_rate': round((total_opens / total_sent * 100), 1) if total_sent > 0 else 0,
        'overall_click_rate': round((total_clicks / total_sent * 100), 1) if total_sent > 0 else 0
    })


@bp.route('/departments', methods=['GET'])
def get_departments():
    """Get list of all departments"""
    users = UserRiskScore.query.filter(UserRiskScore.department.isnot(None)).all()
    departments = list(set(u.department for u in users if u.department))
    return jsonify({'departments': sorted(departments)})


@bp.route('/heatmap', methods=['GET'])
def get_department_heatmap():
    """Get department risk heatmap data"""
    users = UserRiskScore.query.all()

    heatmap_data = {}
    for user in users:
        dept = user.department or 'Unknown'
        if dept not in heatmap_data:
            heatmap_data[dept] = {
                'department': dept,
                'user_count': 0,
                'total_risk': 0,
                'low': 0,
                'medium': 0,
                'high': 0,
                'critical': 0
            }
        heatmap_data[dept]['user_count'] += 1
        heatmap_data[dept]['total_risk'] += user.risk_score
        heatmap_data[dept][user.risk_level] += 1

    # Calculate averages and format output
    result = []
    for dept, data in heatmap_data.items():
        data['average_risk'] = round(data['total_risk'] / data['user_count'], 2)
        del data['total_risk']
        result.append(data)

    # Sort by average risk descending
    result.sort(key=lambda x: x['average_risk'], reverse=True)

    return jsonify({'heatmap': result})


@bp.route('/update-from-tracking', methods=['POST'])
def update_from_tracking():
    """Update user risk when they interact with a campaign (called from tracking)"""
    data = request.get_json()

    email = data.get('email')
    action = data.get('action')  # 'opened' or 'clicked'

    if not email or not action:
        return jsonify({'error': 'email and action are required'}), 400

    user = UserRiskScore.query.filter_by(email=email).first()
    if not user:
        user = UserRiskScore(email=email)
        db.session.add(user)

    user.campaigns_received += 1
    if action == 'opened':
        user.campaigns_opened += 1
    elif action == 'clicked':
        user.campaigns_clicked += 1
        user.last_incident_at = datetime.utcnow()

    user.calculate_risk_score()
    db.session.commit()

    return jsonify(user.to_dict())
