"""
Campaign Program API Routes

Endpoints for managing vulnerability profiling campaign programs.
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from database import db
from models import (
    User, Employee, CampaignProgram, ProgramPhase, ScheduledCampaign,
    VulnerabilityProfile, ProgramScenario, ScenarioAssignment, CustomTemplate,
    Campaign, SMSCampaign, QRCodeCampaign
)
from services.campaign_program_service import CampaignProgramService
import uuid

bp = Blueprint('programs', __name__, url_prefix='/api/programs')

# Initialize service
program_service = CampaignProgramService()


def get_current_user():
    """Helper to get current user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user():
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


# =============================================================================
# PROGRAM CRUD
# =============================================================================

@bp.route('/', methods=['GET'])
@require_auth
def get_all_programs():
    """
    Get all campaign programs.

    Query params:
    - status: Filter by status (draft, scheduled, active, paused, completed)
    """
    status = request.args.get('status')

    query = CampaignProgram.query

    if status:
        query = query.filter_by(status=status)

    programs = query.order_by(CampaignProgram.created_at.desc()).all()

    return jsonify({
        'programs': [p.to_dict(include_phases=True) for p in programs],
        'total': len(programs)
    })


@bp.route('/<program_id>', methods=['GET'])
@require_auth
def get_program(program_id):
    """Get a specific program with full details"""
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    from models import Campaign, SMSCampaign, QRCodeCampaign
    result = program.to_dict(include_phases=True)

    # Include statistics
    stats = program_service.get_program_stats(program_id)
    if 'error' not in stats:
        result['stats'] = stats['summary']
        result['technique_effectiveness'] = stats['technique_effectiveness']
        result['phase_stats'] = stats['phase_stats']

    # Add a summary of launched campaigns
    email_campaigns = Campaign.query.filter_by(program_id=program_id).order_by(Campaign.created_at.desc()).all()
    sms_campaigns = SMSCampaign.query.filter_by(program_id=program_id).order_by(SMSCampaign.created_at.desc()).all()
    qr_campaigns = QRCodeCampaign.query.filter_by(program_id=program_id).order_by(QRCodeCampaign.created_at.desc()).all()

    result['launched_campaigns_summary'] = {
        'email': {
            'count': len(email_campaigns),
            'campaigns': [{'id': c.id, 'name': c.name, 'status': c.status, 'created_at': c.created_at.isoformat()} for c in email_campaigns]
        },
        'sms': {
            'count': len(sms_campaigns),
            'campaigns': [{'id': c.id, 'name': c.name, 'status': c.status, 'created_at': c.created_at.isoformat()} for c in sms_campaigns]
        },
        'qr': {
            'count': len(qr_campaigns),
            'campaigns': [{'id': c.id, 'name': c.name, 'status': c.status, 'created_at': c.created_at.isoformat()} for c in qr_campaigns]
        }
    }

    return jsonify(result)


@bp.route('/', methods=['POST'])
@require_auth
def create_program():
    """
    Create a new vulnerability profiling program.

    Request body:
    {
        "name": "Q1 2024 Security Assessment",
        "description": "Monthly phishing awareness program",
        "duration_days": 30,
        "techniques_to_test": ["urgency", "authority", "fear", "curiosity", "reward", "social_proof"],
        "vectors_to_test": ["email"],
        "emails_per_week_per_user": 2,
        "target_all_employees": true,
        "target_departments": ["Finance", "HR"],  // if not targeting all
        "target_employee_ids": [],  // for specific employees
        "use_progressive_difficulty": true,
        "adapt_to_responses": true,
        "scheduled_start": "2024-01-15T09:00:00",

        // NEW: Vector configurations for immediate sending
        "email_config": {...},  // Email vector config from UI
        "sms_config": {...},    // SMS vector config from UI
        "qr_config": {...}      // QR vector config from UI
    }
    """
    data = request.json
    user = get_current_user()

    if not data.get('name'):
        return jsonify({'error': 'Program name is required'}), 400

    # Parse scheduled_start if provided
    scheduled_start = None
    if data.get('scheduled_start'):
        try:
            scheduled_start = datetime.fromisoformat(data['scheduled_start'].replace('Z', '+00:00'))
        except:
            return jsonify({'error': 'Invalid scheduled_start format'}), 400

    # Create the base program using the existing service
    program = program_service.create_program(
        name=data['name'],
        description=data.get('description'),
        duration_days=data.get('duration_days', 30),
        techniques_to_test=data.get('techniques_to_test'),
        vectors_to_test=data.get('vectors_to_test'),
        difficulty_levels=data.get('difficulty_levels'),
        emails_per_week_per_user=data.get('emails_per_week_per_user', 2),
        target_all_employees=data.get('target_all_employees', False),
        target_departments=data.get('target_departments'),
        target_employee_ids=data.get('target_employee_ids'),
        use_progressive_difficulty=data.get('use_progressive_difficulty', True),
        adapt_to_responses=data.get('adapt_to_responses', True),
        scheduled_start=scheduled_start,
        created_by=user.id if user else None
    )

    # NEW: Process vector configurations and launch campaigns immediately
    results = {
        'program': program.to_dict(include_phases=True),
        'campaigns_launched': []
    }

    # Process EMAIL vector
    if data.get('email_config'):
        email_result = _launch_email_campaign_from_config(user, program, data['email_config'])
        if email_result:
            results['campaigns_launched'].append(email_result)

    # Process SMS vector
    if data.get('sms_config'):
        sms_result = _launch_sms_campaign_from_config(user, program, data['sms_config'])
        if sms_result:
            results['campaigns_launched'].append(sms_result)

    # Process QR vector
    if data.get('qr_config'):
        qr_result = _launch_qr_campaign_from_config(user, program, data['qr_config'])
        if qr_result:
            results['campaigns_launched'].append(qr_result)

    return jsonify(results), 201


# =============================================================================
# HELPER FUNCTIONS FOR IMMEDIATE CAMPAIGN LAUNCHING
# =============================================================================

def _launch_email_campaign_from_config(user, program, email_config):
    """
    Launch email campaign immediately from profiling program email_config.

    email_config structure:
    {
        "template_id": "uuid",
        "target_selection": "employees" | "manual" | "csv",
        "search_query": "Finance",  // for employees
        "selected_department": "Finance",  // for employees
        "manual_emails": "email1@test.com\nemail2@test.com",  // for manual
        "csv_content": "...",  // for csv
        "landing_page_id": "uuid"  // optional
    }
    """
    from models import Campaign, CampaignTarget, CustomTemplate, LandingPage, Employee, Settings
    from services.email_service import EmailService
    from services.email_parser import parse_email_to_name, substitute_template_variables
    import json
    import os

    try:
        # Get template
        template_id = email_config.get('template_id')
        if not template_id:
            return {'error': 'No template selected for email campaign', 'vector': 'email'}

        template = CustomTemplate.query.get(template_id)
        if not template or not template.is_active:
            return {'error': 'Email template not found or inactive', 'vector': 'email'}

        # Collect target emails and employee data
        target_recipients = []  # List of dicts with email, first_name, last_name
        target_selection = email_config.get('target_selection', 'employees')

        if target_selection == 'employees':
            # Get employees from database
            department = email_config.get('selected_department')
            search_query = email_config.get('search_query', '')

            query = Employee.query
            if department:
                query = query.filter_by(department=department)
            if search_query:
                query = query.filter(
                    db.or_(
                        Employee.first_name.ilike(f'%{search_query}%'),
                        Employee.last_name.ilike(f'%{search_query}%'),
                        Employee.email.ilike(f'%{search_query}%'),
                        Employee.department.ilike(f'%{search_query}%')
                    )
                )

            employees = query.all()
            target_recipients = [
                {
                    'email': emp.email,
                    'first_name': emp.first_name,
                    'last_name': emp.last_name
                }
                for emp in employees if emp.email
            ]

        elif target_selection == 'manual':
            # Parse manual email entries (format: "Name, email@example.com, Department" or "Name, email@example.com" or just "email@example.com")
            manual_emails = email_config.get('manual_emails', '')
            for line in manual_emails.split('\n'):
                line = line.strip()
                if not line or '@' not in line:
                    continue

                department = None
                # Check if line contains comma (Name, Email, Department format)
                if ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        # Name, Email, Department format
                        name = parts[0].strip()
                        email = parts[1].strip()
                        department = parts[2].strip()
                    elif len(parts) == 2:
                        # Name, Email format
                        name = parts[0].strip()
                        email = parts[1].strip()
                    else:
                        # Just email
                        name = ''
                        email = parts[0].strip()

                    # Split name into first and last
                    name_parts = name.split(' ', 1)
                    first_name = name_parts[0] if len(name_parts) > 0 else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                else:
                    # Just email, try to parse name from email
                    email = line
                    parsed = parse_email_to_name(email)
                    first_name = parsed.get('first_name', '')
                    last_name = parsed.get('last_name', '')

                target_recipients.append({
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'department': department
                })

        elif target_selection == 'csv':
            # Parse CSV content
            csv_content = email_config.get('csv_content', '')
            lines = csv_content.split('\n')
            for line in lines:
                line = line.strip()
                if not line or not '@' in line:
                    continue
                parts = line.split(',')
                email = parts[0].strip()
                first_name = parts[1].strip() if len(parts) > 1 else ''
                last_name = parts[2].strip() if len(parts) > 2 else ''

                if not first_name and not last_name:
                    # Try to parse from email
                    parsed = parse_email_to_name(email)
                    first_name = parsed.get('first_name', '')
                    last_name = parsed.get('last_name', '')

                target_recipients.append({
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                })

        if not target_recipients:
            return {'error': 'No email recipients found', 'vector': 'email'}

        # Deduplicate recipients by email to prevent duplicate sends
        seen_emails = set()
        deduplicated_recipients = []
        for recipient in target_recipients:
            if recipient['email'] not in seen_emails:
                seen_emails.add(recipient['email'])
                deduplicated_recipients.append(recipient)

        target_recipients = deduplicated_recipients

        # Get email service configured for user
        settings = Settings.query.filter_by(user_id=user.id).first()
        email_service = EmailService.from_user_settings(settings, allow_env_fallback=False)

        if not email_service.is_configured():
            return {'error': 'SMTP not configured. Please configure SMTP settings first.', 'vector': 'email'}

        # Create Campaign record
        campaign = Campaign(
            name=f"{program.name} - Email Campaign",
            template_type=template_id,
            subject=template.subject,
            target_emails=json.dumps([r['email'] for r in target_recipients]),
            status='active',
            landing_page_id=email_config.get('landing_page_id'),
            program_id=program.id
        )
        db.session.add(campaign)
        db.session.flush()

        # Send emails to targets
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        landing_page = None
        if email_config.get('landing_page_id'):
            landing_page = LandingPage.query.get(email_config['landing_page_id'])

        emails_sent = 0
        emails_failed = 0

        for recipient in target_recipients:
            # Generate tracking token
            tracking_token = str(uuid.uuid4())

            # Prepare recipient data
            first_name = recipient.get('first_name', '')
            last_name = recipient.get('last_name', '')
            full_name = f"{first_name} {last_name}".strip() if first_name or last_name else None
            department = recipient.get('department')

            # Create target record
            target = CampaignTarget(
                campaign_id=campaign.id,
                name=full_name,
                email=recipient['email'],
                department=department,
                tracking_token=tracking_token
            )
            db.session.add(target)
            recipient_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': recipient['email'],
                'full_name': f"{first_name} {last_name}".strip() or recipient['email'].split('@')[0],
                'base_url': base_url
            }

            # Set tracking link
            if landing_page:
                recipient_data['tracking_link'] = f"{base_url}/api/landing/serve/{tracking_token}"
            else:
                recipient_data['tracking_link'] = f"{base_url}/api/track/click/{tracking_token}"

            # Apply template substitutions
            final_subject = substitute_template_variables(template.subject, recipient_data)
            final_html = substitute_template_variables(template.html_content, recipient_data)

            # Add tracking pixel
            tracking_pixel = f'<img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />'
            if '</body>' in final_html:
                final_html = final_html.replace('</body>', f'{tracking_pixel}</body>')
            else:
                final_html += tracking_pixel

            # Send email
            if email_service.send_email(recipient['email'], final_subject, final_html, from_name_override=template.from_name):
                emails_sent += 1
            else:
                emails_failed += 1

        db.session.commit()

        return {
            'vector': 'email',
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'sent': emails_sent,
            'failed': emails_failed,
            'total': len(target_recipients)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': f'Failed to launch email campaign: {str(e)}', 'vector': 'email'}


def _launch_sms_campaign_from_config(user, program, sms_config):
    """
    Launch SMS campaign immediately from profiling program sms_config.

    sms_config structure:
    {
        "template_id": "uuid",
        "sender_id": "Birbank" | "+994..." | "CustomName",
        "message_template": "Your message {{link}}",
        "target_selection": "employees" | "manual" | "csv",
        "selected_department": "Finance",  // for employees
        "search_query": "",  // for employees
        "manual_numbers": "+994...\n+994...",  // for manual
        "csv_content": "...",  // for csv
        "landing_page_id": "uuid"  // optional
    }
    """
    from models import SMSCampaign, SMSTarget, LandingPage, Employee, Settings
    import os
    import json

    try:
        # Get message template
        message_template = sms_config.get('message_template')
        if not message_template:
            return {'error': 'No message template provided for SMS campaign', 'vector': 'sms'}

        # Collect target phone numbers
        target_phones = []
        target_selection = sms_config.get('target_selection', 'employees')

        if target_selection == 'employees':
            # Get employees by filter
            department = sms_config.get('selected_department')
            search_query = sms_config.get('search_query', '')

            query = Employee.query
            if department:
                query = query.filter_by(department=department)
            if search_query:
                query = query.filter(
                    db.or_(
                        Employee.first_name.ilike(f'%{search_query}%'),
                        Employee.last_name.ilike(f'%{search_query}%'),
                        Employee.email.ilike(f'%{search_query}%'),
                        Employee.phone_number.ilike(f'%{search_query}%')
                    )
                )

            employees = query.all()
            target_phones = [
                {
                    'name': f"{emp.first_name} {emp.last_name}".strip() if emp.first_name or emp.last_name else None,
                    'phone': emp.phone_number
                }
                for emp in employees if emp.phone_number
            ]

        elif target_selection == 'manual':
            # Parse manual numbers (format: "Name, +994501234567, Department" or "Name, +994501234567" or just "+994501234567")
            manual_numbers = sms_config.get('manual_numbers', '')
            target_phones = []
            for line in manual_numbers.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Check if line contains comma (Name, Phone, Department format)
                if ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3:
                        # Name, Phone, Department format
                        name = parts[0].strip()
                        phone = parts[1].strip()
                        department = parts[2].strip()
                        target_phones.append({'name': name, 'phone': phone, 'department': department})
                    elif len(parts) == 2:
                        # Name, Phone format
                        name = parts[0].strip()
                        phone = parts[1].strip()
                        target_phones.append({'name': name, 'phone': phone, 'department': None})
                    else:
                        # Just phone
                        target_phones.append({'name': None, 'phone': parts[0].strip(), 'department': None})
                else:
                    # Just phone number
                    target_phones.append({'name': None, 'phone': line, 'department': None})

        elif target_selection == 'csv':
            # Parse CSV content (format: Name,Phone or just Phone)
            csv_content = sms_config.get('csv_content', '')
            lines = csv_content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if ',' in line:
                    parts = line.split(',', 1)
                    name = parts[0].strip()
                    phone = parts[1].strip()
                    if phone.startswith('+'):
                        target_phones.append({'name': name, 'phone': phone})
                elif line.startswith('+'):
                    target_phones.append({'name': None, 'phone': line})

        if not target_phones:
            return {'error': 'No phone numbers found for SMS campaign', 'vector': 'sms'}

        # Deduplicate phone numbers to prevent duplicate sends
        seen_phones = set()
        deduplicated_phones = []
        for phone_data in target_phones:
            phone_number = phone_data['phone'] if isinstance(phone_data, dict) else phone_data
            if phone_number not in seen_phones:
                seen_phones.add(phone_number)
                deduplicated_phones.append(phone_data)

        target_phones = deduplicated_phones

        # Create SMS Campaign
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        campaign = SMSCampaign(
            name=f"{program.name} - SMS Campaign",
            description=f"SMS campaign from program: {program.name}",
            message_template=message_template,
            sender_id=sms_config.get('sender_id'),
            target_url=f"{base_url}/api/sms/click",
            landing_page_id=sms_config.get('landing_page_id'),
            status='draft',
            program_id=program.id
        )
        db.session.add(campaign)
        db.session.flush()

        # Add targets
        for phone_data in target_phones:
            tracking_token = str(uuid.uuid4())[:12]
            # Handle both old format (just string) and new format (dict with name and phone)
            if isinstance(phone_data, dict):
                phone_number = phone_data['phone']
                name = phone_data.get('name')
                department = phone_data.get('department')
            else:
                phone_number = phone_data
                name = None
                department = None

            target = SMSTarget(
                campaign_id=campaign.id,
                name=name,
                phone_number=phone_number,
                department=department,
                tracking_token=tracking_token
            )
            db.session.add(target)

        db.session.commit()

        # Now send the campaign using existing SMS sending logic
        from routes.sms_routes import send_mock_sms, send_twilio_sms_new
        try:
            from services.twilio_sms_service import TWILIO_AVAILABLE
        except:
            TWILIO_AVAILABLE = False

        # Get Twilio credentials
        settings = Settings.query.filter_by(user_id=user.id).first()
        twilio_sid = None
        twilio_token = None
        twilio_phone = None

        if settings:
            twilio_sid = settings.twilio_account_sid
            twilio_token = settings.twilio_auth_token
            twilio_phone = settings.twilio_phone_number

        # Fallback to environment
        if not all([twilio_sid, twilio_token, twilio_phone]):
            twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
            twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')

        use_mock = not (TWILIO_AVAILABLE and twilio_sid and twilio_token and twilio_phone)

        if use_mock:
            send_results = send_mock_sms(campaign)
        else:
            send_results = send_twilio_sms_new(campaign, twilio_sid, twilio_token, twilio_phone)

        campaign.status = 'active'
        campaign.total_sent = send_results['sent']
        campaign.total_delivered = send_results['delivered']
        db.session.commit()

        return {
            'vector': 'sms',
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'mock_mode': use_mock,
            'sent': send_results['sent'],
            'delivered': send_results['delivered'],
            'failed': send_results.get('failed', 0),
            'total': len(target_phones)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': f'Failed to launch SMS campaign: {str(e)}', 'vector': 'sms'}


def _launch_qr_campaign_from_config(user, program, qr_config):
    """
    Create a new QR campaign for this program and send QR code posters to target employees.

    qr_config structure:
    {
        "qr_campaign_id": "uuid",  // ID of template QR poster to copy from
        "target_selection": "employees" | "manual" | "csv",
        "selected_department": "Finance",
        "search_query": "",
        "manual_emails": "Name, email@example.com, Department\\n...",
        "csv_data": "Name, email@example.com, Department\\n..."
    }
    """
    from models import QRCodeCampaign, Employee, Settings, QRCodeTarget
    from services.email_service import EmailService
    import os
    import secrets
    from datetime import datetime

    try:
        print(f"[QR CAMPAIGN] Starting QR campaign launch for program: {program.name} (ID: {program.id})")

        # Get the template QR poster that user selected
        template_qr_id = qr_config.get('qr_campaign_id')
        if not template_qr_id:
            print("[QR CAMPAIGN ERROR] No QR poster ID in config")
            return {'error': 'No QR poster selected', 'vector': 'qr'}

        print(f"[QR CAMPAIGN] Using template QR ID: {template_qr_id}")
        template_qr = QRCodeCampaign.query.get(template_qr_id)
        if not template_qr:
            print(f"[QR CAMPAIGN ERROR] Template QR not found: {template_qr_id}")
            return {'error': 'QR poster not found', 'vector': 'qr'}

        # Collect target employees
        target_employees = []

        # Handle manual entry
        if qr_config.get('target_selection') == 'manual' and qr_config.get('manual_emails'):
            manual_lines = qr_config['manual_emails'].strip().split('\n')
            for line in manual_lines:
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 2:
                        name = parts[0] if len(parts) > 0 else ''
                        email = parts[1] if len(parts) > 1 else ''
                        department = parts[2] if len(parts) > 2 else ''
                        if email:
                            target_employees.append({
                                'name': name,
                                'email': email,
                                'department': department
                            })
        # Handle CSV upload
        elif qr_config.get('target_selection') == 'csv' and qr_config.get('csv_data'):
            csv_lines = qr_config['csv_data'].strip().split('\n')
            for line in csv_lines:
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 2:
                        name = parts[0] if len(parts) > 0 else ''
                        email = parts[1] if len(parts) > 1 else ''
                        department = parts[2] if len(parts) > 2 else ''
                        if email:
                            target_employees.append({
                                'name': name,
                                'email': email,
                                'department': department
                            })
        else:
            # Handle employee selection
            department = qr_config.get('selected_department')
            search_query = qr_config.get('search_query', '')

            query = Employee.query
            if department:
                query = query.filter_by(department=department)
            if search_query:
                query = query.filter(
                    db.or_(
                        Employee.first_name.ilike(f'%{search_query}%'),
                        Employee.last_name.ilike(f'%{search_query}%'),
                        Employee.department.ilike(f'%{search_query}%')
                    )
                )

            employees = query.all()
            target_employees = [
                {
                    'name': f"{emp.first_name} {emp.last_name}".strip() or emp.email,
                    'email': emp.email,
                    'department': emp.department or ''
                }
                for emp in employees
            ]

        if not target_employees:
            return {'error': 'No target employees found', 'vector': 'qr'}

        # Deduplicate target employees by email to prevent duplicate sends
        seen_emails = set()
        deduplicated_employees = []
        for emp in target_employees:
            if emp['email'] not in seen_emails:
                seen_emails.add(emp['email'])
                deduplicated_employees.append(emp)

        target_employees = deduplicated_employees

        # CREATE NEW QR CAMPAIGN for this program (copy from template)
        campaign = QRCodeCampaign(
            name=f"{program.name} - QR Campaign",
            description=template_qr.description,
            target_url=template_qr.target_url,
            landing_page_id=template_qr.landing_page_id,
            qr_image_path=template_qr.qr_image_path,  # Use same QR image
            status='active',
            placement_location='Email Poster',
            program_id=program.id  # LINK TO PROGRAM!
        )
        db.session.add(campaign)
        db.session.flush()

        # Get email service
        settings = Settings.query.filter_by(user_id=user.id).first()
        email_service = EmailService.from_user_settings(settings, allow_env_fallback=True)

        if not email_service.is_configured():
            return {'error': 'Email service is not configured. Please configure SMTP settings.', 'vector': 'qr'}

        # Verify QR code image exists
        if not campaign.qr_image_path:
            print(f"[QR CAMPAIGN ERROR] Template QR has no image path. Template ID: {template_qr.id}")
            return {'error': 'QR code image not found for this campaign', 'vector': 'qr'}

        # Get QR code image path
        import os as os_module
        QR_CODE_DIR = os_module.path.join(os_module.path.dirname(os_module.path.dirname(__file__)), 'static', 'qrcodes')
        qr_path = os_module.path.join(QR_CODE_DIR, campaign.qr_image_path)

        print(f"[QR CAMPAIGN DEBUG] Looking for QR image at: {qr_path}")
        print(f"[QR CAMPAIGN DEBUG] QR image exists: {os_module.path.exists(qr_path)}")

        if not os_module.path.exists(qr_path):
            print(f"[QR CAMPAIGN ERROR] QR image file not found: {qr_path}")
            return {'error': f'QR code image file not found: {qr_path}', 'vector': 'qr'}

        # Create QR targets (just like Email/SMS campaigns)
        emails_sent = 0
        emails_failed = 0

        for recipient in target_employees:
            email_addr = recipient.get('email')
            if not email_addr:
                continue

            # Create target record
            tracking_token = secrets.token_urlsafe(32)
            target = QRCodeTarget(
                campaign_id=campaign.id,
                name=recipient.get('name'),
                email=email_addr,
                department=recipient.get('department'),
                tracking_token=tracking_token,
                sent_at=None  # Will be set after email is sent
            )
            db.session.add(target)

        # Commit targets before sending emails
        db.session.commit()

        # Generate base tracking URL
        import os as os_module
        base_url = os_module.environ.get('BASE_URL', 'http://localhost:5000')

        # Send poster to each recipient with personalized QR code
        import qrcode
        import io

        for recipient in target_employees:
            email_addr = recipient.get('email')
            if not email_addr:
                continue

            # Find the target record to get their tracking token
            target = QRCodeTarget.query.filter_by(campaign_id=campaign.id, email=email_addr).first()
            if not target:
                continue

            # Generate personalized tracking URL for this target
            tracking_url = f"{base_url}/api/qr/scan/{target.tracking_token}"

            # Generate personalized QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(tracking_url)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color='#000000', back_color='white')

            # Save QR code to bytes for email attachment
            qr_bytes = io.BytesIO()
            qr_img.save(qr_bytes, format='PNG')
            qr_bytes.seek(0)

            # Save to temp file for email attachment
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_qr:
                qr_img.save(temp_qr, format='PNG')
                temp_qr_path = temp_qr.name

            # Generate poster HTML with CID reference
            qr_cid = f"qrcode_{target.tracking_token}"
            email_html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Special Offer</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #ffffff;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; background-color: #f8f9fa; border: 3px solid #333; border-radius: 10px; padding: 50px 40px;">
            <h1 style="color: #333; margin: 0 0 30px 0; font-size: 32px;">Scan to Join!</h1>

            {f'<p style="color: #666; font-size: 18px; margin: 0 0 40px 0; line-height: 1.5;">{campaign.description}</p>' if campaign.description else ''}

            <div style="margin: 40px 0;">
                <img src="cid:{qr_cid}" alt="QR Code" style="width: 350px; height: 350px; max-width: 100%; display: block; margin: 0 auto;">
            </div>

            <p style="color: #666; font-size: 18px; margin: 30px 0 0 0; line-height: 1.6;">
                📱 Scan this QR code with your phone camera<br>
                to access exclusive content!
            </p>
        </div>
    </div>
</body>
</html>
'''

            # Use template QR poster name as subject
            subject = template_qr.name if template_qr.name else campaign.name
            success = email_service.send_email_with_inline_image(email_addr, subject, email_html, temp_qr_path, qr_cid)

            # Clean up temp file
            try:
                os_module.unlink(temp_qr_path)
            except:
                pass

            if success:
                emails_sent += 1
                target.sent_at = datetime.utcnow()
            else:
                emails_failed += 1

        # Commit sent_at timestamps
        db.session.commit()

        result = {
            'vector': 'qr',
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'sent': emails_sent,
            'failed': emails_failed,
            'total': len(target_employees)
        }

        print(f"[QR CAMPAIGN] Successfully launched! Campaign ID: {campaign.id}, Sent: {emails_sent}, Failed: {emails_failed}")
        return result

    except Exception as e:
        import traceback
        print(f"[QR CAMPAIGN ERROR] Exception occurred:")
        traceback.print_exc()
        return {'error': f'Failed to launch QR campaign: {str(e)}', 'vector': 'qr'}



@bp.route('/<program_id>', methods=['PUT'])
@require_auth
def update_program(program_id):
    """Update a program (only allowed for draft/scheduled programs)"""
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    if program.status not in ['draft', 'scheduled']:
        return jsonify({'error': 'Cannot modify active or completed programs'}), 400

    data = request.json

    # Update allowed fields
    if 'name' in data:
        program.name = data['name']
    if 'description' in data:
        program.description = data['description']
    if 'duration_days' in data:
        program.duration_days = data['duration_days']
    if 'emails_per_week_per_user' in data:
        program.emails_per_week_per_user = data['emails_per_week_per_user']
    if 'techniques_to_test' in data:
        import json
        program.techniques_to_test = json.dumps(data['techniques_to_test'])
    if 'vectors_to_test' in data:
        import json
        program.vectors_to_test = json.dumps(data['vectors_to_test'])
    if 'target_all_employees' in data:
        program.target_all_employees = data['target_all_employees']
    if 'target_departments' in data:
        import json
        program.target_departments = json.dumps(data['target_departments'])
    if 'use_progressive_difficulty' in data:
        program.use_progressive_difficulty = data['use_progressive_difficulty']
    if 'adapt_to_responses' in data:
        program.adapt_to_responses = data['adapt_to_responses']
    if 'scheduled_start' in data:
        try:
            program.scheduled_start = datetime.fromisoformat(data['scheduled_start'].replace('Z', '+00:00'))
        except:
            pass

    program.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(program.to_dict(include_phases=True))


@bp.route('/<program_id>', methods=['DELETE'])
@require_auth
def delete_program(program_id):
    """Delete a program (allowed for draft and scheduled programs)"""
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    if program.status not in ['draft', 'scheduled']:
        return jsonify({'error': 'Can only delete draft or scheduled programs. Complete or cancel active programs first.'}), 400

    # Delete related records to avoid foreign key constraints
    try:
        # Use raw SQL to delete all related records to avoid schema issues
        # The database schema may not match the model definitions

        # 1. Delete scheduled campaigns
        db.session.execute(
            db.text("DELETE FROM scheduled_campaigns WHERE program_id = :program_id"),
            {"program_id": program_id}
        )

        # 2. Get all scenario IDs for this program
        scenario_result = db.session.execute(
            db.text("SELECT id FROM program_scenarios WHERE program_id = :program_id"),
            {"program_id": program_id}
        )
        scenario_ids = [row[0] for row in scenario_result]

        # 3. Delete scenario assignments for these scenarios
        for scenario_id in scenario_ids:
            db.session.execute(
                db.text("DELETE FROM scenario_assignments WHERE scenario_id = :scenario_id"),
                {"scenario_id": scenario_id}
            )

        # 4. Delete program scenarios
        db.session.execute(
            db.text("DELETE FROM program_scenarios WHERE program_id = :program_id"),
            {"program_id": program_id}
        )

        # 5. Delete program phases
        db.session.execute(
            db.text("DELETE FROM program_phases WHERE program_id = :program_id"),
            {"program_id": program_id}
        )

        # 6. Finally delete the program itself
        db.session.execute(
            db.text("DELETE FROM campaign_programs WHERE id = :program_id"),
            {"program_id": program_id}
        )

        db.session.commit()

        return jsonify({'success': True, 'message': 'Program deleted successfully'})
    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"[DELETE ERROR] {error_detail}")
        return jsonify({'error': f'Failed to delete program: {str(e)}'}), 500


# =============================================================================
# PROGRAM LIFECYCLE
# =============================================================================

@bp.route('/<program_id>/schedule', methods=['POST'])
@require_auth
def schedule_program(program_id):
    """
    Schedule a program - generates all scheduled campaigns.
    Must be called before starting.
    """
    result = program_service.schedule_program(program_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@bp.route('/<program_id>/start', methods=['POST'])
@require_auth
def start_program(program_id):
    """Start a scheduled program"""
    result = program_service.start_program(program_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@bp.route('/<program_id>/pause', methods=['POST'])
@require_auth
def pause_program(program_id):
    """Pause an active program"""
    result = program_service.pause_program(program_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@bp.route('/<program_id>/resume', methods=['POST'])
@require_auth
def resume_program(program_id):
    """Resume a paused program"""
    result = program_service.resume_program(program_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@bp.route('/<program_id>/complete', methods=['POST'])
@require_auth
def complete_program(program_id):
    """Mark a program as completed (ends early if active)"""
    result = program_service.complete_program(program_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


# =============================================================================
# PROGRAM STATISTICS
# =============================================================================

@bp.route('/<program_id>/stats', methods=['GET'])
@require_auth
def get_program_stats(program_id):
    """Get comprehensive statistics for a program"""
    stats = program_service.get_program_stats(program_id)

    if 'error' in stats:
        return jsonify(stats), 404

    return jsonify(stats)


@bp.route('/<program_id>/employees', methods=['GET'])
@require_auth
def get_program_employees(program_id):
    """
    Get list of employees in a program with their current vulnerability status.

    Query params:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20)
    """
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Get unique employee IDs from scheduled campaigns
    scheduled = ScheduledCampaign.query.filter_by(program_id=program_id).all()
    employee_ids = list(set(s.employee_id for s in scheduled))

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated_ids = employee_ids[start:end]

    employees_data = []
    for emp_id in paginated_ids:
        employee = Employee.query.get(emp_id)
        if not employee:
            continue

        # Get employee's campaigns in this program
        emp_campaigns = [s for s in scheduled if s.employee_id == emp_id]

        # Get vulnerability profile
        profile = VulnerabilityProfile.query.filter_by(employee_id=emp_id).first()

        employees_data.append({
            'employee': employee.to_dict(),
            'program_stats': {
                'total_scheduled': len(emp_campaigns),
                'sent': sum(1 for c in emp_campaigns if c.status == 'sent'),
                'clicked': sum(1 for c in emp_campaigns if c.link_clicked),
                'credentials_submitted': sum(1 for c in emp_campaigns if c.credentials_submitted)
            },
            'vulnerability_profile': {
                'overall_score': profile.overall_vulnerability_score if profile else 50,
                'risk_level': profile.risk_level if profile else 'medium',
                'trend': profile.improvement_trend if profile else 'stable'
            } if profile else None
        })

    return jsonify({
        'employees': employees_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': len(employee_ids),
            'pages': (len(employee_ids) + per_page - 1) // per_page
        }
    })


@bp.route('/<program_id>/timeline', methods=['GET'])
@require_auth
def get_program_timeline(program_id):
    """Get timeline of scheduled and sent campaigns"""
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    scheduled = ScheduledCampaign.query.filter_by(program_id=program_id).order_by(
        ScheduledCampaign.scheduled_for.asc()
    ).all()

    # Group by date
    timeline = {}
    for s in scheduled:
        date_key = s.scheduled_for.strftime('%Y-%m-%d')
        if date_key not in timeline:
            timeline[date_key] = {
                'date': date_key,
                'scheduled': 0,
                'sent': 0,
                'clicked': 0,
                'campaigns': []
            }

        timeline[date_key]['scheduled'] += 1
        if s.status == 'sent':
            timeline[date_key]['sent'] += 1
        if s.link_clicked:
            timeline[date_key]['clicked'] += 1

        # Only include first 10 campaigns per day in detail
        if len(timeline[date_key]['campaigns']) < 10:
            employee = Employee.query.get(s.employee_id)
            timeline[date_key]['campaigns'].append({
                'id': s.id,
                'employee_name': f"{employee.first_name} {employee.last_name}" if employee else 'Unknown',
                'technique': s.technique_tested,
                'difficulty': s.difficulty_level,
                'status': s.status,
                'clicked': s.link_clicked
            })

    return jsonify({
        'timeline': list(timeline.values()),
        'total_days': len(timeline)
    })


# =============================================================================
# PHASES
# =============================================================================

@bp.route('/<program_id>/phases', methods=['GET'])
@require_auth
def get_program_phases(program_id):
    """Get all phases for a program"""
    phases = ProgramPhase.query.filter_by(program_id=program_id).order_by(
        ProgramPhase.phase_number.asc()
    ).all()

    return jsonify({
        'phases': [p.to_dict() for p in phases],
        'total': len(phases)
    })


@bp.route('/<program_id>/phases/<phase_id>', methods=['PUT'])
@require_auth
def update_phase(program_id, phase_id):
    """Update a phase configuration (only for draft programs)"""
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    if program.status != 'draft':
        return jsonify({'error': 'Can only modify phases of draft programs'}), 400

    phase = ProgramPhase.query.get(phase_id)
    if not phase or phase.program_id != program_id:
        return jsonify({'error': 'Phase not found'}), 404

    data = request.json
    import json

    if 'name' in data:
        phase.name = data['name']
    if 'description' in data:
        phase.description = data['description']
    if 'difficulty_level' in data:
        phase.difficulty_level = data['difficulty_level']
    if 'techniques_focus' in data:
        phase.techniques_focus = json.dumps(data['techniques_focus'])
    if 'vectors_focus' in data:
        phase.vectors_focus = json.dumps(data['vectors_focus'])
    if 'duration_days' in data:
        phase.duration_days = data['duration_days']

    db.session.commit()

    return jsonify(phase.to_dict())


# =============================================================================
# SCENARIO MANAGEMENT
# =============================================================================

@bp.route('/<program_id>/scenarios', methods=['GET'])
@require_auth
def get_program_scenarios(program_id):
    """
    Get all scenarios for a program.
    """
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    scenarios = ProgramScenario.query.filter_by(program_id=program_id).all()

    # Include assignment counts
    result = []
    for scenario in scenarios:
        scenario_dict = scenario.to_dict()
        scenario_dict['assignment_count'] = ScenarioAssignment.query.filter_by(scenario_id=scenario.id).count()
        result.append(scenario_dict)

    return jsonify(result)


@bp.route('/<program_id>/scenarios', methods=['POST'])
@require_auth
def create_scenario(program_id):
    """
    Create a new scenario for a program.

    Required fields:
    - name: Scenario name
    - channel: email, sms, qr, voice
    - technique: urgency, authority, fear, etc.
    - template_id: Template to use

    Optional fields:
    - description
    - difficulty_level: easy, medium, hard, expert
    - schedule_type: immediate, specific_datetime, relative
    - scheduled_datetime: For specific_datetime type
    - relative_days, relative_hours: For relative type
    """
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    # Only allow creating scenarios for draft/scheduled programs
    if program.status not in ['draft', 'scheduled']:
        return jsonify({'error': 'Cannot modify scenarios for active/completed programs'}), 400

    data = request.json

    # Validate required fields
    required_fields = ['name', 'channel', 'technique', 'template_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Validate template exists
    template = CustomTemplate.query.get(data['template_id'])
    if not template:
        return jsonify({'error': 'Template not found'}), 404

    # Validate channel
    valid_channels = ['email', 'sms', 'qr', 'voice']
    if data['channel'] not in valid_channels:
        return jsonify({'error': f'Invalid channel. Must be one of: {", ".join(valid_channels)}'}), 400

    # Validate technique
    valid_techniques = ['urgency', 'authority', 'fear', 'curiosity', 'reward', 'social_proof']
    if data['technique'] not in valid_techniques:
        return jsonify({'error': f'Invalid technique. Must be one of: {", ".join(valid_techniques)}'}), 400

    # Create scenario
    scenario = ProgramScenario(
        program_id=program_id,
        name=data['name'],
        description=data.get('description'),
        channel=data['channel'],
        technique=data['technique'],
        template_id=data['template_id'],
        difficulty_level=data.get('difficulty_level'),
        schedule_type=data.get('schedule_type', 'immediate')
    )

    # Handle scheduling
    if scenario.schedule_type == 'specific_datetime' and 'scheduled_datetime' in data:
        scenario.scheduled_datetime = datetime.fromisoformat(data['scheduled_datetime'])
    elif scenario.schedule_type == 'relative':
        scenario.relative_days = data.get('relative_days', 0)
        scenario.relative_hours = data.get('relative_hours', 0)

    db.session.add(scenario)
    db.session.commit()

    return jsonify(scenario.to_dict()), 201


@bp.route('/<program_id>/scenarios/<scenario_id>', methods=['GET'])
@require_auth
def get_scenario(program_id, scenario_id):
    """
    Get a specific scenario with its assignments.
    """
    scenario = ProgramScenario.query.filter_by(id=scenario_id, program_id=program_id).first()
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404

    scenario_dict = scenario.to_dict()

    # Include assignments
    assignments = ScenarioAssignment.query.filter_by(scenario_id=scenario_id).all()
    scenario_dict['assignments'] = [
        {
            **a.to_dict(),
            'employee_name': a.employee.name if a.employee else None,
            'employee_email': a.employee.email if a.employee else None
        }
        for a in assignments
    ]

    return jsonify(scenario_dict)


@bp.route('/<program_id>/scenarios/<scenario_id>', methods=['PUT'])
@require_auth
def update_scenario(program_id, scenario_id):
    """
    Update a scenario (only for draft/scheduled programs).
    """
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    if program.status not in ['draft', 'scheduled']:
        return jsonify({'error': 'Cannot modify scenarios for active/completed programs'}), 400

    scenario = ProgramScenario.query.filter_by(id=scenario_id, program_id=program_id).first()
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404

    data = request.json

    # Update fields
    if 'name' in data:
        scenario.name = data['name']
    if 'description' in data:
        scenario.description = data['description']
    if 'channel' in data:
        scenario.channel = data['channel']
    if 'technique' in data:
        scenario.technique = data['technique']
    if 'template_id' in data:
        template = CustomTemplate.query.get(data['template_id'])
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        scenario.template_id = data['template_id']
    if 'difficulty_level' in data:
        scenario.difficulty_level = data['difficulty_level']
    if 'schedule_type' in data:
        scenario.schedule_type = data['schedule_type']
    if 'scheduled_datetime' in data:
        scenario.scheduled_datetime = datetime.fromisoformat(data['scheduled_datetime']) if data['scheduled_datetime'] else None
    if 'relative_days' in data:
        scenario.relative_days = data['relative_days']
    if 'relative_hours' in data:
        scenario.relative_hours = data['relative_hours']

    db.session.commit()
    return jsonify(scenario.to_dict())


@bp.route('/<program_id>/scenarios/<scenario_id>', methods=['DELETE'])
@require_auth
def delete_scenario(program_id, scenario_id):
    """
    Delete a scenario and all its assignments (only for draft programs).
    """
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    if program.status != 'draft':
        return jsonify({'error': 'Can only delete scenarios from draft programs'}), 400

    scenario = ProgramScenario.query.filter_by(id=scenario_id, program_id=program_id).first()
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404

    db.session.delete(scenario)
    db.session.commit()

    return jsonify({'message': 'Scenario deleted successfully'})


# =============================================================================
# SCENARIO ASSIGNMENTS
# =============================================================================

@bp.route('/<program_id>/scenarios/<scenario_id>/assignments', methods=['POST'])
@require_auth
def create_assignments(program_id, scenario_id):
    """
    Create assignments for a scenario.

    Supports three assignment types:
    1. Specific employees: {"employee_ids": ["id1", "id2"]}
    2. Department: {"department": "Engineering"}
    3. Rule-based: {"assignment_rule": {"risk_level": "high"}}

    Optional: custom_scheduled_time for per-assignment scheduling
    """
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    if program.status not in ['draft', 'scheduled']:
        return jsonify({'error': 'Cannot modify assignments for active/completed programs'}), 400

    scenario = ProgramScenario.query.filter_by(id=scenario_id, program_id=program_id).first()
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404

    data = request.json
    created_assignments = []

    # Type 1: Specific employees
    if 'employee_ids' in data:
        for emp_id in data['employee_ids']:
            employee = Employee.query.get(emp_id)
            if not employee:
                continue

            # Check if assignment already exists
            existing = ScenarioAssignment.query.filter_by(
                scenario_id=scenario_id,
                employee_id=emp_id
            ).first()

            if existing:
                continue

            assignment = ScenarioAssignment(
                scenario_id=scenario_id,
                employee_id=emp_id,
                custom_scheduled_time=datetime.fromisoformat(data['custom_scheduled_time']) if 'custom_scheduled_time' in data else None
            )
            db.session.add(assignment)
            created_assignments.append(assignment)

    # Type 2: Department
    elif 'department' in data:
        # Check if department assignment already exists
        existing = ScenarioAssignment.query.filter_by(
            scenario_id=scenario_id,
            department=data['department']
        ).first()

        if not existing:
            assignment = ScenarioAssignment(
                scenario_id=scenario_id,
                department=data['department'],
                custom_scheduled_time=datetime.fromisoformat(data['custom_scheduled_time']) if 'custom_scheduled_time' in data else None
            )
            db.session.add(assignment)
            created_assignments.append(assignment)

    # Type 3: Rule-based
    elif 'assignment_rule' in data:
        import json
        assignment = ScenarioAssignment(
            scenario_id=scenario_id,
            assignment_rule=json.dumps(data['assignment_rule']),
            custom_scheduled_time=datetime.fromisoformat(data['custom_scheduled_time']) if 'custom_scheduled_time' in data else None
        )
        db.session.add(assignment)
        created_assignments.append(assignment)

    else:
        return jsonify({'error': 'Must specify employee_ids, department, or assignment_rule'}), 400

    # Update scenario assigned count
    scenario.total_assigned = ScenarioAssignment.query.filter_by(scenario_id=scenario_id).count() + len(created_assignments)

    db.session.commit()

    return jsonify({
        'message': f'Created {len(created_assignments)} assignment(s)',
        'assignments': [a.to_dict() for a in created_assignments]
    }), 201


@bp.route('/<program_id>/scenarios/<scenario_id>/assignments/<assignment_id>', methods=['DELETE'])
@require_auth
def delete_assignment(program_id, scenario_id, assignment_id):
    """
    Delete a specific assignment (only for draft/scheduled programs).
    """
    program = CampaignProgram.query.get(program_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404

    if program.status not in ['draft', 'scheduled']:
        return jsonify({'error': 'Cannot delete assignments for active/completed programs'}), 400

    assignment = ScenarioAssignment.query.filter_by(
        id=assignment_id,
        scenario_id=scenario_id
    ).first()

    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    db.session.delete(assignment)

    # Update scenario assigned count
    scenario = ProgramScenario.query.get(scenario_id)
    if scenario:
        scenario.total_assigned = ScenarioAssignment.query.filter_by(scenario_id=scenario_id).count() - 1

    db.session.commit()

    return jsonify({'message': 'Assignment deleted successfully'})


@bp.route('/<program_id>/scenarios/<scenario_id>/stats', methods=['GET'])
@require_auth
def get_scenario_stats(program_id, scenario_id):
    """
    Get detailed statistics for a scenario.
    """
    scenario = ProgramScenario.query.filter_by(id=scenario_id, program_id=program_id).first()
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404

    # Get all scheduled campaigns for this scenario
    campaigns = ScheduledCampaign.query.filter_by(scenario_id=scenario_id).all()

    stats = {
        'scenario': scenario.to_dict(),
        'total_assigned': scenario.total_assigned,
        'total_scheduled': len(campaigns),
        'total_sent': sum(1 for c in campaigns if c.status == 'sent'),
        'total_opened': sum(1 for c in campaigns if c.email_opened),
        'total_clicked': sum(1 for c in campaigns if c.link_clicked),
        'total_submitted': sum(1 for c in campaigns if c.credentials_submitted),
        'total_reported': sum(1 for c in campaigns if c.reported_as_phishing),
        'open_rate': round((sum(1 for c in campaigns if c.email_opened) / len(campaigns) * 100), 2) if campaigns else 0,
        'click_rate': round((sum(1 for c in campaigns if c.link_clicked) / len(campaigns) * 100), 2) if campaigns else 0,
        'submission_rate': round((sum(1 for c in campaigns if c.credentials_submitted) / len(campaigns) * 100), 2) if campaigns else 0,
        'report_rate': round((sum(1 for c in campaigns if c.reported_as_phishing) / len(campaigns) * 100), 2) if campaigns else 0
    }

    return jsonify(stats)


# =============================================================================
# SCHEDULED CAMPAIGNS
# =============================================================================

@bp.route('/<program_id>/campaigns', methods=['GET'])
@require_auth
def get_scheduled_campaigns(program_id):
    """
    Get actual campaigns (email, SMS, QR) created by a program.

    Query params:
    - status: Filter by status
    - page: Page number
    - per_page: Items per page
    """
    print(f"[DEBUG] get_scheduled_campaigns called for program_id: {program_id}")

    program = CampaignProgram.query.get(program_id)
    if not program:
        print(f"[DEBUG] Program not found: {program_id}")
        return jsonify({'error': 'Program not found'}), 404

    print(f"[DEBUG] Program found: {program.name}")

    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Gather all campaigns from this program
    all_campaigns = []

    # Email campaigns
    email_campaigns = Campaign.query.filter_by(program_id=program_id)
    if status:
        email_campaigns = email_campaigns.filter_by(status=status)

    for campaign in email_campaigns.all():
        campaign_dict = campaign.to_dict()
        campaign_dict['type'] = 'email'
        campaign_dict['targets_count'] = len(campaign.targets)

        # Calculate stats
        total = len(campaign.targets)
        opened = sum(1 for t in campaign.targets if t.opened_at)
        clicked = sum(1 for t in campaign.targets if t.clicked_at)

        # Get credential submissions from CredentialCapture table
        from models import CredentialCapture
        submitted_target_ids = set(
            c.target_id for c in CredentialCapture.query.filter_by(campaign_id=campaign.id).all()
        )
        submitted = len(submitted_target_ids)

        campaign_dict['stats'] = {
            'total': total,
            'opened': opened,
            'clicked': clicked,
            'submitted': submitted,
            'open_rate': round((opened / total * 100) if total > 0 else 0, 1),
            'click_rate': round((clicked / total * 100) if total > 0 else 0, 1),
            'submit_rate': round((submitted / total * 100) if total > 0 else 0, 1)
        }

        # Include targets data with details
        campaign_dict['targets'] = [
            {
                'id': t.id,
                'name': t.name if hasattr(t, 'name') else None,
                'email': t.email,
                'department': t.department if hasattr(t, 'department') else None,
                'opened_at': t.opened_at.isoformat() if t.opened_at else None,
                'clicked_at': t.clicked_at.isoformat() if t.clicked_at else None,
                'submitted_at': (
                    CredentialCapture.query.filter_by(target_id=t.id).first().submitted_at.isoformat()
                    if CredentialCapture.query.filter_by(target_id=t.id).first()
                    else None
                ),
                'device_type': t.user_agent if hasattr(t, 'user_agent') else None,
                'ip_address': t.ip_address
            }
            for t in campaign.targets
        ]

        all_campaigns.append(campaign_dict)

    # SMS campaigns
    sms_campaigns = SMSCampaign.query.filter_by(program_id=program_id)
    if status:
        sms_campaigns = sms_campaigns.filter_by(status=status)

    for campaign in sms_campaigns.all():
        campaign_dict = campaign.to_dict()
        campaign_dict['type'] = 'sms'
        campaign_dict['targets_count'] = len(campaign.targets)

        # Calculate stats
        total = len(campaign.targets)
        clicked = sum(1 for t in campaign.targets if t.clicked_at)

        # For SMS, check if there are credential submissions (via landing pages)
        from models import CredentialCapture
        # Find credential submissions that match the SMS targets by email
        submitted_emails = set(t.email for t in campaign.targets if t.email)
        submitted = 0
        if submitted_emails:
            submitted = CredentialCapture.query.filter(
                CredentialCapture.email.in_(submitted_emails)
            ).count()

        campaign_dict['stats'] = {
            'total': total,
            'clicked': clicked,
            'submitted': submitted,
            'click_rate': round((clicked / total * 100) if total > 0 else 0, 1),
            'submit_rate': round((submitted / total * 100) if total > 0 else 0, 1)
        }

        # Include targets data with details
        campaign_dict['targets'] = [
            {
                'id': t.id,
                'name': t.name if hasattr(t, 'name') else None,
                'phone_number': t.phone_number,
                'department': t.department if hasattr(t, 'department') else None,
                'clicked_at': t.clicked_at.isoformat() if t.clicked_at else None,
                'submitted_at': None,  # SMS targets don't directly track submissions
                'device_type': str(t.metadata) if hasattr(t, 'metadata') and t.metadata else None,
                'ip_address': t.ip_address
            }
            for t in campaign.targets
        ]

        all_campaigns.append(campaign_dict)

    # QR campaigns
    qr_campaigns = QRCodeCampaign.query.filter_by(program_id=program_id)
    if status:
        qr_campaigns = qr_campaigns.filter_by(status=status)

    print(f"[DEBUG] Found {qr_campaigns.count()} QR campaigns for program {program_id}")

    for campaign in qr_campaigns.all():
        print(f"[DEBUG] Processing QR campaign: {campaign.name} (ID: {campaign.id})")

        campaign_dict = campaign.to_dict()
        campaign_dict['type'] = 'qr'
        campaign_dict['targets_count'] = len(campaign.targets)

        # Calculate stats from targets
        total = len(campaign.targets)
        scanned = sum(1 for t in campaign.targets if t.scanned_at)

        # Get credential submissions for this QR campaign
        from models import CredentialCapture
        submitted_count = 0
        if campaign.landing_page_id:
            submitted_count = CredentialCapture.query.filter_by(
                campaign_id=campaign.id
            ).count()

        campaign_dict['stats'] = {
            'total': total,
            'total_scans': scanned,
            'submitted': submitted_count,
            'scan_rate': round((scanned / total * 100) if total > 0 else 0, 1),
            'submit_rate': round((submitted_count / total * 100) if total > 0 else 0, 1)
        }

        # Include targets data with details (like Email/SMS campaigns)
        targets_with_details = []
        for target in campaign.targets:
            # Check if this target submitted credentials
            submitted_cred = None
            if campaign.landing_page_id and target.scanned_at:
                submitted_cred = CredentialCapture.query.filter(
                    CredentialCapture.campaign_id == campaign.id,
                    CredentialCapture.submitted_at >= target.scanned_at
                ).order_by(CredentialCapture.submitted_at.asc()).first()

            target_data = {
                'id': target.id,
                'name': target.name,
                'email': target.email,
                'department': target.department,
                'sent_at': target.sent_at.isoformat() if target.sent_at else None,
                'scanned_at': target.scanned_at.isoformat() if target.scanned_at else None,
                'submitted_at': submitted_cred.submitted_at.isoformat() if submitted_cred else None,
                'device_type': target.user_agent if target.user_agent else None,
                'ip_address': target.ip_address
            }
            targets_with_details.append(target_data)

        campaign_dict['targets'] = targets_with_details
        campaign_dict['scans'] = targets_with_details  # For backwards compatibility

        print(f"[DEBUG] QR campaign dict keys: {campaign_dict.keys()}")
        print(f"[DEBUG] QR campaign has {len(targets_with_details)} targets")

        all_campaigns.append(campaign_dict)

    # Sort by created_at descending
    all_campaigns.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    print(f"[DEBUG] Total campaigns found: {len(all_campaigns)}")
    for camp in all_campaigns:
        print(f"[DEBUG]   - {camp.get('type')}: {camp.get('name')} (targets: {camp.get('targets_count', 0)})")

    # Manual pagination
    total = len(all_campaigns)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_campaigns = all_campaigns[start:end]

    print(f"[DEBUG] Returning {len(paginated_campaigns)} campaigns after pagination")

    # Print summary of what we're returning
    print("[DEBUG] FINAL RESPONSE SUMMARY:")
    for camp in paginated_campaigns:
        print(f"[DEBUG]   - Type: {camp.get('type')}, Name: {camp.get('name')}, ID: {camp.get('id')}")
        if camp.get('type') == 'email':
            print(f"[DEBUG]     Email stats: {camp.get('stats')}")
        elif camp.get('type') == 'sms':
            print(f"[DEBUG]     SMS stats: {camp.get('stats')}")
        elif camp.get('type') == 'qr':
            print(f"[DEBUG]     QR stats: {camp.get('stats')}, Scans count: {len(camp.get('scans', []))}")

    # Debug: Check if any campaign has problematic objects
    import json
    try:
        test_json = json.dumps(paginated_campaigns)
        print("[DEBUG] Campaigns JSON serialization test passed")
    except TypeError as e:
        print(f"[DEBUG] JSON serialization test FAILED: {e}")
        # Find which campaign has the issue
        for i, camp in enumerate(paginated_campaigns):
            try:
                json.dumps(camp)
            except TypeError as e2:
                print(f"[DEBUG] Campaign {i} ({camp.get('name')}) failed: {e2}")
                # Find which key has the issue
                for key, value in camp.items():
                    try:
                        json.dumps({key: value})
                    except TypeError as e3:
                        print(f"[DEBUG]   Key '{key}' has non-serializable value: {type(value)}")

    return jsonify({
        'campaigns': paginated_campaigns,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })


@bp.route('/campaigns/<campaign_id>/cancel', methods=['POST'])
@require_auth
def cancel_scheduled_campaign(campaign_id):
    """Cancel a scheduled campaign"""
    scheduled = ScheduledCampaign.query.get(campaign_id)
    if not scheduled:
        return jsonify({'error': 'Scheduled campaign not found'}), 404

    if scheduled.status != 'scheduled':
        return jsonify({'error': 'Can only cancel scheduled campaigns'}), 400

    scheduled.status = 'cancelled'
    db.session.commit()

    return jsonify({'success': True, 'status': 'cancelled'})


# =============================================================================
# PROCESSING
# =============================================================================

@bp.route('/process-due', methods=['POST'])
@require_auth
def process_due_campaigns():
    """
    Process all campaigns that are due to be sent.
    This should typically be called by a scheduler/cron job.
    """
    user = get_current_user()
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    batch_size = request.args.get('batch_size', 50, type=int)
    results = program_service.process_due_campaigns(batch_size=batch_size)

    return jsonify(results)


# =============================================================================
# EMPLOYEE HISTORY
# =============================================================================

@bp.route('/employee/<employee_id>/history', methods=['GET'])
@require_auth
def get_employee_program_history(employee_id):
    """Get an employee's campaign history across all programs"""
    program_id = request.args.get('program_id')

    history = program_service.get_employee_program_history(
        employee_id=employee_id,
        program_id=program_id
    )

    employee = Employee.query.get(employee_id)

    return jsonify({
        'employee': employee.to_dict() if employee else None,
        'history': history,
        'total': len(history)
    })


# ========================================
#  PROGRAM AWARENESS REPORT ENDPOINTS
# ========================================

@bp.route('/<program_id>/report', methods=['GET'])
def get_program_report(program_id):
    """
    Generate and return awareness report for a profiling program

    Returns comprehensive analysis including:
    - Program overview
    - Company-level awareness summary across all campaigns
    - Campaign breakdown (email, SMS, QR)
    - Individual employee results across all vectors
    - Department risk breakdown
    - Identified security gaps and training recommendations
    """
    try:
        from services.program_report_service import ProgramReportService

        # Verify program exists
        program = CampaignProgram.query.get(program_id)
        if not program:
            return jsonify({'error': 'Program not found'}), 404

        # Generate report
        report = ProgramReportService.generate_report(program_id)

        if 'error' in report:
            return jsonify(report), 400

        return jsonify(report), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/<program_id>/report/export', methods=['GET'])
def export_program_report(program_id):
    """
    Export program report in various formats (JSON, PDF)
    """
    try:
        from services.program_report_service import ProgramReportService
        from flask import send_file
        import io

        program = CampaignProgram.query.get(program_id)
        if not program:
            return jsonify({'error': 'Program not found'}), 404

        # Get export format (default: json)
        export_format = request.args.get('format', 'json').lower()

        # Generate report
        report = ProgramReportService.generate_report(program_id)

        if 'error' in report:
            return jsonify(report), 400

        if export_format == 'json':
            return jsonify(report), 200

        elif export_format == 'pdf':
            # Generate professional PDF report
            try:
                from xhtml2pdf import pisa

                overview = report['overview']
                summary = report['awareness_summary']
                campaign_breakdown = report['campaign_breakdown']
                gaps = report['security_gaps']
                departments = report['department_breakdown'][:10]
                employees = report['employee_results'][:50]  # Top 50 employees

                # Combine all campaigns for the table
                all_campaigns = []
                all_campaigns.extend(campaign_breakdown.get('email_campaigns', []))
                all_campaigns.extend(campaign_breakdown.get('sms_campaigns', []))
                all_campaigns.extend(campaign_breakdown.get('qr_campaigns', []))

                # Helper function for risk badge styling
                def get_risk_badge(level):
                    colors = {
                        'critical': '#dc2626',
                        'high': '#f97316',
                        'medium': '#f59e0b',
                        'low': '#10b981'
                    }
                    color = colors.get(level.lower(), '#6b7280')
                    return f'<span style="background:{color};color:white;padding:2px 8px;font-size:9pt;font-weight:bold;border-radius:3px;">{level.upper()}</span>'

                # Build HTML content
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Profiling Program Awareness Report</title>
    <style>
        @page {{ size: A4; margin: 25mm; }}
        body {{ font-family: 'Helvetica', 'Arial', sans-serif; font-size: 11pt; line-height: 1.4; color: #1f2937; }}

        /* Header */
        .report-header {{ text-align: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #2563eb; }}
        .report-title {{ font-size: 24pt; font-weight: bold; color: #1e40af; margin: 8px 0; }}
        .program-name {{ font-size: 14pt; color: #4b5563; margin: 5px 0; font-style: italic; }}
        .report-date {{ font-size: 9pt; color: #6b7280; margin-top: 5px; }}

        /* Sections */
        h2 {{ font-size: 14pt; font-weight: bold; color: #1f2937; margin: 25px 0 10px 0; padding-bottom: 4px; border-bottom: 2px solid #e5e7eb; }}
        h2:first-of-type {{ margin-top: 15px; }}
        h3 {{ font-size: 12pt; font-weight: bold; color: #374151; margin: 15px 0 8px 0; }}
        p {{ margin: 5px 0; }}

        /* Score Display */
        .score-box {{ text-align: center; background: #eff6ff; border: 2px solid #2563eb; padding: 12px; margin: 10px 0; }}
        .score-number {{ font-size: 36pt; font-weight: bold; color: #1e40af; }}
        .score-label {{ font-size: 11pt; color: #6b7280; margin-top: 3px; }}

        /* Behavior List */
        .behavior-list {{ margin: 8px 0; }}
        .behavior-item {{ padding: 4px 0; border-bottom: 1px solid #e5e7eb; }}
        .behavior-label {{ display: inline-block; width: 180px; font-weight: bold; color: #374151; }}

        /* Tables */
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background: #1e40af; color: white; font-weight: bold; text-align: left; padding: 8px; font-size: 10pt; }}
        td {{ padding: 6px 8px; border-bottom: 1px solid #e5e7eb; font-size: 9pt; }}
        tr:nth-child(even) {{ background: #f9fafb; }}

        /* Security Gaps */
        .gap-item {{ margin: 8px 0; padding: 8px; border-left: 4px solid #f59e0b; background: #fef3c7; }}
        .gap-title {{ font-weight: bold; color: #92400e; margin-bottom: 3px; }}
        .gap-desc {{ font-size: 9pt; color: #78350f; }}

        /* Page Break */
        .page-break {{ page-break-before: always; }}

        /* Footer */
        .footer {{ margin-top: 20px; padding-top: 10px; border-top: 2px solid #e5e7eb; text-align: center; font-size: 8pt; color: #6b7280; }}
    </style>
</head>
<body>
    <!-- Header -->
    <div class="report-header">
        <div style="font-size:11pt;font-weight:bold;color:#2563eb;">PhishVision Security Awareness Platform</div>
        <div class="report-title">Profiling Program Awareness Report</div>
        <div class="program-name">{overview['program_name']}</div>
        <div class="report-date">Generated on {datetime.fromisoformat(report['generated_at']).strftime('%B %d, %Y at %I:%M %p')}</div>
    </div>

    <!-- Program Overview -->
    <h2>Program Overview</h2>
    <p><strong>Description:</strong> {overview['program_description']}</p>
    <p><strong>Status:</strong> {overview['status']}</p>
    <p><strong>Total Campaigns:</strong> {overview['total_campaigns']} ({overview['email_campaigns']} Email, {overview['sms_campaigns']} SMS, {overview['qr_campaigns']} QR Code)</p>
    <p><strong>Total Targets:</strong> {overview['total_targets']} interactions</p>

    <!-- Company Awareness Score -->
    <h2>Company-Level Awareness Summary</h2>
    <div class="score-box">
        <div class="score-number">{summary['awareness_score']}/100</div>
        <div class="score-label">Awareness Level: <strong>{summary['awareness_level']}</strong></div>
    </div>

    <h3>Employee Behavior Breakdown</h3>
    <div class="behavior-list">
        <div class="behavior-item">
            <span class="behavior-label">No Interaction:</span>
            <span>{summary['no_interaction_count']} ({summary['no_interaction_percent']}%)</span>
        </div>
        <div class="behavior-item">
            <span class="behavior-label">Clicked/Interacted:</span>
            <span>{summary['clicked_count']} ({summary['clicked_percent']}%)</span>
        </div>
        <div class="behavior-item">
            <span class="behavior-label">Submitted Credentials:</span>
            <span>{summary['submitted_credentials_count']} ({summary['submitted_percent']}%)</span>
        </div>
    </div>

    <!-- Campaign Breakdown -->
    <h2>Campaign Breakdown</h2>
    <table>
        <thead>
            <tr>
                <th>Campaign Name</th>
                <th>Type</th>
                <th>Targets</th>
                <th>Click Rate</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f'''
            <tr>
                <td>{camp.get('campaign_name') or camp.get('name', 'Unknown')}</td>
                <td>{camp.get('type', 'Unknown')}</td>
                <td>{camp.get('total_targets', 0)}</td>
                <td>{camp.get('clicked_rate') or camp.get('click_rate', 0)}%</td>
                <td>{camp.get('status', 'N/A')}</td>
            </tr>
            ''' for camp in all_campaigns])}
        </tbody>
    </table>

    <!-- Department Risk Breakdown -->
    <h2>Department Risk Breakdown</h2>
    <table>
        <thead>
            <tr>
                <th>Department</th>
                <th>Employees</th>
                <th>Click Rate</th>
                <th>Risk Level</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f'''
            <tr>
                <td>{dept['department']}</td>
                <td>{dept['total_employees']}</td>
                <td>{dept['click_rate']}%</td>
                <td>{get_risk_badge(dept['risk_level'])}</td>
            </tr>
            ''' for dept in departments])}
        </tbody>
    </table>

    <!-- Individual Employee Results -->
    <div class="page-break"></div>
    <h2>Individual Employee Results (Top 50)</h2>
    <table>
        <thead>
            <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Outcome</th>
                <th>Risk Level</th>
                <th>Training</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f'''
            <tr>
                <td>{emp['name']}</td>
                <td>{emp['department']}</td>
                <td>{emp['outcome_label']}</td>
                <td>{get_risk_badge(emp['risk_level'])}</td>
                <td>{'<strong>Yes</strong>' if emp.get('training_recommended', False) else 'No'}</td>
            </tr>
            ''' for emp in employees])}
        </tbody>
    </table>

    <!-- Identified Security Gaps -->
    <h2>Identified Security Gaps & Recommendations</h2>
    <p><strong>Overall Risk Level:</strong> {get_risk_badge(gaps['overall_risk_level'])}</p>
    <p>{gaps.get('summary', 'Security gap analysis completed.')}</p>

    <h3>Detailed Findings</h3>
    {''.join([f'''
    <div class="gap-item">
        <div class="gap-title">{gap['category']}: {gap['finding']}</div>
        <div class="gap-desc"><strong>Recommendation:</strong> {gap['recommendation']}</div>
    </div>
    ''' for gap in gaps.get('gaps', [])])}

    <!-- Footer -->
    <div class="footer">
        Generated by PhishVision Security Awareness Platform<br>
        Confidential - For Internal Use Only
    </div>
</body>
</html>
"""

                # Generate PDF from HTML
                pdf_file = io.BytesIO()
                pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

                if pisa_status.err:
                    return jsonify({'error': 'Error generating PDF'}), 500

                pdf_file.seek(0)

                # Generate filename
                program_name_clean = "".join(c for c in program.name if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"Program_Report_{program_name_clean}_{datetime.now().strftime('%Y%m%d')}.pdf"

                # Return PDF file
                return send_file(
                    pdf_file,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=filename
                )

            except ImportError:
                return jsonify({'error': 'xhtml2pdf library not installed. Run: pip install xhtml2pdf'}), 500
            except Exception as pdf_error:
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'Error generating PDF document: {str(pdf_error)}'}), 500

        else:
            return jsonify({'error': f'Export format "{export_format}" not supported. Use: json, pdf'}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
