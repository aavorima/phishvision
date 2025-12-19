"""
QR Code Phishing (Quishing) Routes
Generate and track malicious QR code simulations
"""

from flask import Blueprint, request, jsonify, send_file, redirect, render_template_string
from database import db
from models import QRCodeCampaign, QRCodeScan, LandingPage, UserRiskScore
from datetime import datetime
import uuid
import io
import os
import json

# Try to import qrcode library
try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("Warning: qrcode library not installed. Run: pip install qrcode[pil]")

bp = Blueprint('qrcode', __name__, url_prefix='/api/qr')

# Directory to store generated QR codes
QR_CODE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'qrcodes')
os.makedirs(QR_CODE_DIR, exist_ok=True)


# ============================================
# QR CODE CAMPAIGN CRUD
# ============================================

@bp.route('/campaigns', methods=['GET'])
def get_qr_campaigns():
    """Get all QR code campaigns"""
    status = request.args.get('status')

    query = QRCodeCampaign.query

    if status:
        query = query.filter_by(status=status)

    campaigns = query.order_by(QRCodeCampaign.created_at.desc()).all()

    return jsonify([c.to_dict() for c in campaigns])


@bp.route('/campaigns/<campaign_id>', methods=['GET'])
def get_qr_campaign(campaign_id):
    """Get a specific QR campaign with scans and targets"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)

    result = campaign.to_dict()
    result['scans'] = [s.to_dict() for s in campaign.scans]
    result['targets'] = [t.to_dict() for t in campaign.targets]

    return jsonify(result)


@bp.route('/campaigns', methods=['POST'])
def create_qr_campaign():
    """Create a new QR code phishing campaign"""
    try:
        if not QR_AVAILABLE:
            return jsonify({'error': 'QR code library not installed. Run: pip install qrcode[pil]'}), 500

        data = request.json

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        if not data.get('name'):
            return jsonify({'error': 'Campaign name is required'}), 400

        # Generate unique tracking ID
        tracking_id = str(uuid.uuid4())[:8]

        # Build the tracking URL
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        target_url = f"{base_url}/api/qr/scan/{tracking_id}"

        # Create campaign
        campaign = QRCodeCampaign(
            name=data['name'],
            description=data.get('description'),
            target_url=target_url,
            landing_page_id=data.get('landing_page_id'),
            program_id=data.get('program_id'),  # Link to profiling program if provided
            placement_location=data.get('placement_location'),
            status='active'
        )

        db.session.add(campaign)
        db.session.flush()  # Get the ID

        # Generate QR code image
        qr_filename = f"qr_{campaign.id}.png"
        qr_path = os.path.join(QR_CODE_DIR, qr_filename)

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(target_url)
            qr.make(fit=True)

            # Create styled QR code
            img = qr.make_image(
                fill_color=data.get('color', '#000000'),
                back_color='white'
            )
            img.save(qr_path)

            campaign.qr_image_path = qr_filename

        except Exception as e:
            print(f"Error generating QR: {e}")
            # Continue without image

        db.session.commit()

        return jsonify(campaign.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating QR campaign: {e}")
        return jsonify({'error': f'Failed to create QR campaign: {str(e)}'}), 500


@bp.route('/campaigns/<campaign_id>', methods=['PUT'])
def update_qr_campaign(campaign_id):
    """Update a QR campaign"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)
    data = request.json

    if data.get('name'):
        campaign.name = data['name']
    if data.get('description'):
        campaign.description = data['description']
    if data.get('status'):
        campaign.status = data['status']
    if data.get('placement_location'):
        campaign.placement_location = data['placement_location']
    if data.get('landing_page_id'):
        campaign.landing_page_id = data['landing_page_id']

    db.session.commit()

    return jsonify(campaign.to_dict())


@bp.route('/campaigns/<campaign_id>', methods=['DELETE'])
def delete_qr_campaign(campaign_id):
    """Delete a QR campaign"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)

    # Delete QR image file
    if campaign.qr_image_path:
        qr_path = os.path.join(QR_CODE_DIR, campaign.qr_image_path)
        if os.path.exists(qr_path):
            os.remove(qr_path)

    db.session.delete(campaign)
    db.session.commit()

    return jsonify({'message': 'Campaign deleted'})


# ============================================
# QR CODE IMAGE ENDPOINTS
# ============================================

@bp.route('/campaigns/<campaign_id>/image')
def get_qr_image(campaign_id):
    """Get the QR code image for a campaign"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)

    # Construct the expected filename from campaign ID (more reliable than stored path)
    qr_filename = f"qr_{campaign.id}.png"
    qr_path = os.path.join(QR_CODE_DIR, qr_filename)

    if not os.path.exists(qr_path):
        return jsonify({'error': 'QR image file not found'}), 404

    return send_file(qr_path, mimetype='image/png')


@bp.route('/campaigns/<campaign_id>/download')
def download_qr_image(campaign_id):
    """Download QR code as image file"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)

    # Construct the expected filename from campaign ID (more reliable than stored path)
    qr_filename = f"qr_{campaign.id}.png"
    qr_path = os.path.join(QR_CODE_DIR, qr_filename)

    if not os.path.exists(qr_path):
        return jsonify({'error': 'QR image file not found'}), 404

    return send_file(
        qr_path,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'phishing_qr_{campaign.name.replace(" ", "_")}.png'
    )


@bp.route('/campaigns/<campaign_id>/poster')
def get_printable_poster(campaign_id):
    """Generate a printable poster with QR code for physical placement"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)

    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    qr_image_url = f"{base_url}/api/qr/campaigns/{campaign_id}/image"

    poster_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Code Poster - {campaign.name}</title>
        <style>
            @page {{ size: A4; margin: 0; }}
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding: 40px;
                box-sizing: border-box;
            }}
            .poster {{
                text-align: center;
                border: 3px solid #333;
                padding: 40px;
                max-width: 600px;
            }}
            h1 {{
                color: #333;
                margin-bottom: 20px;
            }}
            .qr-container {{
                margin: 30px 0;
            }}
            .qr-container img {{
                width: 300px;
                height: 300px;
            }}
            .instructions {{
                color: #666;
                font-size: 18px;
                margin-top: 20px;
            }}
            .warning {{
                color: #e74c3c;
                font-size: 12px;
                margin-top: 30px;
                padding: 10px;
                border: 1px dashed #e74c3c;
            }}
            @media print {{
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="poster">
            <h1>Scan for Special Offer!</h1>
            <div class="qr-container">
                <img src="{qr_image_url}" alt="QR Code">
            </div>
            <p class="instructions">
                Scan this QR code with your phone camera<br>
                to access exclusive content!
            </p>
            <p class="warning no-print">
                [TRAINING MATERIAL] - This is a phishing simulation QR code<br>
                Location: {campaign.placement_location or 'Not specified'}
            </p>
        </div>
        <button class="no-print" onclick="window.print()" style="margin-top:20px;padding:10px 20px;cursor:pointer;">
            Print Poster
        </button>
    </body>
    </html>
    '''

    return render_template_string(poster_html)


@bp.route('/campaigns/<campaign_id>/send-poster', methods=['POST'])
def send_poster_email(campaign_id):
    """Send QR code poster via email to specified recipients"""
    try:
        from services.email_service import EmailService
        from models import Settings
        from flask import g

        campaign = QRCodeCampaign.query.get_or_404(campaign_id)
        data = request.json

        if not data or not data.get('recipients'):
            return jsonify({'error': 'Recipients list is required'}), 400

        recipients = data.get('recipients', [])
        subject = data.get('subject', f'QR Code Poster - {campaign.name}')

        # Get user settings for SMTP
        user_id = g.get('user_id')
        settings = None
        if user_id:
            settings = Settings.query.filter_by(user_id=user_id).first()

        email_service = EmailService.from_user_settings(settings, allow_env_fallback=True)

        if not email_service.is_configured():
            return jsonify({'error': 'SMTP not configured. Please configure your email settings.'}), 400

        # Generate poster HTML for email
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        qr_image_url = f"{base_url}/api/qr/campaigns/{campaign_id}/image"

        # Create email HTML with embedded poster
        def create_email_html(recipient_email):
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>QR Code Poster</title>
            </head>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">QR Code Poster</h1>
                    </div>

                    <div style="padding: 40px; text-align: center;">
                        <h2 style="color: #333; margin-bottom: 20px;">{campaign.name}</h2>

                        {f'<p style="color: #666; font-size: 16px; margin-bottom: 30px;">{campaign.description}</p>' if campaign.description else ''}

                        <div style="background-color: #f8f9fa; border: 3px solid #333; border-radius: 10px; padding: 40px; margin: 20px 0;">
                            <h3 style="color: #333; margin-bottom: 20px; font-size: 24px;">Scan for Special Offer!</h3>

                            <div style="margin: 30px 0;">
                                <img src="{qr_image_url}" alt="QR Code" style="width: 300px; height: 300px; border-radius: 10px;">
                            </div>

                            <p style="color: #666; font-size: 18px; margin-top: 20px;">
                                📱 Scan this QR code with your phone camera<br>
                                to access exclusive content!
                            </p>

                            {f'<p style="color: #999; font-size: 14px; margin-top: 20px;">Location: {campaign.placement_location}</p>' if campaign.placement_location else ''}
                        </div>

                        <div style="margin-top: 30px; padding: 20px; background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 5px;">
                            <p style="color: #856404; font-size: 14px; margin: 0;">
                                <strong>⚠️ Note:</strong> You can also print this poster and place it in your office.
                            </p>
                        </div>

                        <div style="margin-top: 20px;">
                            <a href="{base_url}/api/qr/campaigns/{campaign_id}/poster"
                               style="display: inline-block; padding: 12px 30px; background-color: #667eea; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                                View Printable Version
                            </a>
                        </div>
                    </div>

                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                        <p style="color: #999; font-size: 12px; margin: 0;">
                            This is a security awareness testing campaign from PhishVision
                        </p>
                    </div>
                </div>
            </body>
            </html>
            '''

        # Send emails to all recipients
        results = []
        for recipient in recipients:
            # Handle both string emails and dict objects with email field
            email = recipient if isinstance(recipient, str) else recipient.get('email')
            name = recipient.get('name', '') if isinstance(recipient, dict) else ''

            if not email:
                continue

            html_content = create_email_html(email)
            success = email_service.send_email(email, subject, html_content)

            results.append({
                'email': email,
                'name': name,
                'success': success
            })

        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        return jsonify({
            'message': f'Sent {successful} emails, {failed} failed',
            'successful': successful,
            'failed': failed,
            'results': results
        }), 200

    except Exception as e:
        print(f"Error sending poster emails: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================
# QR CODE SCANNING & TRACKING
# ============================================

@bp.route('/scan/<tracking_id>')
def track_qr_scan(tracking_id):
    """Track when someone scans the QR code"""
    from models import QRCodeTarget
    from datetime import datetime

    # Try to find target by tracking token (for profiling program QR campaigns)
    target = QRCodeTarget.query.filter_by(tracking_token=tracking_id).first()

    if target:
        # This is a profiling program QR scan - update the target
        campaign = QRCodeCampaign.query.get(target.campaign_id)

        if not campaign:
            return "QR code expired or invalid", 404

        if campaign.status != 'active':
            return "This QR code is no longer active", 410

        # Update target's scanned_at timestamp if not already scanned
        if not target.scanned_at:
            target.scanned_at = datetime.utcnow()
            target.ip_address = request.remote_addr
            target.user_agent = request.headers.get('User-Agent', '')

            # Update campaign stats
            campaign.total_scans += 1
            campaign.unique_scans += 1

            db.session.commit()

        # Serve the training page with employee context
        import os as os_module
        base_url = os_module.environ.get('BASE_URL', 'http://localhost:5000')
        scanned_url = f"{base_url}/api/qr/scan/{tracking_id}"

        return render_template_string(
            QR_TRAINING_PAGE,
            employee_name=target.name or 'Unknown',
            employee_id=target.id,
            employee_email=target.email,
            placement_location=campaign.placement_location or 'Unknown',
            program_id=campaign.program_id or '',
            campaign_id=campaign.id,
            scanned_url=scanned_url
        )

    # Fallback: Try old method (find campaign by tracking ID in URL)
    campaign = QRCodeCampaign.query.filter(
        QRCodeCampaign.target_url.contains(tracking_id)
    ).first()

    if not campaign:
        return "QR code expired or invalid", 404

    if campaign.status != 'active':
        return "This QR code is no longer active", 410

    # Detect device type from user agent
    user_agent = request.headers.get('User-Agent', '').lower()
    device_type = 'desktop'
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        device_type = 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        device_type = 'tablet'

    # Check if this is a unique scan (by IP)
    existing_scan = QRCodeScan.query.filter_by(
        campaign_id=campaign.id,
        ip_address=request.remote_addr
    ).first()

    is_unique = existing_scan is None

    # Record the scan
    scan = QRCodeScan(
        campaign_id=campaign.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        device_type=device_type
    )
    db.session.add(scan)

    # Update campaign stats
    campaign.total_scans += 1
    if is_unique:
        campaign.unique_scans += 1

    db.session.commit()

    # Always show the QR training page instead of landing page
    import os as os_module
    base_url = os_module.environ.get('BASE_URL', 'http://localhost:5000')
    scanned_url = f"{base_url}/api/qr/scan/{tracking_id}"

    return render_template_string(
        QR_TRAINING_PAGE,
        employee_name='Unknown',
        employee_id='',
        employee_email='',
        placement_location=campaign.placement_location or 'Unknown',
        program_id='',
        campaign_id=campaign.id,
        scanned_url=scanned_url
    )


@bp.route('/training')
def qr_training_page():
    """Show awareness training after QR scan"""
    return render_template_string(QR_TRAINING_PAGE)


# ============================================
# STATISTICS
# ============================================

@bp.route('/stats')
def get_qr_stats():
    """Get overall QR campaign statistics"""
    total_campaigns = QRCodeCampaign.query.count()
    active_campaigns = QRCodeCampaign.query.filter_by(status='active').count()
    total_scans = QRCodeScan.query.count()

    # Scans by device type
    from sqlalchemy import func
    by_device = db.session.query(
        QRCodeScan.device_type,
        func.count(QRCodeScan.id)
    ).group_by(QRCodeScan.device_type).all()

    # Top campaigns by scans
    top_campaigns = db.session.query(
        QRCodeCampaign.name,
        QRCodeCampaign.total_scans
    ).order_by(QRCodeCampaign.total_scans.desc()).limit(5).all()

    return jsonify({
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'total_scans': total_scans,
        'scans_by_device': {d[0]: d[1] for d in by_device if d[0]},
        'top_campaigns': [{'name': c[0], 'scans': c[1]} for c in top_campaigns]
    })


@bp.route('/campaigns/<campaign_id>/stats')
def get_campaign_stats(campaign_id):
    """Get detailed stats for a specific campaign"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)

    # Scans over time (by day)
    from sqlalchemy import func
    daily_scans = db.session.query(
        func.date(QRCodeScan.scanned_at),
        func.count(QRCodeScan.id)
    ).filter_by(campaign_id=campaign_id).group_by(
        func.date(QRCodeScan.scanned_at)
    ).all()

    # Device breakdown
    by_device = db.session.query(
        QRCodeScan.device_type,
        func.count(QRCodeScan.id)
    ).filter_by(campaign_id=campaign_id).group_by(QRCodeScan.device_type).all()

    # Calculate unique devices based on targets with different user agents
    unique_user_agents = set()
    for target in campaign.targets:
        if target.scanned_at and target.user_agent:
            unique_user_agents.add(target.user_agent)

    unique_devices = len(unique_user_agents)

    return jsonify({
        'campaign': campaign.to_dict(),
        'total_scans': campaign.total_scans,
        'unique_scans': campaign.unique_scans,
        'unique_devices': unique_devices,  # Add this field for frontend
        'daily_scans': [{'date': str(d[0]), 'count': d[1]} for d in daily_scans],
        'device_breakdown': {d[0]: d[1] for d in by_device if d[0]}
    })


# ============================================
# GENERATE QR ON-THE-FLY
# ============================================

@bp.route('/generate', methods=['POST'])
def generate_qr_quick():
    """Generate a QR code without creating a campaign (for testing)"""
    if not QR_AVAILABLE:
        return jsonify({'error': 'QR code library not installed'}), 500

    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(
            fill_color=data.get('color', '#000000'),
            back_color='white'
        )

        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        return send_file(
            img_bytes,
            mimetype='image/png',
            as_attachment=False
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# TRAINING PAGE
# ============================================

QR_TRAINING_PAGE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>QR Phishing Training</title>
  <style>
    :root{
      --bg:#070a12;
      --paper:#0b1020;
      --card:#0f172a;
      --text:#e5e7eb;
      --muted:#9aa7bf;
      --border:rgba(255,255,255,.10);
      --purple:#8b5cf6;
      --cyan:#22d3ee;
      --danger:#fb7185;
      --ok:#34d399;
      --shadow:0 18px 60px rgba(0,0,0,.55);
      --r:22px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      color:var(--text);
      background:
        linear-gradient(180deg, rgba(139,92,246,.18), transparent 40%),
        radial-gradient(900px 400px at 80% 10%, rgba(34,211,238,.14), transparent),
        var(--bg);
    }
    .wrap{max-width:860px;margin:0 auto;padding:18px}
    .hero{
      border:1px solid var(--border);
      border-radius:var(--r);
      background: linear-gradient(135deg, rgba(139,92,246,.18), rgba(34,211,238,.12));
      box-shadow:var(--shadow);
      padding:22px 18px;
      position:relative;
      overflow:hidden;
    }
    .hero h1{margin:0;font-size:28px;font-weight:1000;letter-spacing:.2px}
    .hero p{margin:10px 0 0;color:rgba(255,255,255,.85);max-width:60ch}
    .chipRow{margin-top:12px;display:flex;gap:10px;flex-wrap:wrap}
    .chip{
      border:1px solid var(--border);
      background:rgba(0,0,0,.20);
      padding:8px 12px;border-radius:999px;
      font-size:12px;font-weight:800;color:rgba(255,255,255,.92);
    }

    .poster{
      margin-top:14px;
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap:14px;
    }
    @media (max-width: 820px){ .poster{grid-template-columns:1fr} }

    .panel{
      border:1px solid var(--border);
      background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
      border-radius:var(--r);
      box-shadow:var(--shadow);
      padding:18px;
    }
    h2{
      margin:0 0 10px;
      font-size:18px;
      font-weight:1000;
      color:rgba(34,211,238,.95);
    }
    p{margin:10px 0;color:var(--muted);line-height:1.55}
    ul{margin:10px 0 0 18px;color:var(--muted)}
    li{margin:8px 0}

    .qrMock{
      background:rgba(0,0,0,.25);
      border:1px dashed rgba(255,255,255,.18);
      border-radius:18px;
      padding:16px;
    }
    .qrBox{
      width:170px;height:170px;
      border-radius:14px;
      background:
        linear-gradient(90deg, rgba(255,255,255,.10), rgba(255,255,255,.06)),
        repeating-linear-gradient(0deg, rgba(255,255,255,.08), rgba(255,255,255,.08) 6px, transparent 6px, transparent 12px),
        repeating-linear-gradient(90deg, rgba(255,255,255,.08), rgba(255,255,255,.08) 6px, transparent 6px, transparent 12px);
      border:1px solid rgba(255,255,255,.14);
      box-shadow:0 18px 40px rgba(0,0,0,.35);
    }
    .qrCaption{
      margin-top:12px;
      font-size:12px;color:rgba(255,255,255,.75);font-weight:800;
      word-break:break-all;
    }
    .dangerTitle{color:var(--danger);font-weight:1000;margin-top:12px}
    .okTitle{color:var(--ok);font-weight:1000;margin-top:12px}

    .checkRow{display:flex;gap:10px;align-items:flex-start;margin-top:12px;color:var(--muted)}
    input[type="checkbox"]{width:18px;height:18px;margin-top:2px;accent-color:var(--cyan)}
    .actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
    button{
      border:none;cursor:pointer;border-radius:16px;
      padding:12px 14px;font-weight:1000;font-size:14px;
    }
    .primary{
      background:linear-gradient(90deg, rgba(34,211,238,1), rgba(139,92,246,1));
      color:#071018;opacity:.6;
      box-shadow:0 14px 40px rgba(34,211,238,.15);
    }
    .primary.enabled{opacity:1}
    .ghost{
      background:rgba(255,255,255,.06);
      border:1px solid var(--border);
      color:rgba(255,255,255,.9);
    }
    .success{
      display:none;margin-top:12px;
      background:rgba(52,211,153,.12);
      border:1px solid rgba(52,211,153,.25);
      color:rgba(220,255,235,.95);
      padding:12px 14px;border-radius:16px;font-weight:900;
    }
    .note{margin-top:12px;font-size:12px;color:rgba(255,255,255,.6)}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>QR Code Phishing Detected</h1>
      <p>
        You scanned a QR code as part of a <b>quishing (QR phishing) simulation</b>.
        QR codes can hide malicious links because you can't "hover" to preview them.
      </p>
      <div class="chipRow">
        <span class="chip">SIMULATION</span>
        <span class="chip">Employee: {{employee_name}}</span>
        <span class="chip">Location tag: {{placement_location}}</span>
      </div>
    </div>

    <div class="poster">
      <!-- Left: QR poster vibe -->
      <div class="panel">
        <h2>What happened</h2>
        <p>Here's the QR scan outcome recorded by the program:</p>

        <div class="qrMock">
          <div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap">

            <div style="min-width:220px;flex:1">



              <div class="dangerTitle">Why this matters</div>
              <p>
                QR codes can send you to credential-harvest pages, install malware, or redirect to fake logins.
                They work especially well in public places (posters, elevators, breakrooms).
              </p>
            </div>
          </div>
        </div>

        <div class="dangerTitle">Common quishing tactics</div>
        <ul>
          <li>"Free gift / discount" QR posters</li>
          <li>Fake "Wi-Fi login" or "security update" notices</li>
          <li>QR codes placed over real posters (sticker overlay)</li>
        </ul>
      </div>

      <!-- Right: Training (different tone from email & SMS) -->
      <div class="panel">
        <h2>What went wrong in your case</h2>
        <ul>
          <li>The QR destination couldn't be verified before scanning.</li>
          <li>The context relied on urgency/reward ("scan now", "limited time").</li>
          <li>The scan skipped the "pause & verify" step.</li>
        </ul>

        <div class="dangerTitle">Red flags</div>
        <ul>
          <li>QR code in an unexpected place or looks like a sticker over another QR</li>
          <li>Poster pressures urgency: "act now", "today only"</li>
          <li>Scan leads to a short/strange domain or login page</li>
        </ul>

        <div class="okTitle">Safer behavior</div>
        <ul>
          <li>Use a scanner that previews the link before opening</li>
          <li>Check the domain carefully (spelling, TLD)</li>
          <li>If it's about work accounts, open the official site manually instead</li>
          <li>Report suspicious QR codes to IT/security</li>
        </ul>

        <div class="checkRow">
          <input id="ack" type="checkbox" />
          <div>
            <div><b>I understand how to verify QR links before opening</b></div>
            <div class="note" style="margin-top:6px">Check to enable completion.</div>
          </div>
        </div>

        <div class="actions">
          <button id="completeBtn" class="primary" disabled>Mark Training as Completed</button>
          <button class="ghost" onclick="window.print()">Print / Save PDF</button>
        </div>

        <div id="success" class="success">
          ✅ Completed. You may be re-tested with QR simulations to measure improvement.
        </div>

        <div class="note">
          Re-measurement: later programs can place different QR scenarios (different technique + context) to track improvement.
        </div>
      </div>
    </div>
  </div>

  <script>
    const ack = document.getElementById("ack");
    const btn = document.getElementById("completeBtn");
    const success = document.getElementById("success");

    ack.addEventListener("change", () => {
      btn.disabled = !ack.checked;
      btn.classList.toggle("enabled", ack.checked);
    });

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.textContent = "Recording...";

      try {
        const response = await fetch("/api/training/complete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            employeeId: "{{employee_id}}",
            programId: "{{program_id}}",
            campaignId: "{{campaign_id}}",
            module: "qr_scan",
            completedAt: new Date().toISOString()
          })
        });

        if (response.ok) {
          success.style.display = "block";
          btn.textContent = "Completed";
        } else {
          const error = await response.json().catch(() => ({}));
          alert("Failed to record completion: " + (error.error || response.statusText));
          btn.disabled = false;
          btn.textContent = "Mark Training as Completed";
        }
      } catch (e) {
        console.error("Could not record completion:", e);
        alert("Network error - please check your connection and try again");
        btn.disabled = false;
        btn.textContent = "Mark Training as Completed";
      }
    });
  </script>
</body>
</html>
'''
