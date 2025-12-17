from flask import Blueprint, request, jsonify
from database import db
from models import TrainingCompletion, CampaignTarget, SMSTarget, QRCodeTarget
from datetime import datetime

bp = Blueprint('training', __name__, url_prefix='/api/training')


@bp.route('/complete', methods=['POST'])
def complete_training():
    """Record training completion when employee clicks 'Mark Training as Completed'"""
    try:
        data = request.json

        employee_id = data.get('employeeId')
        program_id = data.get('programId')
        campaign_id = data.get('campaignId')
        module = data.get('module', 'unknown')

        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400

        # Try to find employee details from the target ID
        employee_email = None
        employee_name = None
        campaign_type = None

        # Check if it's an email campaign target
        email_target = CampaignTarget.query.get(employee_id)
        if email_target:
            employee_email = email_target.email
            employee_name = email_target.name
            campaign_type = 'email'

        # Check if it's an SMS campaign target
        if not employee_email:
            sms_target = SMSTarget.query.get(employee_id)
            if sms_target:
                employee_email = sms_target.email if hasattr(sms_target, 'email') and sms_target.email else None
                employee_name = sms_target.name
                campaign_type = 'sms'

        # Check if it's a QR campaign target
        if not employee_email:
            qr_target = QRCodeTarget.query.get(employee_id)
            if qr_target:
                employee_email = qr_target.email
                employee_name = qr_target.name
                campaign_type = 'qr'

        # Create training completion record
        completion = TrainingCompletion(
            employee_id=employee_id,
            employee_email=employee_email,
            employee_name=employee_name,
            program_id=program_id if program_id else None,
            campaign_id=campaign_id if campaign_id else None,
            campaign_type=campaign_type,
            module=module,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            completed_at=datetime.utcnow()
        )

        db.session.add(completion)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Training completion recorded',
            'completion': completion.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/completions/<program_id>', methods=['GET'])
def get_program_completions(program_id):
    """Get all training completions for a specific program"""
    completions = TrainingCompletion.query.filter_by(program_id=program_id).all()

    return jsonify({
        'completions': [c.to_dict() for c in completions],
        'total': len(completions)
    })


@bp.route('/completions/employee/<employee_email>', methods=['GET'])
def get_employee_completions(employee_email):
    """Get all training completions for a specific employee"""
    completions = TrainingCompletion.query.filter_by(employee_email=employee_email).all()

    return jsonify({
        'completions': [c.to_dict() for c in completions],
        'total': len(completions)
    })
