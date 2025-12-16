"""
Landing Page Routes for Credential Harvesting Simulations
Handles creation, management, and serving of fake login pages
"""

from flask import Blueprint, request, jsonify, render_template_string, redirect
from database import db
from models import LandingPage, CredentialCapture, CampaignTarget, UserRiskScore, Campaign, Employee
from datetime import datetime
import uuid
import json
import requests
from bs4 import BeautifulSoup
import re

bp = Blueprint('landing', __name__, url_prefix='/api/landing')


# ============================================
# LANDING PAGE CRUD
# ============================================

@bp.route('/pages', methods=['GET'])
def get_landing_pages():
    """Get all landing pages"""
    category = request.args.get('category')
    active_only = request.args.get('active', 'true').lower() == 'true'

    query = LandingPage.query

    if active_only:
        query = query.filter_by(is_active=True)

    if category:
        query = query.filter_by(category=category)

    pages = query.order_by(LandingPage.created_at.desc()).all()
    return jsonify([p.to_dict() for p in pages])


@bp.route('/pages/<page_id>', methods=['GET'])
def get_landing_page(page_id):
    """Get a specific landing page"""
    page = LandingPage.query.get_or_404(page_id)
    return jsonify(page.to_dict())


@bp.route('/pages', methods=['POST'])
def create_landing_page():
    """Create a new landing page"""
    data = request.json

    if not data.get('name') or not data.get('html_content'):
        return jsonify({'error': 'Name and HTML content are required'}), 400

    page = LandingPage(
        name=data['name'],
        category=data.get('category', 'custom'),
        description=data.get('description'),
        html_content=data['html_content'],
        redirect_url=data.get('redirect_url'),
        capture_fields=json.dumps(data.get('capture_fields', ['username', 'password'])),
        difficulty=data.get('difficulty', 'medium'),
        is_builtin=False,
        is_active=True
    )

    db.session.add(page)
    db.session.commit()

    return jsonify(page.to_dict()), 201


@bp.route('/pages/<page_id>', methods=['PUT'])
def update_landing_page(page_id):
    """Update a landing page"""
    page = LandingPage.query.get_or_404(page_id)
    data = request.json

    if data.get('name'):
        page.name = data['name']
    if data.get('category'):
        page.category = data['category']
    if data.get('description'):
        page.description = data['description']
    if data.get('html_content'):
        page.html_content = data['html_content']
    if data.get('redirect_url'):
        page.redirect_url = data['redirect_url']
    if data.get('capture_fields'):
        page.capture_fields = json.dumps(data['capture_fields'])
    if data.get('difficulty'):
        page.difficulty = data['difficulty']
    if 'is_active' in data:
        page.is_active = data['is_active']

    db.session.commit()
    return jsonify(page.to_dict())


@bp.route('/pages/<page_id>', methods=['DELETE'])
def delete_landing_page(page_id):
    """Soft delete a landing page"""
    page = LandingPage.query.get_or_404(page_id)

    if page.is_builtin:
        return jsonify({'error': 'Cannot delete built-in pages'}), 400

    page.is_active = False
    db.session.commit()

    return jsonify({'message': 'Landing page deleted'})


# ============================================
# WEBSITE CLONING
# ============================================

@bp.route('/clone', methods=['POST'])
def clone_website():
    """Clone a website to create a landing page"""
    data = request.json
    url = data.get('url')
    name = data.get('name', 'Cloned Page')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts that might cause issues
        for script in soup.find_all('script'):
            script.decompose()

        # Find forms and modify them
        for form in soup.find_all('form'):
            # Change action to our capture endpoint
            form['action'] = '/api/landing/capture/{{tracking_token}}'
            form['method'] = 'POST'

            # Add tracking token hidden field
            hidden = soup.new_tag('input')
            hidden['type'] = 'hidden'
            hidden['name'] = 'tracking_token'
            hidden['value'] = '{{tracking_token}}'
            form.insert(0, hidden)

        # Convert relative URLs to absolute
        for tag in soup.find_all(['img', 'link', 'script']):
            for attr in ['src', 'href']:
                if tag.get(attr) and not tag[attr].startswith(('http', '//', 'data:')):
                    base_url = '/'.join(url.split('/')[:3])
                    tag[attr] = base_url + ('/' if not tag[attr].startswith('/') else '') + tag[attr]

        html_content = str(soup)

        # Detect what category this might be
        category = 'custom'
        url_lower = url.lower()
        if 'microsoft' in url_lower or 'office' in url_lower or 'outlook' in url_lower:
            category = 'microsoft'
        elif 'google' in url_lower or 'gmail' in url_lower:
            category = 'google'
        elif 'bank' in url_lower or 'finance' in url_lower:
            category = 'banking'
        elif 'linkedin' in url_lower:
            category = 'linkedin'
        elif 'facebook' in url_lower or 'meta' in url_lower:
            category = 'facebook'

        # Create landing page
        page = LandingPage(
            name=name,
            category=category,
            description=f'Cloned from {url}',
            html_content=html_content,
            redirect_url=data.get('redirect_url', '/api/track/training'),
            cloned_from_url=url,
            cloned_at=datetime.utcnow(),
            difficulty='hard',
            is_builtin=False,
            is_active=True
        )

        db.session.add(page)
        db.session.commit()

        return jsonify({
            'message': 'Website cloned successfully',
            'page': page.to_dict()
        }), 201

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Clone failed: {str(e)}'}), 500


# ============================================
# SERVE LANDING PAGE & CAPTURE CREDENTIALS
# ============================================

@bp.route('/serve/<tracking_token>')
def serve_landing_page(tracking_token):
    """Serve the landing page for a phishing target"""
    # Find the target in email campaign targets
    target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()

    if not target:
        return "Page not found", 404

    # Get the campaign and its landing page
    campaign = target.campaign

    # Use the campaign's landing page if specified
    page = None
    if campaign.landing_page_id:
        page = LandingPage.query.get(campaign.landing_page_id)

    # Fallback to any active landing page
    if not page:
        page = LandingPage.query.filter_by(is_active=True).first()

    if not page:
        # Return a basic default page
        return render_template_string(DEFAULT_LOGIN_PAGE, tracking_token=tracking_token)

    # Replace tracking token in the HTML
    html = page.html_content.replace('{{tracking_token}}', tracking_token)

    # Record that they visited (clicked)
    if not target.clicked_at:
        target.clicked_at = datetime.utcnow()
        target.ip_address = request.remote_addr
        target.user_agent = request.headers.get('User-Agent', '')
        db.session.commit()

    return render_template_string(html, tracking_token=tracking_token)


@bp.route('/preview/<page_id>')
def preview_landing_page(page_id):
    """Preview a landing page by ID (for admin testing)"""
    page = LandingPage.query.get(page_id)

    if not page:
        return "Page not found", 404

    # Replace tracking token with a demo placeholder
    html = page.html_content.replace('{{tracking_token}}', 'preview-demo')

    # Add a preview banner at the top
    preview_banner = '''
    <div style="background: #f59e0b; color: #000; padding: 10px; text-align: center; font-family: Arial, sans-serif; position: fixed; top: 0; left: 0; right: 0; z-index: 9999;">
        <strong>PREVIEW MODE</strong> - This is how the phishing page will appear to targets. Form submissions are disabled.
    </div>
    <div style="height: 40px;"></div>
    '''

    # Disable form submission in preview
    html = html.replace('method="POST"', 'method="POST" onsubmit="alert(\'Preview mode: Form submission disabled\'); return false;"')

    # Insert banner after <body>
    if '<body>' in html.lower():
        html = html.replace('<body>', '<body>' + preview_banner)
        html = html.replace('<BODY>', '<BODY>' + preview_banner)
    else:
        html = preview_banner + html

    return render_template_string(html)


@bp.route('/capture/<tracking_token>', methods=['POST'])
def capture_credentials(tracking_token):
    """
    Capture credential submission event (NOT actual credentials!)
    This only records that a user submitted the form, not what they entered.
    """
    target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()

    if not target:
        # Invalid/expired token - still show training page
        return redirect('/api/landing/training')

    # Record the submission EVENT (not the actual credentials)
    fields_submitted = []
    for field in ['username', 'email', 'password', 'user', 'pass', 'login']:
        if request.form.get(field):
            fields_submitted.append(field)

    # Create capture record
    capture = CredentialCapture(
        campaign_id=target.campaign_id,
        target_id=target.id,
        email=target.email,
        fields_submitted=json.dumps(fields_submitted),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')
    )
    db.session.add(capture)

    # Update user risk score
    user_risk = UserRiskScore.query.filter_by(email=target.email).first()
    if user_risk:
        user_risk.record_credential_submission()
    else:
        # Create new risk profile
        user_risk = UserRiskScore(
            email=target.email,
            total_credential_submissions=1,
            campaigns_received=1,
            campaigns_clicked=1
        )
        user_risk.calculate_risk_score()
        db.session.add(user_risk)

    # Update HVS score for credential submission
    employee = Employee.query.filter_by(email=target.email).first()
    if employee:
        employee.update_hvs('submitted_credentials')

    db.session.commit()

    # Redirect to training page
    return redirect('/api/landing/training')


@bp.route('/training')
def show_training():
    """Show the awareness training page after credential capture"""
    return render_template_string(TRAINING_PAGE)


# ============================================
# STATISTICS
# ============================================

@bp.route('/stats')
def get_landing_stats():
    """Get credential capture statistics"""
    total_captures = CredentialCapture.query.count()
    unique_users = db.session.query(CredentialCapture.email).distinct().count()

    # Get by campaign
    from sqlalchemy import func
    by_campaign = db.session.query(
        Campaign.name,
        func.count(CredentialCapture.id)
    ).join(Campaign).group_by(Campaign.name).all()

    return jsonify({
        'total_credential_submissions': total_captures,
        'unique_users_compromised': unique_users,
        'by_campaign': [{'campaign': c[0], 'submissions': c[1]} for c in by_campaign]
    })


@bp.route('/repeat-offenders')
def get_repeat_offenders():
    """Get list of repeat offenders who need training"""
    offenders = UserRiskScore.query.filter_by(is_repeat_offender=True).order_by(
        UserRiskScore.risk_score.desc()
    ).all()

    return jsonify({
        'total': len(offenders),
        'users': [u.to_dict() for u in offenders]
    })


@bp.route('/requires-training')
def get_requires_training():
    """Get users who require mandatory training"""
    users = UserRiskScore.query.filter_by(requires_training=True).all()

    return jsonify({
        'total': len(users),
        'users': [u.to_dict() for u in users]
    })


# ============================================
# BUILT-IN LANDING PAGE TEMPLATES
# ============================================

DEFAULT_LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign In</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo img { height: 40px; }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-weight: 600;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input[type="text"],
        input[type="email"],
        input[type="password"] {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 14px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5a6fd6;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #888;
            font-size: 14px;
        }
        .footer a { color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <svg width="50" height="50" viewBox="0 0 24 24" fill="#667eea">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
        </div>
        <h1>Sign In</h1>
        <form action="/api/landing/capture/{{ tracking_token }}" method="POST">
            <input type="hidden" name="tracking_token" value="{{ tracking_token }}">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" placeholder="Enter your email" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter your password" required>
            </div>
            <button type="submit">Sign In</button>
        </form>
        <div class="footer">
            <p>Forgot password? <a href="#">Reset it here</a></p>
        </div>
    </div>
</body>
</html>
'''

TRAINING_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Security Awareness Training</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 15px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .content {
            max-width: 800px;
            margin: -40px auto 40px;
            padding: 0 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .card h2 {
            color: #e74c3c;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .card p {
            color: #555;
            line-height: 1.8;
            margin-bottom: 15px;
        }
        .tips {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
        }
        .tips h3 { color: #856404; margin-bottom: 10px; }
        .tips ul { margin-left: 20px; color: #856404; }
        .tips li { margin-bottom: 8px; }
        .success {
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 20px 0;
        }
        .success h3 { color: #155724; }
        .success p { color: #155724; }
    </style>
</head>
<body>
    <div class="header">
        <h1>This Was a Phishing Simulation</h1>
        <p>You entered your credentials on a simulated phishing page</p>
    </div>
    <div class="content">
        <div class="card">
            <h2>What Happened?</h2>
            <p>You just participated in a security awareness exercise. The page you submitted your credentials to was a <strong>simulated phishing page</strong> designed to test security awareness.</p>
            <p><strong>Don't worry!</strong> Your actual credentials were NOT captured or stored. We only recorded that a submission was made.</p>
        </div>
        <div class="card">
            <h2>How to Spot Phishing</h2>
            <div class="tips">
                <h3>Red Flags to Watch For:</h3>
                <ul>
                    <li>Check the URL - does it match the official website?</li>
                    <li>Look for urgent language or threats</li>
                    <li>Verify the sender's email address carefully</li>
                    <li>Hover over links before clicking to see the real URL</li>
                    <li>Be suspicious of unexpected login requests</li>
                    <li>When in doubt, go directly to the official website</li>
                </ul>
            </div>
        </div>
        <div class="card">
            <div class="success">
                <h3>What to Do Next</h3>
                <p>Report suspicious emails to your IT security team. If you ever enter credentials on a suspicious site, change your password immediately and enable two-factor authentication.</p>
            </div>
        </div>
    </div>
</body>
</html>
'''


def seed_builtin_landing_pages():
    """Seed built-in landing page templates"""
    templates = [
        {
            'name': 'Microsoft 365 Login',
            'category': 'microsoft',
            'description': 'Microsoft 365/Office login page simulation',
            'difficulty': 'hard',
            'html_content': MICROSOFT_LOGIN_TEMPLATE
        },
        {
            'name': 'Google Sign In',
            'category': 'google',
            'description': 'Google account login page simulation',
            'difficulty': 'hard',
            'html_content': GOOGLE_LOGIN_TEMPLATE
        },
        {
            'name': 'Generic Corporate Login',
            'category': 'corporate',
            'description': 'Generic corporate SSO login page',
            'difficulty': 'medium',
            'html_content': DEFAULT_LOGIN_PAGE
        }
    ]

    for t in templates:
        existing = LandingPage.query.filter_by(name=t['name'], is_builtin=True).first()
        if not existing:
            page = LandingPage(
                name=t['name'],
                category=t['category'],
                description=t['description'],
                html_content=t['html_content'],
                difficulty=t['difficulty'],
                is_builtin=True,
                is_active=True
            )
            db.session.add(page)

    db.session.commit()


# Microsoft Login Template
MICROSOFT_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign in to your account</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f2f2f2; margin: 0; padding: 0; }
        .container { max-width: 440px; margin: 100px auto; background: white; padding: 44px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
        .logo { margin-bottom: 16px; }
        .logo img { height: 24px; }
        h1 { font-size: 24px; font-weight: 600; margin-bottom: 24px; }
        input { width: 100%; padding: 6px 10px; font-size: 15px; border: none; border-bottom: 1px solid #666; margin-bottom: 24px; }
        input:focus { outline: none; border-bottom: 2px solid #0067b8; }
        .btn { width: 100%; padding: 10px; background: #0067b8; color: white; border: none; font-size: 15px; cursor: pointer; }
        .btn:hover { background: #005a9e; }
        .links { margin-top: 16px; font-size: 13px; }
        .links a { color: #0067b8; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <svg width="108" height="24" viewBox="0 0 108 24" fill="none">
                <path fill="#F25022" d="M0 0h11v11H0z"/><path fill="#7FBA00" d="M12 0h11v11H12z"/>
                <path fill="#00A4EF" d="M0 12h11v11H0z"/><path fill="#FFB900" d="M12 12h11v11H12z"/>
                <text x="28" y="17" fill="#5e5e5e" font-family="Segoe UI" font-size="15">Microsoft</text>
            </svg>
        </div>
        <h1>Sign in</h1>
        <form action="/api/landing/capture/{{ tracking_token }}" method="POST">
            <input type="hidden" name="tracking_token" value="{{ tracking_token }}">
            <input type="email" name="email" placeholder="Email, phone, or Skype" required>
            <input type="password" name="password" placeholder="Password" required>
            <button class="btn" type="submit">Sign in</button>
        </form>
        <div class="links">
            <a href="#">Can't access your account?</a>
        </div>
    </div>
</body>
</html>
'''

# Google Login Template
GOOGLE_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign in - Google Accounts</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Google Sans', Roboto, Arial, sans-serif; background: #fff; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { width: 450px; padding: 48px 40px; border: 1px solid #dadce0; border-radius: 8px; }
        .logo { text-align: center; margin-bottom: 16px; }
        .logo svg { height: 24px; }
        h1 { text-align: center; font-size: 24px; font-weight: 400; margin-bottom: 8px; }
        .subtitle { text-align: center; color: #5f6368; margin-bottom: 32px; }
        input { width: 100%; padding: 13px 15px; font-size: 16px; border: 1px solid #dadce0; border-radius: 4px; margin-bottom: 24px; }
        input:focus { outline: none; border-color: #1a73e8; }
        .btn { width: 100%; padding: 10px; background: #1a73e8; color: white; border: none; border-radius: 4px; font-size: 14px; font-weight: 500; cursor: pointer; }
        .btn:hover { background: #1557b0; }
        .links { margin-top: 24px; }
        .links a { color: #1a73e8; text-decoration: none; font-size: 14px; }
        .create { text-align: left; margin-top: 48px; }
        .create a { color: #1a73e8; text-decoration: none; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <svg viewBox="0 0 75 24" width="75" height="24">
                <path fill="#4285F4" d="M0 12.5c0-6.9 5.6-12.5 12.5-12.5S25 5.6 25 12.5 19.4 25 12.5 25 0 19.4 0 12.5z"/>
                <text x="30" y="18" fill="#5f6368" font-family="Google Sans, Arial" font-size="18">Google</text>
            </svg>
        </div>
        <h1>Sign in</h1>
        <p class="subtitle">Use your Google Account</p>
        <form action="/api/landing/capture/{{ tracking_token }}" method="POST">
            <input type="hidden" name="tracking_token" value="{{ tracking_token }}">
            <input type="email" name="email" placeholder="Email or phone" required>
            <input type="password" name="password" placeholder="Enter your password" required>
            <button class="btn" type="submit">Next</button>
        </form>
        <div class="links">
            <a href="#">Forgot email?</a>
        </div>
        <div class="create">
            <a href="#">Create account</a>
        </div>
    </div>
</body>
</html>
'''
