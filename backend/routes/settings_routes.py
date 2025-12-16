from flask import Blueprint, request, jsonify, session
from database import db
from models import Settings, User
import smtplib
from email.mime.text import MIMEText

bp = Blueprint('settings', __name__, url_prefix='/api/settings')


def get_current_user():
    """Helper to get current user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@bp.route('/', methods=['GET'])
def get_settings():
    """Get current user's settings"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    settings = Settings.query.filter_by(user_id=user.id).first()

    if not settings:
        # Create default settings
        settings = Settings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()

    return jsonify(settings.to_dict())


@bp.route('/', methods=['PUT'])
def update_settings():
    """Update user settings"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    settings = Settings.query.filter_by(user_id=user.id).first()

    if not settings:
        settings = Settings(user_id=user.id)
        db.session.add(settings)

    data = request.json

    # Update SMTP settings
    if 'smtp_host' in data:
        settings.smtp_host = data['smtp_host']
    if 'smtp_port' in data:
        settings.smtp_port = int(data['smtp_port']) if data['smtp_port'] else 587
    if 'smtp_username' in data:
        settings.smtp_username = data['smtp_username']
    if 'smtp_password' in data and data['smtp_password'] != '********':
        settings.smtp_password = data['smtp_password']
    if 'smtp_use_tls' in data:
        settings.smtp_use_tls = bool(data['smtp_use_tls'])
    if 'smtp_from_email' in data:
        settings.smtp_from_email = data['smtp_from_email']
    if 'smtp_from_name' in data:
        settings.smtp_from_name = data['smtp_from_name']

    # Update general settings
    if 'notification_email' in data:
        settings.notification_email = data['notification_email']
    if 'timezone' in data:
        settings.timezone = data['timezone']

    # Update AI settings
    print(f"[DEBUG] Received data keys: {list(data.keys())}")
    if 'gemini_api_key' in data:
        print(f"[DEBUG] gemini_api_key value: '{data['gemini_api_key'][:10]}...' (length: {len(data['gemini_api_key'])})" if data['gemini_api_key'] else "[DEBUG] gemini_api_key is empty")
        if data['gemini_api_key'] and data['gemini_api_key'] != '********':
            settings.gemini_api_key = data['gemini_api_key']
            print(f"[DEBUG] API key saved!")
        else:
            print(f"[DEBUG] API key NOT saved (empty or masked)")

    db.session.commit()

    return jsonify({
        'message': 'Settings updated successfully',
        'settings': settings.to_dict()
    })


@bp.route('/smtp/test', methods=['POST'])
def test_smtp():
    """Test SMTP connection"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    settings = Settings.query.filter_by(user_id=user.id).first()

    if not settings or not settings.smtp_host or not settings.smtp_username:
        return jsonify({'error': 'SMTP settings not configured'}), 400

    try:
        # Try to connect to SMTP server
        if settings.smtp_use_tls:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port)

        server.login(settings.smtp_username, settings.smtp_password)
        server.quit()

        return jsonify({'message': 'SMTP connection successful'})

    except smtplib.SMTPAuthenticationError:
        return jsonify({'error': 'Authentication failed. Check username and password.'}), 400
    except smtplib.SMTPConnectError:
        return jsonify({'error': 'Could not connect to SMTP server. Check host and port.'}), 400
    except Exception as e:
        return jsonify({'error': f'SMTP test failed: {str(e)}'}), 400


@bp.route('/gemini/test', methods=['POST'])
def test_gemini():
    """Test Gemini API connection"""
    data = request.json or {}

    # Allow testing with API key from request body (for testing before saving)
    api_key = data.get('api_key')

    # If no key in request or masked, try to get from user settings
    if not api_key or api_key == '********':
        user = get_current_user()
        if user:
            settings = Settings.query.filter_by(user_id=user.id).first()
            if settings and settings.gemini_api_key:
                api_key = settings.gemini_api_key

    # Fallback: try to get any saved key from database
    if not api_key or api_key == '********':
        settings = Settings.query.filter(Settings.gemini_api_key.isnot(None)).first()
        if settings and settings.gemini_api_key:
            api_key = settings.gemini_api_key

    if not api_key or api_key == '********':
        return jsonify({'error': 'No API key provided. Enter an API key first.'}), 400

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        # Test by listing models and making a simple generation
        models = list(genai.list_models())
        model_names = [m.name.replace('models/', '') for m in models if 'generateContent' in m.supported_generation_methods][:5]

        # Try a simple generation to verify it really works
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content('Say OK')

        return jsonify({
            'message': 'Gemini API connection successful!',
            'available_models': model_names,
            'test_response': response.text[:50] if response.text else 'OK'
        })

    except Exception as e:
        error_msg = str(e)
        if 'API_KEY_INVALID' in error_msg or 'invalid' in error_msg.lower():
            return jsonify({'error': 'Invalid API key. Please check your Gemini API key.'}), 400
        if 'quota' in error_msg.lower():
            return jsonify({'error': 'API key valid but quota exceeded. Wait or use a different key.'}), 400
        return jsonify({'error': f'Gemini API test failed: {error_msg}'}), 400


@bp.route('/smtp/send-test', methods=['POST'])
def send_test_email():
    """Send a test email"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    settings = Settings.query.filter_by(user_id=user.id).first()

    if not settings or not settings.smtp_host or not settings.smtp_username:
        return jsonify({'error': 'SMTP settings not configured'}), 400

    data = request.json
    test_email = data.get('email', user.email)

    if not test_email:
        return jsonify({'error': 'Test email address required'}), 400

    try:
        # Create test message
        msg = MIMEText('This is a test email from PhishVision to verify your SMTP settings are working correctly.')
        msg['Subject'] = 'PhishVision SMTP Test'
        msg['From'] = f"{settings.smtp_from_name or 'PhishVision'} <{settings.smtp_from_email or settings.smtp_username}>"
        msg['To'] = test_email

        # Send email
        if settings.smtp_use_tls:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port)

        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)
        server.quit()

        return jsonify({'message': f'Test email sent to {test_email}'})

    except Exception as e:
        return jsonify({'error': f'Failed to send test email: {str(e)}'}), 400
