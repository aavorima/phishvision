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
        # Get the template QR poster that user selected
        template_qr_id = qr_config.get('qr_campaign_id')
        if not template_qr_id:
            return {'error': 'No QR poster selected', 'vector': 'qr'}

        template_qr = QRCodeCampaign.query.get(template_qr_id)
        if not template_qr:
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
            return {'error': 'QR code image not found for this campaign', 'vector': 'qr'}

        # Get QR code image path
        import os as os_module
        QR_CODE_DIR = os_module.path.join(os_module.path.dirname(os_module.path.dirname(__file__)), 'static', 'qrcodes')
        qr_path = os_module.path.join(QR_CODE_DIR, campaign.qr_image_path)

        if not os_module.path.exists(qr_path):
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

        # Send poster to each recipient with inline image attachment
        for recipient in target_employees:
            email = recipient.get('email')
            if not email:
                continue

            # Generate poster HTML with CID reference
            qr_cid = f"qrcode_{campaign.id}"
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

            # Use campaign description as subject if available, otherwise use campaign name
            subject = campaign.description if campaign.description else campaign.name
            success = email_service.send_email_with_inline_image(email, subject, email_html, qr_path, qr_cid)
            if success:
                emails_sent += 1
                # Update target's sent_at timestamp
                target = QRCodeTarget.query.filter_by(campaign_id=campaign.id, email=email).first()
                if target:
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

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': f'Failed to launch QR campaign: {str(e)}', 'vector': 'qr'}
