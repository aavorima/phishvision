"""
Campaign Awareness Report Service
Generates comprehensive security awareness reports for completed campaigns
"""

from database import db
from models import Campaign, CampaignTarget, Employee, HVSEvent
from sqlalchemy import func
from datetime import datetime


class CampaignReportService:
    """Service for generating campaign awareness reports"""

    @staticmethod
    def generate_report(campaign_id):
        """
        Generate a comprehensive awareness report for a campaign

        Returns:
            dict: Complete campaign awareness report
        """
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        targets = campaign.targets
        total_targets = len(targets)

        if total_targets == 0:
            return {
                'error': 'No targets found for this campaign',
                'campaign_id': campaign_id
            }

        # 1. Campaign Overview
        overview = CampaignReportService._generate_overview(campaign, targets)

        # 2. Company-Level Awareness Summary
        awareness_summary = CampaignReportService._generate_awareness_summary(campaign, targets)

        # 3. Employee Results
        employee_results = CampaignReportService._generate_employee_results(campaign, targets)

        # 4. Department Risk Breakdown
        department_breakdown = CampaignReportService._generate_department_breakdown(targets)

        # 5. Identified Security Gaps
        security_gaps = CampaignReportService._generate_security_gaps(campaign, targets, department_breakdown)

        return {
            'campaign_id': campaign_id,
            'generated_at': datetime.utcnow().isoformat(),
            'overview': overview,
            'awareness_summary': awareness_summary,
            'employee_results': employee_results,
            'department_breakdown': department_breakdown,
            'security_gaps': security_gaps
        }

    @staticmethod
    def _generate_overview(campaign, targets):
        """Generate campaign overview section"""
        total_targets = len(targets)
        opened = sum(1 for t in targets if t.opened_at)
        clicked = sum(1 for t in targets if t.clicked_at)

        # Determine campaign type
        campaign_type = 'Email'
        if hasattr(campaign, 'landing_page_id') and campaign.landing_page_id:
            campaign_type = 'Email with Credential Harvesting'

        # Calculate duration using target timestamps
        duration = None
        sent_times = [t.sent_at for t in targets if t.sent_at]
        if sent_times:
            earliest_sent = min(sent_times)
            latest_interaction = max(
                [t.clicked_at for t in targets if t.clicked_at] +
                [t.opened_at for t in targets if t.opened_at] +
                [earliest_sent]
            )

            if latest_interaction and earliest_sent:
                duration_delta = latest_interaction - earliest_sent
                duration = {
                    'days': duration_delta.days,
                    'hours': duration_delta.seconds // 3600,
                    'minutes': (duration_delta.seconds % 3600) // 60
                }

        # Get sent_at from first target
        sent_at = min(sent_times) if sent_times else None

        # Determine completed_at based on status or last interaction
        completed_at = None
        if campaign.status == 'completed':
            interaction_times = [t.clicked_at for t in targets if t.clicked_at] + [t.opened_at for t in targets if t.opened_at]
            completed_at = max(interaction_times) if interaction_times else None

        return {
            'campaign_name': campaign.name,
            'campaign_type': campaign_type,
            'status': campaign.status,
            'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
            'sent_at': sent_at.isoformat() if sent_at else None,
            'completed_at': completed_at.isoformat() if completed_at else None,
            'duration': duration,
            'total_targets': total_targets,
            'total_opened': opened,
            'total_clicked': clicked,
            'open_rate': round((opened / total_targets * 100), 2) if total_targets > 0 else 0,
            'click_rate': round((clicked / total_targets * 100), 2) if total_targets > 0 else 0
        }

    @staticmethod
    def _generate_awareness_summary(campaign, targets):
        """Generate company-level awareness summary"""
        total_targets = len(targets)

        # Count interactions
        no_interaction = sum(1 for t in targets if not t.opened_at and not t.clicked_at)
        opened_only = sum(1 for t in targets if t.opened_at and not t.clicked_at)
        clicked = sum(1 for t in targets if t.clicked_at)

        # Get credential submissions if applicable
        submitted_credentials = 0
        if hasattr(campaign, 'landing_page_id') and campaign.landing_page_id:
            from models import CredentialCapture
            submitted_credentials = CredentialCapture.query.filter_by(
                landing_page_id=campaign.landing_page_id
            ).count()

        # Calculate awareness score (0-100)
        # Higher score = better awareness (fewer people fell for phishing)
        awareness_score = 0
        if total_targets > 0:
            # No interaction: 100 points
            # Opened only: 70 points
            # Clicked: 30 points
            # Submitted credentials: 0 points
            awareness_score = (
                (no_interaction * 100) +
                (opened_only * 70) +
                ((clicked - submitted_credentials) * 30) +
                (submitted_credentials * 0)
            ) / total_targets
            awareness_score = round(awareness_score, 1)

        # Determine awareness level
        if awareness_score >= 80:
            awareness_level = 'Excellent'
            level_color = 'green'
        elif awareness_score >= 60:
            awareness_level = 'Good'
            level_color = 'blue'
        elif awareness_score >= 40:
            awareness_level = 'Fair'
            level_color = 'yellow'
        elif awareness_score >= 20:
            awareness_level = 'Poor'
            level_color = 'orange'
        else:
            awareness_level = 'Critical'
            level_color = 'red'

        return {
            'total_employees': total_targets,
            'no_interaction_count': no_interaction,
            'no_interaction_percent': round((no_interaction / total_targets * 100), 2) if total_targets > 0 else 0,
            'opened_only_count': opened_only,
            'opened_only_percent': round((opened_only / total_targets * 100), 2) if total_targets > 0 else 0,
            'clicked_count': clicked,
            'clicked_percent': round((clicked / total_targets * 100), 2) if total_targets > 0 else 0,
            'submitted_credentials_count': submitted_credentials,
            'submitted_credentials_percent': round((submitted_credentials / total_targets * 100), 2) if total_targets > 0 else 0,
            'awareness_score': awareness_score,
            'awareness_level': awareness_level,
            'level_color': level_color,
            'score_explanation': 'Awareness Score is calculated based on employee behavior: No interaction (100 pts), Opened only (70 pts), Clicked link (30 pts), Submitted credentials (0 pts).'
        }

    @staticmethod
    def _generate_employee_results(campaign, targets):
        """Generate individual employee results"""
        results = []

        # Get credential submissions if applicable
        credential_submissions = {}
        if hasattr(campaign, 'landing_page_id') and campaign.landing_page_id:
            from models import CredentialCapture
            captures = CredentialCapture.query.filter_by(
                landing_page_id=campaign.landing_page_id
            ).all()
            for capture in captures:
                credential_submissions[capture.email] = True

        for target in targets:
            # Get employee info
            employee = Employee.query.filter_by(email=target.email).first()

            # Determine outcome
            if target.email in credential_submissions:
                outcome = 'submitted_credentials'
                outcome_label = 'Submitted Credentials'
                risk_level = 'critical'
            elif target.clicked_at:
                outcome = 'clicked_link'
                outcome_label = 'Clicked Link'
                risk_level = 'high'
            elif target.opened_at:
                outcome = 'opened_only'
                outcome_label = 'Opened Email'
                risk_level = 'medium'
            else:
                outcome = 'no_interaction'
                outcome_label = 'No Interaction'
                risk_level = 'low'

            # Determine phishing type that failed
            failed_technique = None
            if outcome in ['clicked_link', 'submitted_credentials']:
                # Analyze based on campaign type
                if 'urgent' in campaign.name.lower() or 'immediate' in campaign.name.lower():
                    failed_technique = 'Urgency-based manipulation'
                elif 'ceo' in campaign.name.lower() or 'executive' in campaign.name.lower():
                    failed_technique = 'Authority impersonation'
                elif 'password' in campaign.name.lower() or 'account' in campaign.name.lower():
                    failed_technique = 'Account security pretext'
                elif 'invoice' in campaign.name.lower() or 'payment' in campaign.name.lower():
                    failed_technique = 'Financial pretext'
                else:
                    failed_technique = 'Email impersonation'

            # Training recommendation
            training_recommended = outcome in ['clicked_link', 'submitted_credentials']

            results.append({
                'employee_id': employee.id if employee else None,
                'email': target.email,
                'name': f"{employee.first_name} {employee.last_name}" if employee else target.email,
                'department': employee.department if employee else 'Unknown',
                'outcome': outcome,
                'outcome_label': outcome_label,
                'risk_level': risk_level,
                'failed_technique': failed_technique,
                'opened_at': target.opened_at.isoformat() if target.opened_at else None,
                'clicked_at': target.clicked_at.isoformat() if target.clicked_at else None,
                'training_recommended': training_recommended,
                'current_hvs_score': employee.hvs_score if employee else None,
                'hvs_level': employee.get_hvs_level() if employee else None
            })

        # Sort by risk level (critical first)
        risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        results.sort(key=lambda x: risk_order.get(x['risk_level'], 4))

        return results

    @staticmethod
    def _generate_department_breakdown(targets):
        """Generate department risk breakdown"""
        # Group targets by department
        dept_data = {}

        for target in targets:
            employee = Employee.query.filter_by(email=target.email).first()
            dept = employee.department if employee else 'Unknown'

            if dept not in dept_data:
                dept_data[dept] = {
                    'department': dept,
                    'total_employees': 0,
                    'clicked_count': 0,
                    'opened_count': 0,
                    'no_interaction_count': 0,
                    'hvs_scores': []
                }

            dept_data[dept]['total_employees'] += 1

            if target.clicked_at:
                dept_data[dept]['clicked_count'] += 1
            elif target.opened_at:
                dept_data[dept]['opened_count'] += 1
            else:
                dept_data[dept]['no_interaction_count'] += 1

            if employee and employee.hvs_score is not None:
                dept_data[dept]['hvs_scores'].append(employee.hvs_score)

        # Calculate rates and averages
        breakdown = []
        for dept, data in dept_data.items():
            total = data['total_employees']
            avg_hvs = sum(data['hvs_scores']) / len(data['hvs_scores']) if data['hvs_scores'] else 0

            # Determine risk level
            click_rate = (data['clicked_count'] / total * 100) if total > 0 else 0
            if click_rate >= 50 or avg_hvs >= 75:
                risk_level = 'critical'
            elif click_rate >= 30 or avg_hvs >= 50:
                risk_level = 'high'
            elif click_rate >= 15 or avg_hvs >= 25:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            breakdown.append({
                'department': dept,
                'total_employees': total,
                'clicked_count': data['clicked_count'],
                'click_rate': round(click_rate, 2),
                'opened_count': data['opened_count'],
                'open_rate': round((data['opened_count'] / total * 100), 2) if total > 0 else 0,
                'no_interaction_rate': round((data['no_interaction_count'] / total * 100), 2) if total > 0 else 0,
                'avg_hvs_score': round(avg_hvs, 1),
                'risk_level': risk_level
            })

        # Sort by click rate (highest risk first)
        breakdown.sort(key=lambda x: x['click_rate'], reverse=True)

        return breakdown

    @staticmethod
    def _generate_security_gaps(campaign, targets, department_breakdown):
        """Identify and summarize security gaps"""
        total_targets = len(targets)
        clicked = sum(1 for t in targets if t.clicked_at)
        click_rate = (clicked / total_targets * 100) if total_targets > 0 else 0

        gaps = []

        # 1. Overall vulnerability assessment
        if click_rate >= 40:
            gaps.append({
                'severity': 'critical',
                'category': 'Overall Awareness',
                'finding': f'{click_rate:.1f}% of employees clicked on the phishing link',
                'recommendation': 'Immediate organization-wide security awareness training is recommended.'
            })
        elif click_rate >= 20:
            gaps.append({
                'severity': 'high',
                'category': 'Overall Awareness',
                'finding': f'{click_rate:.1f}% of employees clicked on the phishing link',
                'recommendation': 'Enhanced security awareness training should be provided to all employees.'
            })
        elif click_rate >= 10:
            gaps.append({
                'severity': 'medium',
                'category': 'Overall Awareness',
                'finding': f'{click_rate:.1f}% of employees clicked on the phishing link',
                'recommendation': 'Targeted training for affected employees is recommended.'
            })

        # 2. High-risk departments
        high_risk_depts = [d for d in department_breakdown if d['risk_level'] in ['critical', 'high']]
        if high_risk_depts:
            dept_names = ', '.join([d['department'] for d in high_risk_depts[:3]])
            gaps.append({
                'severity': 'high',
                'category': 'Department Risk',
                'finding': f'Higher susceptibility observed in: {dept_names}',
                'recommendation': f'Implement department-specific training programs focusing on common attack vectors.'
            })

        # 3. Attack technique analysis
        campaign_name_lower = campaign.name.lower()
        if 'urgent' in campaign_name_lower or 'immediate' in campaign_name_lower:
            if click_rate > 15:
                gaps.append({
                    'severity': 'high',
                    'category': 'Attack Technique',
                    'finding': 'Urgency-based phishing tactics showed high success rate',
                    'recommendation': 'Train employees to identify and resist urgency-based manipulation techniques.'
                })

        if 'ceo' in campaign_name_lower or 'executive' in campaign_name_lower:
            if click_rate > 15:
                gaps.append({
                    'severity': 'high',
                    'category': 'Attack Technique',
                    'finding': 'Authority impersonation attacks were effective',
                    'recommendation': 'Implement verification procedures for requests from executives and establish out-of-band communication channels.'
                })

        # 4. Credential submission risk
        credential_count = 0
        if hasattr(campaign, 'landing_page_id') and campaign.landing_page_id:
            from models import CredentialCapture
            credential_count = CredentialCapture.query.filter_by(
                landing_page_id=campaign.landing_page_id
            ).count()

        if credential_count > 0:
            cred_rate = (credential_count / total_targets * 100)
            gaps.append({
                'severity': 'critical',
                'category': 'Credential Security',
                'finding': f'{credential_count} employees ({cred_rate:.1f}%) submitted credentials on a fake login page',
                'recommendation': 'Mandatory password security and MFA training required. Consider implementing passwordless authentication.'
            })

        # 5. Positive findings
        no_interaction = sum(1 for t in targets if not t.opened_at and not t.clicked_at)
        if no_interaction > total_targets * 0.5:
            gaps.append({
                'severity': 'positive',
                'category': 'Awareness Success',
                'finding': f'{(no_interaction / total_targets * 100):.1f}% of employees did not interact with the phishing attempt',
                'recommendation': 'Current security awareness measures are showing effectiveness. Continue reinforcement training.'
            })

        # Summary
        summary = CampaignReportService._generate_gap_summary(click_rate, high_risk_depts, credential_count, campaign)

        return {
            'summary': summary,
            'gaps': gaps,
            'overall_risk_level': 'critical' if click_rate >= 40 else 'high' if click_rate >= 20 else 'medium' if click_rate >= 10 else 'low'
        }

    @staticmethod
    def _generate_gap_summary(click_rate, high_risk_depts, credential_count, campaign):
        """Generate natural language summary of security gaps"""
        summary_parts = []

        # Attack type
        campaign_name_lower = campaign.name.lower()
        attack_type = 'email-based phishing'
        if 'sms' in campaign_name_lower:
            attack_type = 'SMS-based phishing'
        elif 'qr' in campaign_name_lower:
            attack_type = 'QR code phishing'

        # Main finding
        if click_rate >= 40:
            summary_parts.append(f"This campaign revealed critical security awareness gaps, with {click_rate:.1f}% of employees clicking on the {attack_type} attempt.")
        elif click_rate >= 20:
            summary_parts.append(f"This campaign identified significant security awareness concerns, as {click_rate:.1f}% of employees interacted with the {attack_type} attempt.")
        elif click_rate >= 10:
            summary_parts.append(f"This campaign showed moderate susceptibility to {attack_type}, with {click_rate:.1f}% of employees clicking the malicious link.")
        else:
            summary_parts.append(f"This campaign demonstrated good overall awareness, with only {click_rate:.1f}% of employees clicking on the {attack_type} attempt.")

        # Department-specific findings
        if high_risk_depts:
            dept_names = ' and '.join([d['department'] for d in high_risk_depts[:2]])
            summary_parts.append(f"Higher susceptibility was observed in the {dept_names} department(s).")

        # Credential submission
        if credential_count > 0:
            summary_parts.append(f"Critically, {credential_count} employees submitted their credentials on a fake login page, indicating a need for enhanced password security training.")

        # Technique-specific
        if 'urgent' in campaign_name_lower or 'immediate' in campaign_name_lower:
            summary_parts.append("Urgency-based manipulation tactics proved effective, suggesting employees may benefit from training on recognizing pressure tactics.")
        elif 'ceo' in campaign_name_lower or 'executive' in campaign_name_lower:
            summary_parts.append("Authority impersonation techniques were successful, highlighting the need for verification procedures for executive requests.")

        return ' '.join(summary_parts)
