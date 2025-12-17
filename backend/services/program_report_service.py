"""
Profiling Program Awareness Report Service
Generates comprehensive security awareness reports for completed profiling programs
"""

from database import db
from models import CampaignProgram, Campaign, CampaignTarget, SMSCampaign, SMSTarget, QRCodeCampaign, CredentialCapture, Employee
from sqlalchemy import func
from datetime import datetime


class ProgramReportService:
    """Service for generating profiling program awareness reports"""

    @staticmethod
    def generate_report(program_id):
        """
        Generate a comprehensive awareness report for a profiling program

        Returns:
            dict: Complete program awareness report including all campaigns
        """
        program = CampaignProgram.query.get(program_id)
        if not program:
            raise ValueError(f"Program {program_id} not found")

        # Get all campaigns in this program
        email_campaigns = Campaign.query.filter_by(program_id=program_id).all()
        sms_campaigns = SMSCampaign.query.filter_by(program_id=program_id).all()
        qr_campaigns = QRCodeCampaign.query.filter_by(program_id=program_id).all()

        print(f"[REPORT DEBUG] Program ID: {program_id}")
        print(f"[REPORT DEBUG] Email campaigns found: {len(email_campaigns)}")
        print(f"[REPORT DEBUG] SMS campaigns found: {len(sms_campaigns)}")
        print(f"[REPORT DEBUG] QR campaigns found: {len(qr_campaigns)}")

        # Also check ALL QR campaigns in database
        all_qr = QRCodeCampaign.query.all()
        print(f"[REPORT DEBUG] Total QR campaigns in database: {len(all_qr)}")
        for qr in all_qr:
            print(f"[REPORT DEBUG]   - QR Campaign: {qr.name} (ID: {qr.id}, Program ID: {qr.program_id})")

        total_campaigns = len(email_campaigns) + len(sms_campaigns) + len(qr_campaigns)

        if total_campaigns == 0:
            return {
                'error': 'No campaigns found for this program',
                'program_id': program_id
            }

        # 1. Program Overview
        overview = ProgramReportService._generate_overview(program, email_campaigns, sms_campaigns, qr_campaigns)

        # 2. Company-Level Awareness Summary
        awareness_summary = ProgramReportService._generate_awareness_summary(
            email_campaigns, sms_campaigns, qr_campaigns
        )

        # 3. Campaign Breakdown
        campaign_breakdown = ProgramReportService._generate_campaign_breakdown(
            email_campaigns, sms_campaigns, qr_campaigns
        )

        # 4. Employee Results (across all campaigns)
        employee_results = ProgramReportService._generate_employee_results(
            email_campaigns, sms_campaigns, qr_campaigns, program_id
        )

        # 5. Department Risk Breakdown
        department_breakdown = ProgramReportService._generate_department_breakdown(
            email_campaigns, sms_campaigns, qr_campaigns
        )

        # 6. Identified Security Gaps
        security_gaps = ProgramReportService._generate_security_gaps(
            email_campaigns, sms_campaigns, qr_campaigns, employee_results, department_breakdown
        )

        return {
            'program_id': program_id,
            'generated_at': datetime.utcnow().isoformat(),
            'overview': overview,
            'awareness_summary': awareness_summary,
            'campaign_breakdown': campaign_breakdown,
            'employee_results': employee_results,
            'department_breakdown': department_breakdown,
            'security_gaps': security_gaps
        }

    @staticmethod
    def _generate_overview(program, email_campaigns, sms_campaigns, qr_campaigns):
        """Generate program overview section"""
        # Count how many vectors were used (1-3)
        vectors_used = 0
        if len(email_campaigns) > 0:
            vectors_used += 1
        if len(sms_campaigns) > 0:
            vectors_used += 1
        if len(qr_campaigns) > 0:
            vectors_used += 1

        # Count unique employees across all campaigns
        email_targets = []
        for camp in email_campaigns:
            email_targets.extend(camp.targets)

        sms_targets = []
        for camp in sms_campaigns:
            sms_targets.extend(camp.targets)

        qr_targets = []
        for camp in qr_campaigns:
            qr_targets.extend(camp.targets)

        # Count unique employees (use email as primary key, phone as fallback)
        unique_identifiers = set()
        for target in email_targets:
            if target.email:
                unique_identifiers.add(target.email.lower())
        for target in sms_targets:
            # Try to use email first, fallback to phone
            if hasattr(target, 'email') and target.email:
                unique_identifiers.add(target.email.lower())
            elif target.phone_number:
                unique_identifiers.add(f"phone:{target.phone_number}")  # Prefix to avoid collision
        for target in qr_targets:
            if target.email:
                unique_identifiers.add(target.email.lower())

        total_employees = len(unique_identifiers)
        total_targets = len(email_targets) + len(sms_targets) + len(qr_targets)

        # Get program duration
        duration = None
        if program.created_at:
            latest_time = program.created_at
            all_times = []

            for t in email_targets:
                if t.sent_at:
                    all_times.append(t.sent_at)
                if t.clicked_at:
                    all_times.append(t.clicked_at)

            for t in sms_targets:
                if t.sent_at:
                    all_times.append(t.sent_at)
                if t.clicked_at:
                    all_times.append(t.clicked_at)

            if all_times:
                latest_time = max(all_times)
                duration_delta = latest_time - program.created_at
                duration = {
                    'days': duration_delta.days,
                    'hours': duration_delta.seconds // 3600,
                    'minutes': (duration_delta.seconds % 3600) // 60
                }

        return {
            'program_name': program.name,
            'program_description': program.description or 'Multi-vector security awareness testing program',
            'status': program.status,
            'created_at': program.created_at.isoformat() if program.created_at else None,
            'total_campaigns': vectors_used,  # Number of vectors used (1-3)
            'email_campaigns': len(email_campaigns),
            'sms_campaigns': len(sms_campaigns),
            'qr_campaigns': len(qr_campaigns),
            'total_employees': total_employees,  # Unique employees who received campaigns
            'total_targets': total_targets,
            'duration': duration
        }

    @staticmethod
    def _generate_awareness_summary(email_campaigns, sms_campaigns, qr_campaigns):
        """Generate company-level awareness summary"""
        # Track unique employees and their interactions
        employee_interactions = {}  # email -> {'interacted': bool, 'submitted': bool}

        # Process email targets
        for camp in email_campaigns:
            for target in camp.targets:
                email = target.email.lower() if target.email else None
                if not email:
                    continue

                if email not in employee_interactions:
                    employee_interactions[email] = {'interacted': False, 'submitted': False}

                # Check if they clicked
                if target.clicked_at:
                    employee_interactions[email]['interacted'] = True
                    # Check if credentials were submitted
                    cred_capture = CredentialCapture.query.filter_by(target_id=target.id).first()
                    if cred_capture:
                        employee_interactions[email]['submitted'] = True

        # Process SMS targets
        for camp in sms_campaigns:
            for target in camp.targets:
                # Use email if available, otherwise use phone with prefix
                if hasattr(target, 'email') and target.email:
                    key = target.email.lower()
                elif target.phone_number:
                    key = f"phone:{target.phone_number}"
                else:
                    continue

                if key not in employee_interactions:
                    employee_interactions[key] = {'interacted': False, 'submitted': False}

                # Check if they clicked
                if target.clicked_at:
                    employee_interactions[key]['interacted'] = True

        # Process QR targets
        for camp in qr_campaigns:
            for target in camp.targets:
                email = target.email.lower() if target.email else None
                if not email:
                    continue

                if email not in employee_interactions:
                    employee_interactions[email] = {'interacted': False, 'submitted': False}

                # Check if they scanned the QR code
                if target.scanned_at:
                    employee_interactions[email]['interacted'] = True

        total_employees = len(employee_interactions)

        # Count interactions
        no_interaction = 0
        clicked = 0
        submitted_credentials = 0

        for emp_id, interactions in employee_interactions.items():
            if interactions['interacted']:
                clicked += 1
            else:
                no_interaction += 1

            if interactions['submitted']:
                submitted_credentials += 1

        # Calculate awareness score (inverse of failure rate)
        # Lower failure = higher awareness
        failure_rate = (clicked / total_employees * 100) if total_employees > 0 else 0
        awareness_score = max(0, min(100, 100 - failure_rate))

        # Determine awareness level
        if awareness_score >= 80:
            awareness_level = 'Excellent'
            level_color = '#10b981'
        elif awareness_score >= 60:
            awareness_level = 'Good'
            level_color = '#3b82f6'
        elif awareness_score >= 40:
            awareness_level = 'Fair'
            level_color = '#f59e0b'
        elif awareness_score >= 20:
            awareness_level = 'Poor'
            level_color = '#f97316'
        else:
            awareness_level = 'Critical'
            level_color = '#dc2626'

        return {
            'total_employees': total_employees,
            'awareness_score': round(awareness_score, 1),
            'awareness_level': awareness_level,
            'level_color': level_color,
            'no_interaction_count': no_interaction,
            'no_interaction_percent': round(no_interaction / total_employees * 100, 1) if total_employees > 0 else 0,
            'clicked_count': clicked,
            'clicked_percent': round(clicked / total_employees * 100, 1) if total_employees > 0 else 0,
            'submitted_credentials_count': submitted_credentials,
            'submitted_percent': round(submitted_credentials / total_employees * 100, 1) if total_employees > 0 else 0
        }

    @staticmethod
    def _generate_campaign_breakdown(email_campaigns, sms_campaigns, qr_campaigns):
        """Generate breakdown of each campaign in the program"""
        email_campaigns_data = []
        sms_campaigns_data = []
        qr_campaigns_data = []

        # Email campaigns
        for camp in email_campaigns:
            targets = camp.targets
            total = len(targets)
            opened = sum(1 for t in targets if t.opened_at)
            clicked = sum(1 for t in targets if t.clicked_at)
            submitted = sum(1 for t in targets if CredentialCapture.query.filter_by(target_id=t.id).first())

            email_campaigns_data.append({
                'campaign_id': camp.id,
                'campaign_name': camp.name,
                'name': camp.name,  # For backwards compatibility
                'type': 'Email',
                'status': camp.status,
                'total_targets': total,
                'opened': opened,
                'opened_count': opened,  # For backwards compatibility
                'opened_rate': round(opened / total * 100, 1) if total > 0 else 0,
                'clicked': clicked,
                'clicked_count': clicked,  # For backwards compatibility
                'clicked_rate': round(clicked / total * 100, 1) if total > 0 else 0,
                'click_rate': round(clicked / total * 100, 1) if total > 0 else 0,  # For backwards compatibility
                'submitted': submitted,
                'submitted_rate': round(submitted / total * 100, 1) if total > 0 else 0
            })

        # SMS campaigns
        for camp in sms_campaigns:
            targets = camp.targets
            total = len(targets)
            clicked = sum(1 for t in targets if t.clicked_at)

            sms_campaigns_data.append({
                'campaign_id': camp.id,
                'campaign_name': camp.name,
                'name': camp.name,  # For backwards compatibility
                'type': 'SMS',
                'status': camp.status,
                'total_targets': total,
                'opened': 0,  # SMS doesn't track opens
                'opened_rate': 0,
                'clicked': clicked,
                'clicked_count': clicked,  # For backwards compatibility
                'clicked_rate': round(clicked / total * 100, 1) if total > 0 else 0,
                'click_rate': round(clicked / total * 100, 1) if total > 0 else 0,  # For backwards compatibility
                'submitted': 0,
                'submitted_rate': 0
            })

        # QR campaigns
        for camp in qr_campaigns:
            targets = camp.targets  # Now we track targets!
            total = len(targets)

            # Count scanned (clicked)
            scanned = sum(1 for t in targets if t.scanned_at)

            qr_campaigns_data.append({
                'campaign_id': camp.id,
                'campaign_name': camp.name,
                'name': camp.name,  # For backwards compatibility
                'type': 'QR Code',
                'status': camp.status,
                'total_targets': total,
                'total_scans': scanned,
                'opened': 0,
                'opened_rate': 0,
                'clicked': scanned,  # Scanned = clicked
                'clicked_rate': round(scanned / total * 100, 1) if total > 0 else 0,
                'submitted': 0,
                'submitted_rate': 0
            })

        return {
            'email_campaigns': email_campaigns_data,
            'sms_campaigns': sms_campaigns_data,
            'qr_campaigns': qr_campaigns_data
        }

    @staticmethod
    def _generate_employee_results(email_campaigns, sms_campaigns, qr_campaigns, program_id):
        """Generate individual employee results across all campaigns"""
        employee_data = {}

        # Process email campaigns
        for camp in email_campaigns:
            for target in camp.targets:
                email = target.email
                if email not in employee_data:
                    employee_data[email] = {
                        'name': target.name or email.split('@')[0],
                        'email': email,
                        'department': target.department or 'Unknown',
                        'campaigns_sent': 0,
                        'campaigns_opened': 0,
                        'campaigns_clicked': 0,
                        'campaigns_submitted': 0,
                        'vectors_tested': set(),
                        'vectors_failed': set(),
                        'target_ids': []  # Track target IDs for training completion lookup
                    }

                # Add target ID to track training completion
                employee_data[email]['target_ids'].append(target.id)
                employee_data[email]['campaigns_sent'] += 1
                employee_data[email]['vectors_tested'].add('Email')

                if target.opened_at:
                    employee_data[email]['campaigns_opened'] += 1
                if target.clicked_at:
                    employee_data[email]['campaigns_clicked'] += 1
                    employee_data[email]['vectors_failed'].add('Email')

                cred_capture = CredentialCapture.query.filter_by(target_id=target.id).first()
                if cred_capture:
                    employee_data[email]['campaigns_submitted'] += 1

        # Process SMS campaigns
        for camp in sms_campaigns:
            for target in camp.targets:
                phone = target.phone_number
                # Use phone as key if no email
                key = target.email if hasattr(target, 'email') and target.email else phone

                if key not in employee_data:
                    employee_data[key] = {
                        'name': target.name or 'Unknown',
                        'email': target.email if hasattr(target, 'email') and target.email else '',
                        'phone': phone,
                        'department': target.department or 'Unknown',
                        'campaigns_sent': 0,
                        'campaigns_opened': 0,
                        'campaigns_clicked': 0,
                        'campaigns_submitted': 0,
                        'vectors_tested': set(),
                        'vectors_failed': set(),
                        'target_ids': []  # Track target IDs for training completion lookup
                    }

                # Add target ID to track training completion
                employee_data[key]['target_ids'].append(target.id)
                employee_data[key]['campaigns_sent'] += 1
                employee_data[key]['vectors_tested'].add('SMS')

                if target.clicked_at:
                    employee_data[key]['campaigns_clicked'] += 1
                    employee_data[key]['vectors_failed'].add('SMS')

        # Process QR campaigns - NOW WE HAVE TARGETS!
        for camp in qr_campaigns:
            for target in camp.targets:
                key = target.email

                if key not in employee_data:
                    employee_data[key] = {
                        'name': target.name,
                        'email': target.email,
                        'phone': '',
                        'department': target.department or 'Unknown',
                        'campaigns_sent': 0,
                        'campaigns_opened': 0,
                        'campaigns_clicked': 0,
                        'campaigns_submitted': 0,
                        'vectors_tested': set(),
                        'vectors_failed': set(),
                        'target_ids': []  # Track target IDs for training completion lookup
                    }

                # Add target ID to track training completion
                employee_data[key]['target_ids'].append(target.id)
                employee_data[key]['campaigns_sent'] += 1
                employee_data[key]['vectors_tested'].add('QR')

                # Check if they scanned (clicked)
                if target.scanned_at:
                    employee_data[key]['campaigns_clicked'] += 1
                    employee_data[key]['vectors_failed'].add('QR')

                # Check if credentials were submitted
                if camp.landing_page_id and target.scanned_at:
                    cred_capture = CredentialCapture.query.filter(
                        CredentialCapture.campaign_id == camp.id,
                        CredentialCapture.submitted_at >= target.scanned_at
                    ).first()
                    if cred_capture:
                        employee_data[key]['campaigns_submitted'] += 1

        # Calculate risk levels and training recommendations
        results = []
        for emp_key, emp in employee_data.items():
            campaigns_sent = emp['campaigns_sent']
            campaigns_clicked = emp['campaigns_clicked']
            campaigns_submitted = emp['campaigns_submitted']

            # Calculate failure rate
            failure_rate = (campaigns_clicked / campaigns_sent * 100) if campaigns_sent > 0 else 0

            # Determine risk level
            if campaigns_submitted > 0:
                risk_level = 'critical'
            elif campaigns_clicked > 0:
                # If they clicked at least once, they failed - HIGH risk
                risk_level = 'high'
            elif emp['campaigns_opened'] > 0:
                # Opened but didn't click - MEDIUM risk
                risk_level = 'medium'
            else:
                # No interaction - LOW risk
                risk_level = 'low'

            # Training recommendation
            training_recommended = risk_level in ['critical', 'high']

            # Check if training was completed
            from models import TrainingCompletion
            training_completed = False
            if program_id:
                # First try to find by email (if available)
                if emp.get('email'):
                    completion = TrainingCompletion.query.filter_by(
                        program_id=program_id,
                        employee_email=emp.get('email')
                    ).first()
                    training_completed = completion is not None

                # If not found by email, try by target IDs (for SMS targets without emails)
                if not training_completed and emp.get('target_ids'):
                    completion = TrainingCompletion.query.filter(
                        TrainingCompletion.program_id == program_id,
                        TrainingCompletion.employee_id.in_(emp['target_ids'])
                    ).first()
                    training_completed = completion is not None

            # Outcome label
            if campaigns_submitted > 0:
                outcome_label = 'Submitted Credentials'
            elif campaigns_clicked > 0:
                outcome_label = 'Clicked Malicious Link'
            elif emp['campaigns_opened'] > 0:
                outcome_label = 'Opened Email Only'
            else:
                outcome_label = 'No Interaction'

            results.append({
                'name': emp['name'],
                'email': emp.get('email', ''),
                'phone': emp.get('phone', ''),
                'department': emp['department'],
                'campaigns_sent': campaigns_sent,
                'campaigns_clicked': campaigns_clicked,
                'campaigns_submitted': campaigns_submitted,
                'failure_rate': round(failure_rate, 1),
                'risk_level': risk_level,
                'training_recommended': training_recommended,
                'training_completed': training_completed,  # NEW: Track if they completed training
                'outcome_label': outcome_label,
                'vectors_tested': list(emp['vectors_tested']),
                'failed_vectors': list(emp['vectors_failed'])  # Vectors they actually failed (clicked on)
            })

        # Sort by risk level (critical first) and then by failure rate
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        results.sort(key=lambda x: (risk_order[x['risk_level']], -x['failure_rate']))

        return results

    @staticmethod
    def _generate_department_breakdown(email_campaigns, sms_campaigns, qr_campaigns):
        """Generate department-level risk breakdown"""
        dept_data = {}

        # Process email campaigns
        for camp in email_campaigns:
            for target in camp.targets:
                dept = target.department or 'Unknown'
                if dept not in dept_data:
                    dept_data[dept] = {
                        'total_employees': set(),
                        'total_sent': 0,
                        'total_clicked': 0
                    }

                dept_data[dept]['total_employees'].add(target.email)
                dept_data[dept]['total_sent'] += 1
                if target.clicked_at:
                    dept_data[dept]['total_clicked'] += 1

        # Process SMS campaigns
        for camp in sms_campaigns:
            for target in camp.targets:
                dept = target.department or 'Unknown'
                key = target.email if hasattr(target, 'email') and target.email else target.phone_number

                if dept not in dept_data:
                    dept_data[dept] = {
                        'total_employees': set(),
                        'total_sent': 0,
                        'total_clicked': 0
                    }

                dept_data[dept]['total_employees'].add(key)
                dept_data[dept]['total_sent'] += 1
                if target.clicked_at:
                    dept_data[dept]['total_clicked'] += 1

        # Process QR campaigns
        for camp in qr_campaigns:
            for target in camp.targets:
                dept = target.department or 'Unknown'

                if dept not in dept_data:
                    dept_data[dept] = {
                        'total_employees': set(),
                        'total_sent': 0,
                        'total_clicked': 0
                    }

                dept_data[dept]['total_employees'].add(target.email)
                dept_data[dept]['total_sent'] += 1
                if target.scanned_at:
                    dept_data[dept]['total_clicked'] += 1

        # Calculate risk levels
        departments = []
        for dept_name, data in dept_data.items():
            total_employees = len(data['total_employees'])
            click_rate = (data['total_clicked'] / data['total_sent'] * 100) if data['total_sent'] > 0 else 0

            # Determine risk level
            if click_rate >= 75:
                risk_level = 'critical'
            elif click_rate >= 50:
                risk_level = 'high'
            elif click_rate >= 25:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            departments.append({
                'department': dept_name,
                'total_employees': total_employees,
                'total_tests': data['total_sent'],
                'total_clicked': data['total_clicked'],
                'click_rate': round(click_rate, 1),
                'risk_level': risk_level
            })

        # Sort by risk level
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        departments.sort(key=lambda x: (risk_order[x['risk_level']], -x['click_rate']))

        return departments

    @staticmethod
    def _generate_security_gaps(email_campaigns, sms_campaigns, qr_campaigns, employee_results, department_breakdown):
        """Identify security gaps and recommendations"""
        gaps = []

        # Overall risk assessment
        high_risk_employees = [e for e in employee_results if e['risk_level'] in ['critical', 'high']]
        high_risk_departments = [d for d in department_breakdown if d['risk_level'] in ['critical', 'high']]

        overall_failure_rate = sum(e['campaigns_clicked'] for e in employee_results) / sum(e['campaigns_sent'] for e in employee_results) * 100 if employee_results else 0

        if overall_failure_rate > 50:
            overall_risk_level = 'High'
        elif overall_failure_rate > 25:
            overall_risk_level = 'Medium'
        else:
            overall_risk_level = 'Low'

        # Gap 1: High-risk employees
        if len(high_risk_employees) > 0:
            gaps.append({
                'category': 'Employee Risk',
                'severity': 'critical' if len(high_risk_employees) > 5 else 'high',
                'finding': f'{len(high_risk_employees)} employees showed high susceptibility to phishing',
                'recommendation': f'Immediate mandatory security awareness training required for {len(high_risk_employees)} employees'
            })

        # Gap 2: High-risk departments
        if len(high_risk_departments) > 0:
            dept_names = ', '.join([d['department'] for d in high_risk_departments[:3]])
            gaps.append({
                'category': 'Department Risk',
                'severity': 'high',
                'finding': f'{len(high_risk_departments)} departments showed elevated risk levels: {dept_names}',
                'recommendation': 'Department-wide training sessions and targeted security education programs'
            })

        # Gap 3: Credential submission
        submitted_count = sum(e['campaigns_submitted'] for e in employee_results)
        if submitted_count > 0:
            gaps.append({
                'category': 'Credential Compromise',
                'severity': 'critical',
                'finding': f'{submitted_count} employees submitted credentials to phishing pages',
                'recommendation': 'Urgent password reset and MFA enrollment for affected accounts. Enhanced authentication training required.'
            })

        # Gap 4: Multi-vector failures
        multi_vector_failures = [e for e in employee_results if len(e['vectors_tested']) > 1 and e['risk_level'] in ['critical', 'high']]
        if len(multi_vector_failures) > 0:
            gaps.append({
                'category': 'Multi-Vector Vulnerability',
                'severity': 'high',
                'finding': f'{len(multi_vector_failures)} employees failed across multiple attack vectors',
                'recommendation': 'Comprehensive security awareness training covering email, SMS, and QR code threats'
            })

        summary = f"Overall organizational risk level: {overall_risk_level}. {len(gaps)} critical security gaps identified requiring immediate attention."

        return {
            'overall_risk_level': overall_risk_level,
            'overall_failure_rate': round(overall_failure_rate, 1),
            'high_risk_employee_count': len(high_risk_employees),
            'high_risk_department_count': len(high_risk_departments),
            'summary': summary,
            'gaps': gaps
        }
