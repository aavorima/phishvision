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
    """Get a specific QR campaign with scans"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)

    result = campaign.to_dict()
    result['scans'] = [s.to_dict() for s in campaign.scans]

    return jsonify(result)


@bp.route('/campaigns', methods=['POST'])
def create_qr_campaign():
    """Create a new QR code phishing campaign"""
    if not QR_AVAILABLE:
        return jsonify({'error': 'QR code library not installed. Run: pip install qrcode[pil]'}), 500

    data = request.json

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

    if not campaign.qr_image_path:
        return jsonify({'error': 'QR image not generated'}), 404

    qr_path = os.path.join(QR_CODE_DIR, campaign.qr_image_path)

    if not os.path.exists(qr_path):
        return jsonify({'error': 'QR image file not found'}), 404

    return send_file(qr_path, mimetype='image/png')


@bp.route('/campaigns/<campaign_id>/download')
def download_qr_image(campaign_id):
    """Download QR code as image file"""
    campaign = QRCodeCampaign.query.get_or_404(campaign_id)

    if not campaign.qr_image_path:
        return jsonify({'error': 'QR image not generated'}), 404

    qr_path = os.path.join(QR_CODE_DIR, campaign.qr_image_path)

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


# ============================================
# QR CODE SCANNING & TRACKING
# ============================================

@bp.route('/scan/<tracking_id>')
def track_qr_scan(tracking_id):
    """Track when someone scans the QR code"""
    # Find campaign by tracking ID in URL
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

    # Redirect to landing page or training
    if campaign.landing_page_id:
        landing_page = LandingPage.query.get(campaign.landing_page_id)
        if landing_page:
            # Generate a tracking token for this scan
            tracking_token = str(uuid.uuid4())
            html = landing_page.html_content.replace('{{tracking_token}}', tracking_token)
            return render_template_string(html, tracking_token=tracking_token)

    # Default: show training page
    return redirect('/api/qr/training')


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

    return jsonify({
        'campaign': campaign.to_dict(),
        'total_scans': campaign.total_scans,
        'unique_scans': campaign.unique_scans,
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
<!DOCTYPE html>
<html>
<head>
    <title>QR Code Security Awareness</title>
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
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            padding: 60px 20px;
            text-align: center;
        }
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            max-width: 700px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 24px;
        }
        .card h2 {
            color: #e74c3c;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .card p {
            color: #ccc;
            line-height: 1.7;
            margin-bottom: 12px;
        }
        .warning-box {
            background: rgba(231, 76, 60, 0.1);
            border-left: 4px solid #e74c3c;
            padding: 20px;
            margin: 20px 0;
        }
        .warning-box h3 {
            color: #e74c3c;
            margin-bottom: 10px;
        }
        .warning-box ul {
            color: #ccc;
            margin-left: 20px;
        }
        .warning-box li {
            margin-bottom: 8px;
        }
        .icon {
            font-size: 1.5em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>You Scanned a Simulated Malicious QR Code</h1>
        <p>This was a security awareness exercise</p>
    </div>
    <div class="content">
        <div class="card">
            <h2><span class="icon">⚠️</span> What Just Happened?</h2>
            <p>You scanned a QR code that was part of a <strong>phishing simulation</strong>. In a real attack, this could have:</p>
            <ul style="color:#ccc;margin-left:20px;margin-top:10px;">
                <li>Directed you to a fake login page to steal your credentials</li>
                <li>Downloaded malware to your device</li>
                <li>Enrolled your device in a malicious profile</li>
                <li>Redirected you to a payment scam</li>
            </ul>
        </div>

        <div class="card">
            <h2><span class="icon">🔒</span> QR Code Safety Tips</h2>
            <div class="warning-box">
                <h3>Before Scanning ANY QR Code:</h3>
                <ul>
                    <li><strong>Check the source</strong> - Is it from a trusted location?</li>
                    <li><strong>Look for tampering</strong> - Has a sticker been placed over another code?</li>
                    <li><strong>Preview the URL</strong> - Most phone cameras show the URL before opening</li>
                    <li><strong>Verify the domain</strong> - Does it match the expected website?</li>
                    <li><strong>Avoid public QR codes</strong> - Especially on flyers, posters, or parking meters</li>
                    <li><strong>Never enter credentials</strong> - After scanning a QR code from unknown sources</li>
                </ul>
            </div>
        </div>

        <div class="card">
            <h2><span class="icon">📱</span> Safe Scanning Practices</h2>
            <p>If you need to scan a QR code:</p>
            <ul style="color:#ccc;margin-left:20px;margin-top:10px;">
                <li>Use your phone's built-in camera (not third-party QR apps)</li>
                <li>Always preview the URL before opening</li>
                <li>Type the URL manually if you're unsure</li>
                <li>Report suspicious QR codes to IT security</li>
            </ul>
        </div>
    </div>
</body>
</html>
'''
