"""
SMS Phishing (Smishing) Simulation Routes
Send and track SMS phishing simulations
"""

from flask import Blueprint, request, jsonify, redirect
from database import db
from models import SMSCampaign, SMSTarget, LandingPage, UserRiskScore, Settings, Employee
from datetime import datetime
import uuid
import json
import os

# Import Twilio SMS Service
try:
    from services.twilio_sms_service import TwilioSMSService, TWILIO_AVAILABLE
except ImportError:
    TWILIO_AVAILABLE = False
    print("Warning: Twilio SMS service not available")

bp = Blueprint('sms', __name__, url_prefix='/api/sms')


# ============================================
# SMISHING CAMPAIGN CRUD
# ============================================

@bp.route('/campaigns', methods=['GET'])
def get_sms_campaigns():
    """Get all SMS campaigns"""
    status = request.args.get('status')

    query = SMSCampaign.query

    if status:
        query = query.filter_by(status=status)

    campaigns = query.order_by(SMSCampaign.created_at.desc()).all()

    return jsonify([c.to_dict() for c in campaigns])


@bp.route('/campaigns/<campaign_id>', methods=['GET'])
def get_sms_campaign(campaign_id):
    """Get a specific SMS campaign with targets"""
    campaign = SMSCampaign.query.get_or_404(campaign_id)

    result = campaign.to_dict()
    result['targets'] = [t.to_dict() for t in campaign.targets]

    return jsonify(result)


@bp.route('/campaigns', methods=['POST'])
def create_sms_campaign():
    """Create a new SMS phishing campaign"""
    data = request.json

    if not data.get('name') or not data.get('message_template'):
        return jsonify({'error': 'Name and message template are required'}), 400

    # Generate tracking URL base
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')

    campaign = SMSCampaign(
        name=data['name'],
        description=data.get('description'),
        message_template=data['message_template'],
        sender_id=data.get('sender_id'),
        target_url=f"{base_url}/api/sms/click",  # Will append tracking token
        landing_page_id=data.get('landing_page_id'),
        status='draft'
    )

    db.session.add(campaign)
    db.session.commit()

    return jsonify(campaign.to_dict()), 201


@bp.route('/campaigns/<campaign_id>', methods=['PUT'])
def update_sms_campaign(campaign_id):
    """Update an SMS campaign"""
    campaign = SMSCampaign.query.get_or_404(campaign_id)
    data = request.json

    if data.get('name'):
        campaign.name = data['name']
    if data.get('description'):
        campaign.description = data['description']
    if data.get('message_template'):
        campaign.message_template = data['message_template']
    if data.get('sender_id'):
        campaign.sender_id = data['sender_id']
    if data.get('status'):
        campaign.status = data['status']
    if data.get('landing_page_id'):
        campaign.landing_page_id = data['landing_page_id']
    if data.get('scheduled_at'):
        campaign.scheduled_at = datetime.fromisoformat(data['scheduled_at'])

    db.session.commit()

    return jsonify(campaign.to_dict())


@bp.route('/campaigns/<campaign_id>', methods=['DELETE'])
def delete_sms_campaign(campaign_id):
    """Delete an SMS campaign"""
    campaign = SMSCampaign.query.get_or_404(campaign_id)

    db.session.delete(campaign)
    db.session.commit()

    return jsonify({'message': 'Campaign deleted'})


# ============================================
# TARGET MANAGEMENT
# ============================================

@bp.route('/campaigns/<campaign_id>/targets', methods=['POST'])
def add_targets(campaign_id):
    """Add targets to an SMS campaign"""
    campaign = SMSCampaign.query.get_or_404(campaign_id)
    data = request.json

    targets_data = data.get('targets', [])

    if not targets_data:
        return jsonify({'error': 'No targets provided'}), 400

    added = 0
    for target_info in targets_data:
        phone = target_info.get('phone_number') or target_info.get('phone')

        if not phone:
            continue

        # Generate unique tracking token
        tracking_token = str(uuid.uuid4())[:12]

        target = SMSTarget(
            campaign_id=campaign.id,
            phone_number=phone,
            email=target_info.get('email'),
            tracking_token=tracking_token
        )

        db.session.add(target)
        added += 1

    db.session.commit()

    return jsonify({
        'message': f'Added {added} targets',
        'total_targets': len(campaign.targets)
    })


@bp.route('/campaigns/<campaign_id>/targets', methods=['GET'])
def get_targets(campaign_id):
    """Get all targets for a campaign"""
    campaign = SMSCampaign.query.get_or_404(campaign_id)

    return jsonify([t.to_dict() for t in campaign.targets])


# ============================================
# SEND SMS CAMPAIGN
# ============================================

@bp.route('/campaigns/<campaign_id>/send', methods=['POST'])
def send_sms_campaign(campaign_id):
    """Send SMS to all targets in campaign"""
    campaign = SMSCampaign.query.get_or_404(campaign_id)

    if not campaign.targets:
        return jsonify({'error': 'No targets in campaign'}), 400

    # Get Twilio credentials from environment or user settings
    data = request.json or {}
    user_id = data.get('user_id')

    # Try user settings first, then environment
    twilio_sid = None
    twilio_token = None
    twilio_phone = None

    if user_id:
        settings = Settings.query.filter_by(user_id=user_id).first()
        if settings:
            twilio_sid = settings.twilio_account_sid
            twilio_token = settings.twilio_auth_token
            twilio_phone = settings.twilio_phone_number

    # Fall back to environment variables
    if not all([twilio_sid, twilio_token, twilio_phone]):
        twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
        twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')

    use_mock = not (TWILIO_AVAILABLE and twilio_sid and twilio_token and twilio_phone)

    if use_mock:
        # Mock mode - just simulate sending
        results = send_mock_sms(campaign)
    else:
        # Real Twilio sending using new service
        results = send_twilio_sms_new(campaign, twilio_sid, twilio_token, twilio_phone)

    campaign.status = 'active'
    campaign.total_sent = results['sent']
    campaign.total_delivered = results['delivered']
    db.session.commit()

    return jsonify({
        'message': 'Campaign sent',
        'mock_mode': use_mock,
        'results': results
    })


def send_mock_sms(campaign):
    """Mock SMS sending for testing"""
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    sent = 0
    delivered = 0

    for target in campaign.targets:
        # Generate personalized message
        message = campaign.message_template
        tracking_url = f"{base_url}/api/sms/click/{target.tracking_token}"

        # Replace variables
        message = message.replace('{{link}}', tracking_url)
        message = message.replace('{{url}}', tracking_url)

        # Mark as sent
        target.sent_at = datetime.utcnow()
        target.delivered_at = datetime.utcnow()  # Mock always delivers

        sent += 1
        delivered += 1

        print(f"[MOCK SMS] To: {target.phone_number}")
        print(f"[MOCK SMS] Message: {message}")
        print(f"[MOCK SMS] Tracking URL: {tracking_url}")
        print("-" * 40)

    db.session.commit()

    return {
        'sent': sent,
        'delivered': delivered,
        'failed': 0
    }


def send_twilio_sms_new(campaign, sid, token, from_phone):
    """Send SMS via Twilio using the new service"""
    try:
        print(f"[TWILIO] Initializing Twilio service...")
        print(f"[TWILIO] Account SID: {sid[:10]}...")
        print(f"[TWILIO] From Phone: {from_phone}")

        # Initialize Twilio service
        sms_service = TwilioSMSService(sid, token, from_phone)
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')

        sent = 0
        delivered = 0
        failed = 0

        # Prepare recipients list
        recipients = []
        for target in campaign.targets:
            recipients.append({
                'phone': target.phone_number,
                'tracking_token': target.tracking_token,
                'target_id': target.id
            })

        print(f"[TWILIO] Sending to {len(recipients)} recipients...")
        for recipient in recipients:
            print(f"[TWILIO] Target: {recipient['phone']}")

        # Build tracking URL base
        tracking_url_base = f"{base_url}/api/sms/click"

        # Get sender ID from campaign (if set and not empty)
        sender_id = campaign.sender_id if (campaign.sender_id and campaign.sender_id.strip()) else None
        if sender_id:
            print(f"[TWILIO] Using custom sender ID: {sender_id}")
        else:
            print(f"[TWILIO] Using default Twilio phone number: {from_phone}")

        # Send bulk SMS
        bulk_result = sms_service.send_bulk_sms(
            recipients=recipients,
            message_template=campaign.message_template,
            base_tracking_url=tracking_url_base,
            sender_id=sender_id
        )

        print(f"[TWILIO] Bulk send result: {bulk_result}")

        # Update target records with results
        for result in bulk_result['results']:
            # Find the target
            target = next((t for t in campaign.targets if t.phone_number == result['phone']), None)
            if target:
                target.sent_at = datetime.utcnow()
                target.twilio_message_sid = result.get('message_sid')

                if result['success']:
                    target.delivered_at = datetime.utcnow()
                    delivered += 1
                    sent += 1
                    print(f"[TWILIO] ✓ Sent to {result['phone']}")
                else:
                    failed += 1
                    target.delivery_error = result.get('error')
                    print(f"[TWILIO] ✗ Failed to {result['phone']}: {result.get('error')}")

        db.session.commit()

        return {
            'sent': sent,
            'delivered': delivered,
            'failed': failed,
            'details': bulk_result
        }

    except Exception as e:
        print(f"[TWILIO] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            'sent': 0,
            'delivered': 0,
            'failed': len(campaign.targets),
            'error': str(e)
        }


# ============================================
# CLICK TRACKING
# ============================================

@bp.route('/click/<tracking_token>')
def track_sms_click(tracking_token):
    """Track when someone clicks the SMS link"""
    target = SMSTarget.query.filter_by(tracking_token=tracking_token).first()

    if not target:
        return "Link expired or invalid", 404

    # Record the click
    if not target.clicked_at:
        target.clicked_at = datetime.utcnow()
        target.ip_address = request.remote_addr
        target.user_agent = request.headers.get('User-Agent', '')

        # Update campaign stats
        campaign = target.campaign
        campaign.total_clicked += 1

        # Update user risk if email is known
        if target.email:
            user_risk = UserRiskScore.query.filter_by(email=target.email).first()
            if user_risk:
                user_risk.record_click()
            else:
                user_risk = UserRiskScore(
                    email=target.email,
                    campaigns_received=1,
                    campaigns_clicked=1
                )
                user_risk.calculate_risk_score()
                db.session.add(user_risk)

            # Update HVS score for SMS click
            employee = Employee.query.filter_by(email=target.email).first()
            if employee:
                employee.update_hvs('clicked_sms')

        db.session.commit()

    # Redirect to landing page or training
    campaign = target.campaign
    if campaign.landing_page_id:
        landing_page = LandingPage.query.get(campaign.landing_page_id)
        if landing_page:
            new_token = str(uuid.uuid4())
            html = landing_page.html_content.replace('{{tracking_token}}', new_token)
            from flask import render_template_string
            return render_template_string(html, tracking_token=new_token)

    # Default: show SMS training page
    return redirect('/api/sms/training')


@bp.route('/training')
def sms_training_page():
    """Show SMS phishing awareness training"""
    from flask import render_template_string
    return render_template_string(SMS_TRAINING_PAGE)


# ============================================
# STATISTICS
# ============================================

@bp.route('/stats')
def get_sms_stats():
    """Get overall SMS campaign statistics"""
    total_campaigns = SMSCampaign.query.count()
    active_campaigns = SMSCampaign.query.filter_by(status='active').count()
    total_sent = db.session.query(db.func.sum(SMSCampaign.total_sent)).scalar() or 0
    total_delivered = db.session.query(db.func.sum(SMSCampaign.total_delivered)).scalar() or 0
    total_clicked = db.session.query(db.func.sum(SMSCampaign.total_clicked)).scalar() or 0

    click_rate = round((total_clicked / total_sent * 100), 2) if total_sent > 0 else 0

    return jsonify({
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'total_sent': total_sent,
        'total_delivered': total_delivered,
        'total_clicked': total_clicked,
        'overall_click_rate': click_rate
    })


@bp.route('/campaigns/<campaign_id>/stats')
def get_campaign_stats(campaign_id):
    """Get detailed stats for a specific campaign"""
    campaign = SMSCampaign.query.get_or_404(campaign_id)

    clicked_targets = SMSTarget.query.filter_by(
        campaign_id=campaign_id
    ).filter(SMSTarget.clicked_at.isnot(None)).count()

    return jsonify({
        'campaign': campaign.to_dict(),
        'total_targets': len(campaign.targets),
        'total_sent': campaign.total_sent,
        'total_delivered': campaign.total_delivered,
        'total_clicked': clicked_targets,
        'click_rate': round((clicked_targets / campaign.total_sent * 100), 2) if campaign.total_sent > 0 else 0
    })


# ============================================
# SMS TEMPLATES
# ============================================

@bp.route('/test', methods=['POST'])
def test_sms_send():
    """Test SMS sending with Twilio (send a test message)"""
    data = request.json

    if not data.get('phone_number') or not data.get('message'):
        return jsonify({'error': 'phone_number and message are required'}), 400

    # Get Twilio credentials
    user_id = data.get('user_id')
    twilio_sid = None
    twilio_token = None
    twilio_phone = None

    if user_id:
        settings = Settings.query.filter_by(user_id=user_id).first()
        if settings:
            twilio_sid = settings.twilio_account_sid
            twilio_token = settings.twilio_auth_token
            twilio_phone = settings.twilio_phone_number

    # Fall back to environment
    if not all([twilio_sid, twilio_token, twilio_phone]):
        twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
        twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')

    if not all([twilio_sid, twilio_token, twilio_phone]):
        return jsonify({
            'error': 'Twilio credentials not configured. Set them in Settings or environment variables.'
        }), 400

    try:
        # Initialize service and send
        sms_service = TwilioSMSService(twilio_sid, twilio_token, twilio_phone)
        result = sms_service.send_sms(
            to_number=data['phone_number'],
            message=data['message'],
            sender_id=data.get('sender_id')  # Optional custom sender ID
        )

        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Test SMS sent successfully',
                'details': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error'),
                'details': result
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/validate-phone', methods=['POST'])
def validate_phone():
    """Validate a phone number using Twilio Lookup API"""
    data = request.json

    if not data.get('phone_number'):
        return jsonify({'error': 'phone_number is required'}), 400

    # Get Twilio credentials
    user_id = data.get('user_id')
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')

    if user_id:
        settings = Settings.query.filter_by(user_id=user_id).first()
        if settings and settings.twilio_account_sid:
            twilio_sid = settings.twilio_account_sid
            twilio_token = settings.twilio_auth_token
            twilio_phone = settings.twilio_phone_number

    if not all([twilio_sid, twilio_token, twilio_phone]):
        return jsonify({'error': 'Twilio credentials not configured'}), 400

    try:
        sms_service = TwilioSMSService(twilio_sid, twilio_token, twilio_phone)
        result = sms_service.validate_phone_number(data['phone_number'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/templates', methods=['GET'])
def get_sms_templates():
    """Get pre-built SMS templates"""
    templates = [
        {
            'id': 'delivery',
            'name': 'Package Delivery',
            'category': 'delivery',
            'message': 'Your package could not be delivered. Reschedule here: {{link}}',
            'difficulty': 'easy'
        },
        {
            'id': 'bank_alert',
            'name': 'Bank Security Alert',
            'category': 'banking',
            'message': 'ALERT: Unusual activity on your account. Verify now: {{link}}',
            'difficulty': 'medium'
        },
        {
            'id': 'prize',
            'name': 'Prize Winner',
            'category': 'reward',
            'message': 'Congrats! You won a $500 gift card. Claim here: {{link}}',
            'difficulty': 'easy'
        },
        {
            'id': 'it_support',
            'name': 'IT Password Reset',
            'category': 'corporate',
            'message': 'IT Dept: Your password expires today. Reset: {{link}}',
            'difficulty': 'medium'
        },
        {
            'id': 'hr_survey',
            'name': 'HR Survey',
            'category': 'corporate',
            'message': 'HR: Complete the mandatory employee survey by EOD: {{link}}',
            'difficulty': 'hard'
        },
        {
            'id': 'mfa_code',
            'name': 'MFA Code Request',
            'category': 'security',
            'message': 'Your verification code is 847291. If you did not request this, secure your account: {{link}}',
            'difficulty': 'hard'
        }
    ]

    return jsonify(templates)


# ============================================
# TRAINING PAGE
# ============================================

SMS_TRAINING_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SMS Phishing Awareness</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: white;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #9b59b6, #8e44ad);
            padding: 60px 20px;
            text-align: center;
        }
        .header h1 {
            font-size: 1.8em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
        }
        .content {
            max-width: 600px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .card h2 {
            color: #9b59b6;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .card p, .card li {
            color: #ccc;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .card ul {
            margin-left: 20px;
        }
        .phone-example {
            background: #0f0f23;
            border-radius: 20px;
            padding: 20px;
            margin: 20px 0;
            border: 2px solid #333;
        }
        .sms-bubble {
            background: #1a73e8;
            color: white;
            padding: 12px 16px;
            border-radius: 18px 18px 4px 18px;
            max-width: 80%;
            margin-bottom: 10px;
            font-size: 14px;
        }
        .red-flag {
            color: #e74c3c;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>You Clicked a Smishing Link</h1>
        <p>This was an SMS phishing simulation</p>
    </div>
    <div class="content">
        <div class="card">
            <h2>What is Smishing?</h2>
            <p><strong>Smishing</strong> (SMS + Phishing) is when attackers send fraudulent text messages to trick you into:</p>
            <ul>
                <li>Clicking malicious links</li>
                <li>Downloading malware</li>
                <li>Revealing personal information</li>
                <li>Making payments to scammers</li>
            </ul>
        </div>

        <div class="card">
            <h2>Example Smishing Message</h2>
            <div class="phone-example">
                <div class="sms-bubble">
                    ALERT: Unusual activity on your account. Verify immediately: bit.ly/x8k2m
                </div>
            </div>
            <p><span class="red-flag">Red Flags:</span></p>
            <ul>
                <li>Urgent language ("ALERT", "immediately")</li>
                <li>Shortened/suspicious URL</li>
                <li>No personalization (doesn't use your name)</li>
                <li>Requests to click a link</li>
            </ul>
        </div>

        <div class="card">
            <h2>How to Protect Yourself</h2>
            <ul>
                <li><strong>Don't click links</strong> in unexpected text messages</li>
                <li><strong>Verify the sender</strong> by calling the organization directly</li>
                <li><strong>Check URLs</strong> - hover or long-press to preview</li>
                <li><strong>Report suspicious texts</strong> to your IT team</li>
                <li><strong>Delete the message</strong> without responding</li>
            </ul>
        </div>
    </div>
</body>
</html>
'''
