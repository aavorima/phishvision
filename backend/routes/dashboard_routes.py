from flask import Blueprint, jsonify
from database import db
from models import Campaign, CampaignTarget, EmailAnalysis
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""

    # Campaign stats
    total_campaigns = Campaign.query.count()
    active_campaigns = Campaign.query.filter_by(status='active').count()

    # Target/email stats
    total_targets = CampaignTarget.query.count()
    total_opens = CampaignTarget.query.filter(CampaignTarget.opened_at.isnot(None)).count()
    total_clicks = CampaignTarget.query.filter(CampaignTarget.clicked_at.isnot(None)).count()

    # Analysis stats
    total_analyzed = EmailAnalysis.query.count()
    malicious_detected = EmailAnalysis.query.filter_by(classification='malicious').count()
    suspicious_detected = EmailAnalysis.query.filter_by(classification='suspicious').count()
    safe_emails = EmailAnalysis.query.filter_by(classification='safe').count()

    # Calculate rates
    open_rate = round((total_opens / total_targets * 100) if total_targets > 0 else 0, 2)
    click_rate = round((total_clicks / total_targets * 100) if total_targets > 0 else 0, 2)
    threat_detection_rate = round(
        ((malicious_detected + suspicious_detected) / total_analyzed * 100) if total_analyzed > 0 else 0,
        2
    )

    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_campaigns = Campaign.query.filter(Campaign.created_at >= week_ago).count()
    recent_analyses = EmailAnalysis.query.filter(EmailAnalysis.analyzed_at >= week_ago).count()

    return jsonify({
        'campaigns': {
            'total': total_campaigns,
            'active': active_campaigns,
            'recent': recent_campaigns
        },
        'phishing_simulation': {
            'total_sent': total_targets,
            'total_opened': total_opens,
            'total_clicked': total_clicks,
            'open_rate': open_rate,
            'click_rate': click_rate
        },
        'email_analysis': {
            'total_analyzed': total_analyzed,
            'safe': safe_emails,
            'suspicious': suspicious_detected,
            'malicious': malicious_detected,
            'threat_detection_rate': threat_detection_rate,
            'recent': recent_analyses
        },
        'summary': {
            'total_emails_processed': total_targets + total_analyzed,
            'security_incidents': malicious_detected,
            'awareness_level': 100 - click_rate if click_rate < 100 else 0
        }
    })

@bp.route('/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get recent activity across all systems"""

    activities = []

    # Recent campaigns
    recent_campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(5).all()
    for campaign in recent_campaigns:
        activities.append({
            'type': 'campaign_created',
            'timestamp': campaign.created_at.isoformat(),
            'description': f'Campaign "{campaign.name}" created with {len(campaign.targets)} targets',
            'data': campaign.to_dict()
        })

    # Recent email analyses
    recent_analyses = EmailAnalysis.query.order_by(EmailAnalysis.analyzed_at.desc()).limit(5).all()
    for analysis in recent_analyses:
        activities.append({
            'type': 'email_analyzed',
            'timestamp': analysis.analyzed_at.isoformat(),
            'description': f'Email from {analysis.email_from} classified as {analysis.classification}',
            'data': {
                'id': analysis.id,
                'classification': analysis.classification,
                'risk_score': analysis.risk_score
            }
        })

    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return jsonify(activities[:10])

@bp.route('/campaign-performance', methods=['GET'])
def get_campaign_performance():
    """Get performance metrics for all campaigns"""

    campaigns = Campaign.query.all()
    performance_data = []

    for campaign in campaigns:
        total = len(campaign.targets)
        opened = sum(1 for t in campaign.targets if t.opened_at)
        clicked = sum(1 for t in campaign.targets if t.clicked_at)

        performance_data.append({
            'id': campaign.id,
            'name': campaign.name,
            'template_type': campaign.template_type,
            'created_at': campaign.created_at.isoformat(),
            'total_sent': total,
            'opened': opened,
            'clicked': clicked,
            'open_rate': round((opened / total * 100) if total > 0 else 0, 2),
            'click_rate': round((clicked / total * 100) if total > 0 else 0, 2)
        })

    return jsonify(performance_data)

@bp.route('/threat-distribution', methods=['GET'])
def get_threat_distribution():
    """Get distribution of threat classifications"""

    distribution = db.session.query(
        EmailAnalysis.classification,
        func.count(EmailAnalysis.id).label('count')
    ).group_by(EmailAnalysis.classification).all()

    result = {
        'safe': 0,
        'suspicious': 0,
        'malicious': 0
    }

    for classification, count in distribution:
        result[classification] = count

    return jsonify(result)
