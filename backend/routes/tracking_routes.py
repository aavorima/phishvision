from flask import Blueprint, request, send_file, send_from_directory
from database import db
from models import CampaignTarget, ScheduledCampaign, Employee
from datetime import datetime
import io
import os

bp = Blueprint('tracking', __name__, url_prefix='/api/track')

# Path to static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')

# 1x1 transparent pixel for tracking email opens
TRACKING_PIXEL = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'


def _detect_device_type(user_agent: str) -> str:
    """Detect device type from user agent string"""
    ua_lower = user_agent.lower()
    if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
        return 'mobile'
    elif 'tablet' in ua_lower or 'ipad' in ua_lower:
        return 'tablet'
    return 'desktop'


def _update_vulnerability_profile(tracking_token: str, interaction_type: str, device_type: str = None):
    """Update vulnerability profile if this is from a campaign program"""
    try:
        # Check if this target is linked to a scheduled campaign (profiling program)
        target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()
        if not target:
            return

        scheduled = ScheduledCampaign.query.filter_by(target_id=target.id).first()
        if not scheduled:
            return  # Not a profiling program campaign

        # Import here to avoid circular imports
        from services.campaign_program_service import CampaignProgramService
        program_service = CampaignProgramService()

        program_service.record_interaction(
            tracking_token=tracking_token,
            interaction_type=interaction_type,
            device_type=device_type
        )
    except Exception as e:
        # Log but don't fail the tracking
        print(f"[TRACKING] Error updating vulnerability profile: {e}")


@bp.route('/open/<tracking_token>')
def track_open(tracking_token):
    """Track email open via pixel"""
    target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()

    if target and not target.opened_at:
        target.opened_at = datetime.utcnow()
        target.ip_address = request.remote_addr
        target.user_agent = request.headers.get('User-Agent', '')

        # Update HVS score for email open
        employee = Employee.query.filter_by(email=target.email).first()
        if employee:
            employee.update_hvs('opened_email')

        db.session.commit()

        # Update vulnerability profile if from a program
        device_type = _detect_device_type(target.user_agent or '')
        _update_vulnerability_profile(tracking_token, 'open', device_type)

    # Return 1x1 transparent GIF
    return send_file(
        io.BytesIO(TRACKING_PIXEL),
        mimetype='image/gif',
        as_attachment=False,
        download_name='pixel.gif'
    )

@bp.route('/click/<tracking_token>')
def track_click(tracking_token):
    """Track link click and show training page"""
    target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()

    device_type = None
    if target:
        # Record click (clicking implies opening, so set both)
        if not target.clicked_at:
            target.clicked_at = datetime.utcnow()

        # If they clicked, they must have opened the email
        if not target.opened_at:
            target.opened_at = datetime.utcnow()

        # Update IP and user agent if not already set
        if not target.ip_address:
            target.ip_address = request.remote_addr
            target.user_agent = request.headers.get('User-Agent', '')

        # Update HVS score for link click
        employee = Employee.query.filter_by(email=target.email).first()
        if employee:
            employee.update_hvs('clicked_link')

        db.session.commit()

        # Update vulnerability profile if from a program
        device_type = _detect_device_type(target.user_agent or request.headers.get('User-Agent', ''))
        _update_vulnerability_profile(tracking_token, 'click', device_type)

    # Serve the training/awareness page
    return send_from_directory(STATIC_DIR, 'training.html')


@bp.route('/c/<tracking_token>')
def track_click_short(tracking_token):
    """Short URL for click tracking - redirects to main click handler"""
    return track_click(tracking_token)

@bp.route('/stats/<campaign_id>')
def get_campaign_stats(campaign_id):
    """Get tracking stats for a campaign"""
    from models import Campaign
    campaign = Campaign.query.get_or_404(campaign_id)

    targets = campaign.targets
    total = len(targets)
    opened = sum(1 for t in targets if t.opened_at)
    clicked = sum(1 for t in targets if t.clicked_at)

    return {
        'campaign_id': campaign_id,
        'total_sent': total,
        'opened': opened,
        'clicked': clicked,
        'open_rate': round((opened / total * 100) if total > 0 else 0, 2),
        'click_rate': round((clicked / total * 100) if total > 0 else 0, 2)
    }
