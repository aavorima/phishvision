from flask import Blueprint, request, jsonify, session
from database import db
from models import Campaign, CampaignTarget, CustomTemplate, LandingPage, Settings, User, CredentialCapture, ScheduledCampaign
from services.email_service import EmailService
from services.email_parser import parse_email_to_name, substitute_template_variables
import json
import uuid
import os

bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


def get_current_user():
    """Helper to get current user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


def get_email_service_for_user(user):
    """
    Get EmailService configured with user's SMTP settings.
    Does NOT fall back to .env - user must configure SMTP in Settings.
    """
    if not user:
        # No user logged in, return unconfigured service
        return EmailService(smtp_username=None, smtp_password=None)

    # Get user's settings from database
    settings = Settings.query.filter_by(user_id=user.id).first()

    # Create email service from user settings (no .env fallback)
    return EmailService.from_user_settings(settings, allow_env_fallback=False)


@bp.route('/', methods=['GET'])
def get_campaigns():
    """Get all campaigns"""
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return jsonify([c.to_dict() for c in campaigns])


@bp.route('/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get single campaign with details"""
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign_data = campaign.to_dict()
    campaign_data['targets'] = [t.to_dict() for t in campaign.targets]
    return jsonify(campaign_data)


@bp.route('/', methods=['POST'])
def create_campaign():
    """Create and launch new phishing campaign"""
    data = request.json

    # Get current user and their email service
    user = get_current_user()
    email_service = get_email_service_for_user(user)

    # Check if SMTP is configured
    if not email_service.is_configured():
        return jsonify({
            'error': 'SMTP not configured. Please configure your SMTP settings in Settings page before creating campaigns.',
            'smtp_config': email_service.get_config_summary()
        }), 400

    # Validate input
    required_fields = ['name', 'template_id', 'target_emails']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Parse target emails
    if isinstance(data['target_emails'], str):
        target_emails = [e.strip() for e in data['target_emails'].split(',') if e.strip()]
    else:
        target_emails = data['target_emails']

    if not target_emails:
        return jsonify({'error': 'No target emails provided'}), 400

    # Get base URL
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')

    # Get template from database
    template_id = data['template_id']
    template = CustomTemplate.query.get(template_id)

    if not template:
        return jsonify({'error': 'Template not found'}), 404

    if not template.is_active:
        return jsonify({'error': 'Template is not active'}), 400

    subject_template = template.subject
    html_template = template.html_content
    template_from_name = template.from_name  # Per-template sender name

    # Get landing page if specified
    landing_page_id = data.get('landing_page_id')
    landing_page = None
    if landing_page_id:
        landing_page = LandingPage.query.get(landing_page_id)
        if not landing_page:
            return jsonify({'error': 'Landing page not found'}), 404

    # Create campaign
    campaign = Campaign(
        name=data['name'],
        template_type=template_id,  # Store template ID
        subject=subject_template,
        target_emails=json.dumps(target_emails),
        status='active',
        landing_page_id=landing_page_id
    )
    db.session.add(campaign)
    db.session.flush()  # Get campaign ID

    # Track email sending results
    emails_sent = 0
    emails_failed = 0

    # Create targets and send emails
    for email in target_emails:
        # Generate unique tracking token
        tracking_token = str(uuid.uuid4())

        # Create target record
        target = CampaignTarget(
            campaign_id=campaign.id,
            email=email,
            tracking_token=tracking_token
        )
        db.session.add(target)

        # Parse recipient data from email
        recipient_data = parse_email_to_name(email)

        # If landing page is set, link to the credential harvest page
        if landing_page:
            recipient_data['tracking_link'] = f"{base_url}/api/landing/serve/{tracking_token}"
        else:
            recipient_data['tracking_link'] = f"{base_url}/api/track/click/{tracking_token}"
        recipient_data['base_url'] = base_url

        # Use template with variable substitution
        final_subject = substitute_template_variables(subject_template, recipient_data)
        final_html = substitute_template_variables(html_template, recipient_data)

        # Add tracking pixel
        tracking_pixel = f'<img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />'
        if '</body>' in final_html:
            final_html = final_html.replace('</body>', f'{tracking_pixel}</body>')
        else:
            final_html += tracking_pixel

        # Send email with template's from_name (if set)
        if email_service.send_email(email, final_subject, final_html, from_name_override=template_from_name):
            emails_sent += 1
        else:
            emails_failed += 1

    db.session.commit()

    # Return campaign with email sending stats
    result = campaign.to_dict()
    result['email_stats'] = {
        'sent': emails_sent,
        'failed': emails_failed,
        'total': len(target_emails)
    }

    return jsonify(result), 201


@bp.route('/<campaign_id>/status', methods=['PUT'])
def update_campaign_status(campaign_id):
    """Update campaign status (active, paused, completed)"""
    campaign = Campaign.query.get_or_404(campaign_id)
    data = request.json

    if 'status' in data:
        if data['status'] not in ['active', 'paused', 'completed']:
            return jsonify({'error': 'Invalid status'}), 400
        campaign.status = data['status']
        db.session.commit()

    return jsonify(campaign.to_dict())


@bp.route('/<campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Delete campaign and all related records"""
    try:
        from sqlalchemy import text

        campaign = Campaign.query.get_or_404(campaign_id)

        # Delete all related records using raw SQL to avoid ORM schema issues

        # 1. First, get all target IDs for this campaign
        target_ids = [t.id for t in campaign.targets]

        # 2. Delete scheduled campaigns that reference this campaign's targets (use raw SQL)
        if target_ids:
            # For SQLite, we need to build the query with proper parameter binding
            placeholders = ','.join([f':tid{i}' for i in range(len(target_ids))])
            params = {f'tid{i}': tid for i, tid in enumerate(target_ids)}
            db.session.execute(
                text(f"DELETE FROM scheduled_campaigns WHERE target_id IN ({placeholders})"),
                params
            )

        # 3. Delete scheduled campaigns that reference this campaign directly (use raw SQL)
        db.session.execute(
            text("DELETE FROM scheduled_campaigns WHERE campaign_id = :campaign_id"),
            {'campaign_id': campaign_id}
        )

        # 4. Delete credential captures related to this campaign
        db.session.execute(
            text("DELETE FROM credential_captures WHERE campaign_id = :campaign_id"),
            {'campaign_id': campaign_id}
        )

        # 5. Delete campaign targets (in case cascade doesn't work)
        db.session.execute(
            text("DELETE FROM campaign_targets WHERE campaign_id = :campaign_id"),
            {'campaign_id': campaign_id}
        )

        # 6. Delete the campaign itself
        db.session.execute(
            text("DELETE FROM campaigns WHERE id = :campaign_id"),
            {'campaign_id': campaign_id}
        )

        db.session.commit()

        return jsonify({'message': 'Campaign deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting campaign {campaign_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to delete campaign: {str(e)}'}), 500


@bp.route('/smtp-status', methods=['GET'])
def get_smtp_status():
    """Get current SMTP configuration status for the logged-in user"""
    user = get_current_user()

    # Debug: print session info
    print(f"[SMTP-STATUS] Session user_id: {session.get('user_id')}")
    print(f"[SMTP-STATUS] User found: {user}")

    if user:
        settings = Settings.query.filter_by(user_id=user.id).first()
        print(f"[SMTP-STATUS] Settings found: {settings}")
        if settings:
            print(f"[SMTP-STATUS] smtp_host: {settings.smtp_host}, smtp_username: {settings.smtp_username}")

    email_service = get_email_service_for_user(user)

    return jsonify({
        'configured': email_service.is_configured(),
        'config': email_service.get_config_summary()
    })
