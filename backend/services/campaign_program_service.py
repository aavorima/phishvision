"""
Campaign Program Service

Responsibilities:
1. Create and configure vulnerability profiling programs
2. Generate scheduled campaigns across the program duration
3. Select appropriate templates based on phase, technique, and difficulty
4. Manage program lifecycle (schedule, start, pause, complete)
5. Adapt future campaigns based on employee responses
6. Process scheduled campaigns and send emails
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import random
import uuid

from database import db
from models import (
    Employee, CampaignProgram, ProgramPhase, ScheduledCampaign,
    CustomTemplate, Campaign, CampaignTarget, VulnerabilityProfile,
    LandingPage, Settings, User, ProgramScenario, ScenarioAssignment
)
from services.vulnerability_analyzer import VulnerabilityAnalyzer


class CampaignProgramService:
    """
    Service for managing month-long vulnerability profiling programs.
    """

    # Default techniques to test
    DEFAULT_TECHNIQUES = ['urgency', 'authority', 'fear', 'curiosity', 'reward', 'social_proof']

    # Default vectors
    DEFAULT_VECTORS = ['email']  # Can expand to qr, sms

    # Default difficulty progression
    DEFAULT_DIFFICULTIES = ['easy', 'medium', 'hard', 'expert']

    # Phase configurations for a typical 4-week program
    DEFAULT_PHASES = [
        {'name': 'Week 1 - Baseline', 'difficulty': 'easy', 'duration_days': 7, 'techniques': ['urgency', 'reward']},
        {'name': 'Week 2 - Intermediate', 'difficulty': 'medium', 'duration_days': 7, 'techniques': ['authority', 'fear']},
        {'name': 'Week 3 - Advanced', 'difficulty': 'hard', 'duration_days': 7, 'techniques': ['curiosity', 'social_proof']},
        {'name': 'Week 4 - Expert', 'difficulty': 'expert', 'duration_days': 7, 'techniques': ['urgency', 'authority', 'fear']}
    ]

    def __init__(self):
        self.vulnerability_analyzer = VulnerabilityAnalyzer()

    def create_program(
        self,
        name: str,
        description: str = None,
        duration_days: int = 30,
        techniques_to_test: List[str] = None,
        vectors_to_test: List[str] = None,
        difficulty_levels: List[str] = None,
        emails_per_week_per_user: int = 2,
        target_all_employees: bool = False,
        target_departments: List[str] = None,
        target_employee_ids: List[str] = None,
        use_progressive_difficulty: bool = True,
        adapt_to_responses: bool = True,
        scheduled_start: datetime = None,
        created_by: str = None
    ) -> CampaignProgram:
        """
        Create a new vulnerability profiling campaign program.
        """
        program = CampaignProgram(
            name=name,
            description=description,
            duration_days=duration_days,
            techniques_to_test=json.dumps(techniques_to_test or self.DEFAULT_TECHNIQUES),
            vectors_to_test=json.dumps(vectors_to_test or self.DEFAULT_VECTORS),
            difficulty_levels=json.dumps(difficulty_levels or self.DEFAULT_DIFFICULTIES),
            emails_per_week_per_user=emails_per_week_per_user,
            target_all_employees=target_all_employees,
            target_departments=json.dumps(target_departments) if target_departments else None,
            target_employee_ids=json.dumps(target_employee_ids) if target_employee_ids else None,
            use_progressive_difficulty=use_progressive_difficulty,
            adapt_to_responses=adapt_to_responses,
            scheduled_start=scheduled_start,
            created_by=created_by,
            status='draft'
        )

        db.session.add(program)
        db.session.flush()

        # Create default phases
        self._create_default_phases(program)

        db.session.commit()
        return program

    def _create_default_phases(self, program: CampaignProgram):
        """Create default phases for the program"""
        techniques = json.loads(program.techniques_to_test) if program.techniques_to_test else self.DEFAULT_TECHNIQUES
        vectors = json.loads(program.vectors_to_test) if program.vectors_to_test else self.DEFAULT_VECTORS

        # Calculate phase count based on duration
        weeks = max(1, program.duration_days // 7)

        for i in range(weeks):
            # Distribute techniques across phases
            phase_techniques = techniques[i % len(techniques):] + techniques[:i % len(techniques)]
            phase_techniques = phase_techniques[:2]  # 2 techniques per phase

            # Progressive difficulty
            if program.use_progressive_difficulty:
                difficulty_index = min(i, len(self.DEFAULT_DIFFICULTIES) - 1)
                difficulty = self.DEFAULT_DIFFICULTIES[difficulty_index]
            else:
                difficulty = 'medium'

            phase = ProgramPhase(
                program_id=program.id,
                name=f'Week {i + 1}',
                description=f'Testing {", ".join(phase_techniques)} techniques at {difficulty} difficulty',
                phase_number=i + 1,
                difficulty_level=difficulty,
                techniques_focus=json.dumps(phase_techniques),
                vectors_focus=json.dumps(vectors),
                start_day=i * 7,
                duration_days=7,
                status='pending'
            )
            db.session.add(phase)

    def schedule_program(self, program_id: str) -> Dict:
        """
        Generate all scheduled campaigns for a program.
        Must be called before starting the program.
        """
        program = CampaignProgram.query.get(program_id)
        if not program:
            return {'error': 'Program not found'}

        if program.status not in ['draft', 'scheduled']:
            return {'error': f'Cannot schedule program in {program.status} status'}

        # Get target employees
        employees = self._get_target_employees(program)
        if not employees:
            return {'error': 'No employees match the targeting criteria'}

        program.total_employees_targeted = len(employees)

        # Clear any existing scheduled campaigns
        ScheduledCampaign.query.filter_by(program_id=program_id).delete()

        # Get available templates grouped by technique and difficulty
        templates_by_config = self._get_templates_by_config()

        # Get phases
        phases = ProgramPhase.query.filter_by(program_id=program_id).order_by(ProgramPhase.phase_number).all()

        start_date = program.scheduled_start or datetime.utcnow()
        program.ends_at = start_date + timedelta(days=program.duration_days)

        scheduled_count = 0

        for employee in employees:
            # Track last scheduled date for this employee to maintain spacing
            last_scheduled = start_date - timedelta(days=program.min_days_between_emails)

            for phase in phases:
                # How many emails to send in this phase
                phase_emails = self._calculate_phase_emails(
                    phase.duration_days,
                    program.emails_per_week_per_user
                )

                techniques = json.loads(phase.techniques_focus) if phase.techniques_focus else self.DEFAULT_TECHNIQUES
                vectors = json.loads(phase.vectors_focus) if phase.vectors_focus else ['email']

                for email_num in range(phase_emails):
                    # Select technique and vector for this email
                    technique = techniques[email_num % len(techniques)]
                    vector = vectors[email_num % len(vectors)]

                    # Find appropriate template
                    template = self._select_template(
                        templates_by_config,
                        technique=technique,
                        difficulty=phase.difficulty_level,
                        employee_id=employee.id
                    )

                    if not template:
                        continue

                    # Schedule the email
                    scheduled_time = self._calculate_scheduled_time(
                        start_date=start_date,
                        phase=phase,
                        email_num=email_num,
                        phase_emails=phase_emails,
                        last_scheduled=last_scheduled,
                        min_days_between=program.min_days_between_emails,
                        randomize=program.randomize_timing
                    )

                    scheduled_campaign = ScheduledCampaign(
                        program_id=program_id,
                        phase_id=phase.id,
                        employee_id=employee.id,
                        template_id=template.id,
                        scheduled_for=scheduled_time,
                        technique_tested=technique,
                        vector_type=vector,
                        difficulty_level=phase.difficulty_level,
                        status='scheduled'
                    )
                    db.session.add(scheduled_campaign)
                    last_scheduled = scheduled_time
                    scheduled_count += 1

        program.total_emails_scheduled = scheduled_count
        program.status = 'scheduled'

        db.session.commit()

        return {
            'success': True,
            'program_id': program_id,
            'employees_targeted': len(employees),
            'emails_scheduled': scheduled_count,
            'start_date': start_date.isoformat(),
            'end_date': program.ends_at.isoformat()
        }

    def _get_target_employees(self, program: CampaignProgram) -> List[Employee]:
        """Get list of employees to target based on program configuration"""
        query = Employee.query.filter_by(is_active=True)

        if program.target_all_employees:
            return query.all()

        if program.target_employee_ids:
            employee_ids = json.loads(program.target_employee_ids)
            return query.filter(Employee.id.in_(employee_ids)).all()

        if program.target_departments:
            departments = json.loads(program.target_departments)
            return query.filter(Employee.department.in_(departments)).all()

        return []

    def _get_templates_by_config(self) -> Dict:
        """Get all active templates organized by technique and difficulty"""
        templates = CustomTemplate.query.filter_by(is_active=True).all()

        organized = {}
        for template in templates:
            technique = template.technique_type or 'general'
            difficulty = template.difficulty or 'medium'

            key = f"{technique}_{difficulty}"
            if key not in organized:
                organized[key] = []
            organized[key].append(template)

        return organized

    def _select_template(
        self,
        templates_by_config: Dict,
        technique: str,
        difficulty: str,
        employee_id: str
    ) -> Optional[CustomTemplate]:
        """Select an appropriate template for the given configuration"""
        # Try exact match first
        key = f"{technique}_{difficulty}"
        if key in templates_by_config and templates_by_config[key]:
            return random.choice(templates_by_config[key])

        # Try technique with any difficulty
        for diff in ['easy', 'medium', 'hard', 'expert']:
            key = f"{technique}_{diff}"
            if key in templates_by_config and templates_by_config[key]:
                return random.choice(templates_by_config[key])

        # Try general templates at the right difficulty
        key = f"general_{difficulty}"
        if key in templates_by_config and templates_by_config[key]:
            return random.choice(templates_by_config[key])

        # Fallback to any available template
        for templates in templates_by_config.values():
            if templates:
                return random.choice(templates)

        return None

    def _calculate_phase_emails(self, phase_duration_days: int, emails_per_week: int) -> int:
        """Calculate how many emails to send in a phase"""
        weeks = phase_duration_days / 7
        return max(1, int(weeks * emails_per_week))

    def _calculate_scheduled_time(
        self,
        start_date: datetime,
        phase: ProgramPhase,
        email_num: int,
        phase_emails: int,
        last_scheduled: datetime,
        min_days_between: int,
        randomize: bool
    ) -> datetime:
        """Calculate when to schedule an email within a phase"""
        phase_start = start_date + timedelta(days=phase.start_day)
        phase_end = phase_start + timedelta(days=phase.duration_days)

        # Spread emails evenly across the phase
        if phase_emails > 1:
            interval = phase.duration_days / phase_emails
            base_day = phase.start_day + (email_num * interval)
        else:
            base_day = phase.start_day + (phase.duration_days / 2)

        scheduled = start_date + timedelta(days=base_day)

        # Add randomization (within business hours)
        if randomize:
            # Random hour between 9 AM and 5 PM
            random_hour = random.randint(9, 16)
            random_minute = random.randint(0, 59)
            scheduled = scheduled.replace(hour=random_hour, minute=random_minute)

            # Add random offset of 0-2 days
            scheduled += timedelta(hours=random.randint(0, 48))

        # Ensure minimum spacing from last email
        min_next = last_scheduled + timedelta(days=min_days_between)
        if scheduled < min_next:
            scheduled = min_next

        # Don't schedule beyond phase end
        if scheduled > phase_end:
            scheduled = phase_end - timedelta(hours=random.randint(1, 12))

        return scheduled

    def start_program(self, program_id: str) -> Dict:
        """Start a scheduled program"""
        program = CampaignProgram.query.get(program_id)
        if not program:
            return {'error': 'Program not found'}

        if program.status != 'scheduled':
            return {'error': f'Cannot start program in {program.status} status. Must be scheduled first.'}

        program.status = 'active'
        program.started_at = datetime.utcnow()

        # Activate first phase
        first_phase = ProgramPhase.query.filter_by(
            program_id=program_id,
            phase_number=1
        ).first()
        if first_phase:
            first_phase.status = 'active'

        db.session.commit()

        return {
            'success': True,
            'program_id': program_id,
            'status': 'active',
            'started_at': program.started_at.isoformat()
        }

    def pause_program(self, program_id: str) -> Dict:
        """Pause an active program"""
        program = CampaignProgram.query.get(program_id)
        if not program:
            return {'error': 'Program not found'}

        if program.status != 'active':
            return {'error': 'Can only pause active programs'}

        program.status = 'paused'
        db.session.commit()

        return {'success': True, 'status': 'paused'}

    def resume_program(self, program_id: str) -> Dict:
        """Resume a paused program"""
        program = CampaignProgram.query.get(program_id)
        if not program:
            return {'error': 'Program not found'}

        if program.status != 'paused':
            return {'error': 'Can only resume paused programs'}

        program.status = 'active'
        db.session.commit()

        return {'success': True, 'status': 'active'}

    def complete_program(self, program_id: str) -> Dict:
        """Mark a program as completed"""
        program = CampaignProgram.query.get(program_id)
        if not program:
            return {'error': 'Program not found'}

        program.status = 'completed'
        program.completed_at = datetime.utcnow()

        # Complete all phases
        ProgramPhase.query.filter_by(program_id=program_id).update({'status': 'completed'})

        # Cancel any remaining scheduled campaigns
        ScheduledCampaign.query.filter_by(
            program_id=program_id,
            status='scheduled'
        ).update({'status': 'cancelled'})

        db.session.commit()

        return {
            'success': True,
            'status': 'completed',
            'completed_at': program.completed_at.isoformat()
        }

    def process_due_campaigns(self, batch_size: int = 50) -> Dict:
        """
        Process scheduled campaigns that are due to be sent.
        Should be called periodically by a scheduler/cron job.
        """
        now = datetime.utcnow()

        # Get campaigns that are due
        due_campaigns = ScheduledCampaign.query.filter(
            ScheduledCampaign.scheduled_for <= now,
            ScheduledCampaign.status == 'scheduled'
        ).join(
            CampaignProgram
        ).filter(
            CampaignProgram.status == 'active'
        ).limit(batch_size).all()

        results = {
            'processed': 0,
            'sent': 0,
            'failed': 0,
            'errors': []
        }

        for scheduled in due_campaigns:
            try:
                result = self._send_scheduled_campaign(scheduled)
                results['processed'] += 1
                if result.get('success'):
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(result.get('error'))
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                scheduled.status = 'failed'

        db.session.commit()
        return results

    def _send_scheduled_campaign(self, scheduled: ScheduledCampaign) -> Dict:
        """Send a single scheduled campaign email"""
        from services.email_service import EmailService
        from services.email_parser import parse_email_to_name, substitute_template_variables
        import os

        employee = Employee.query.get(scheduled.employee_id)
        template = CustomTemplate.query.get(scheduled.template_id)
        program = CampaignProgram.query.get(scheduled.program_id)

        if not employee or not template or not program:
            scheduled.status = 'failed'
            return {'error': 'Missing employee, template, or program'}

        # Get user settings for SMTP (use program creator's settings)
        settings = None
        if program.created_by:
            settings = Settings.query.filter_by(user_id=program.created_by).first()

        # Create email service
        email_service = EmailService.from_user_settings(settings, allow_env_fallback=True)

        if not email_service.is_configured():
            scheduled.status = 'failed'
            return {'error': 'SMTP not configured'}

        # Create tracking campaign
        campaign = Campaign(
            name=f"{program.name} - {scheduled.id[:8]}",
            template_type=template.id,
            subject=template.subject,
            target_emails=json.dumps([employee.email]),
            status='active'
        )
        db.session.add(campaign)
        db.session.flush()

        # Create tracking target
        tracking_token = str(uuid.uuid4())
        target = CampaignTarget(
            campaign_id=campaign.id,
            email=employee.email,
            tracking_token=tracking_token
        )
        db.session.add(target)
        db.session.flush()

        # Link scheduled campaign to actual campaign
        scheduled.campaign_id = campaign.id
        scheduled.target_id = target.id

        # Prepare email content
        base_url = os.getenv('BASE_URL', 'http://localhost:5000')
        recipient_data = parse_email_to_name(employee.email)
        recipient_data['first_name'] = employee.first_name
        recipient_data['last_name'] = employee.last_name
        recipient_data['full_name'] = f"{employee.first_name} {employee.last_name}"
        recipient_data['tracking_link'] = f"{base_url}/api/track/click/{tracking_token}"
        recipient_data['base_url'] = base_url

        final_subject = substitute_template_variables(template.subject, recipient_data)
        final_html = substitute_template_variables(template.html_content, recipient_data)

        # Add tracking pixel
        tracking_pixel = f'<img src="{base_url}/api/track/open/{tracking_token}" width="1" height="1" style="display:none;" />'
        if '</body>' in final_html:
            final_html = final_html.replace('</body>', f'{tracking_pixel}</body>')
        else:
            final_html += tracking_pixel

        # Send email
        success = email_service.send_email(
            employee.email,
            final_subject,
            final_html,
            from_name_override=template.from_name
        )

        if success:
            scheduled.status = 'sent'
            scheduled.sent_at = datetime.utcnow()
            program.total_emails_sent += 1
            return {'success': True, 'tracking_token': tracking_token}
        else:
            scheduled.status = 'failed'
            return {'error': 'Failed to send email'}

    def record_interaction(
        self,
        tracking_token: str,
        interaction_type: str,  # 'open', 'click', 'submit', 'report'
        device_type: Optional[str] = None
    ) -> Dict:
        """
        Record an interaction from a scheduled campaign email.
        Updates the scheduled campaign and vulnerability profile.
        """
        # Find the target by tracking token
        target = CampaignTarget.query.filter_by(tracking_token=tracking_token).first()
        if not target:
            return {'error': 'Invalid tracking token'}

        # Find the scheduled campaign
        scheduled = ScheduledCampaign.query.filter_by(target_id=target.id).first()
        if not scheduled:
            # This might be from a regular campaign, not a program
            return {'success': True, 'note': 'Not a program campaign'}

        now = datetime.utcnow()

        # Calculate time deltas
        if scheduled.sent_at:
            time_since_sent = (now - scheduled.sent_at).total_seconds()
        else:
            time_since_sent = None

        # Update scheduled campaign based on interaction
        if interaction_type == 'open':
            if not scheduled.email_opened:
                scheduled.email_opened = True
                scheduled.time_to_open_seconds = int(time_since_sent) if time_since_sent else None

        elif interaction_type == 'click':
            scheduled.email_opened = True  # Must have opened to click
            if not scheduled.link_clicked:
                scheduled.link_clicked = True
                scheduled.time_to_click_seconds = int(time_since_sent) if time_since_sent else None

        elif interaction_type == 'submit':
            scheduled.email_opened = True
            scheduled.link_clicked = True
            if not scheduled.credentials_submitted:
                scheduled.credentials_submitted = True
                scheduled.time_to_submit_seconds = int(time_since_sent) if time_since_sent else None

        elif interaction_type == 'report':
            scheduled.reported_as_phishing = True

        # Set context
        if device_type:
            scheduled.interaction_device = device_type

        scheduled.interaction_time_of_day = self._get_time_of_day(now)
        scheduled.interaction_day_of_week = now.strftime('%A')

        db.session.commit()

        # Update vulnerability profile
        result = self.vulnerability_analyzer.record_campaign_result(
            employee_id=scheduled.employee_id,
            template_id=scheduled.template_id,
            vector_type=scheduled.vector_type,
            difficulty_level=scheduled.difficulty_level,
            email_opened=scheduled.email_opened,
            link_clicked=scheduled.link_clicked,
            credentials_submitted=scheduled.credentials_submitted,
            reported_as_phishing=scheduled.reported_as_phishing,
            time_to_open_seconds=scheduled.time_to_open_seconds,
            time_to_click_seconds=scheduled.time_to_click_seconds,
            time_to_submit_seconds=scheduled.time_to_submit_seconds,
            device_type=device_type,
            program_id=scheduled.program_id,
            scheduled_campaign_id=scheduled.id
        )

        # If adaptive testing is enabled, potentially adjust future campaigns
        program = CampaignProgram.query.get(scheduled.program_id)
        if program and program.adapt_to_responses and scheduled.link_clicked:
            self._adapt_future_campaigns(scheduled, result['profile'])

        return {
            'success': True,
            'interaction': interaction_type,
            'profile_updated': True
        }

    def _adapt_future_campaigns(self, scheduled: ScheduledCampaign, profile: Dict):
        """
        Adapt future scheduled campaigns based on employee response.
        If they clicked, schedule more tests of that technique.
        """
        # Get remaining scheduled campaigns for this employee
        future_campaigns = ScheduledCampaign.query.filter(
            ScheduledCampaign.program_id == scheduled.program_id,
            ScheduledCampaign.employee_id == scheduled.employee_id,
            ScheduledCampaign.status == 'scheduled',
            ScheduledCampaign.scheduled_for > datetime.utcnow()
        ).order_by(ScheduledCampaign.scheduled_for).all()

        if not future_campaigns:
            return

        # If they failed on a technique, increase testing of that technique
        failed_technique = scheduled.technique_tested
        if failed_technique:
            # Find a future campaign and change its technique to the failed one
            for fc in future_campaigns:
                if fc.technique_tested != failed_technique:
                    fc.technique_tested = failed_technique
                    # Try to find a template for this technique
                    templates = CustomTemplate.query.filter_by(
                        technique_type=failed_technique,
                        is_active=True
                    ).all()
                    if templates:
                        fc.template_id = random.choice(templates).id
                    break  # Only change one

    def _get_time_of_day(self, dt: datetime) -> str:
        """Categorize time into morning/afternoon/evening/night"""
        hour = dt.hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    def get_program_stats(self, program_id: str) -> Dict:
        """Get comprehensive statistics for a program"""
        program = CampaignProgram.query.get(program_id)
        if not program:
            return {'error': 'Program not found'}

        # Get scheduled campaigns
        scheduled = ScheduledCampaign.query.filter_by(program_id=program_id).all()

        # Calculate stats
        total = len(scheduled)
        sent = sum(1 for s in scheduled if s.status == 'sent')
        pending = sum(1 for s in scheduled if s.status == 'scheduled')
        failed = sum(1 for s in scheduled if s.status == 'failed')

        # Interaction stats
        opened = sum(1 for s in scheduled if s.email_opened)
        clicked = sum(1 for s in scheduled if s.link_clicked)
        submitted = sum(1 for s in scheduled if s.credentials_submitted)
        reported = sum(1 for s in scheduled if s.reported_as_phishing)

        # Technique effectiveness
        technique_stats = {}
        for s in scheduled:
            if s.technique_tested:
                if s.technique_tested not in technique_stats:
                    technique_stats[s.technique_tested] = {'total': 0, 'clicked': 0}
                technique_stats[s.technique_tested]['total'] += 1
                if s.link_clicked:
                    technique_stats[s.technique_tested]['clicked'] += 1

        for technique in technique_stats:
            stats = technique_stats[technique]
            stats['click_rate'] = round((stats['clicked'] / stats['total'] * 100), 1) if stats['total'] > 0 else 0

        # Phase stats
        phases = ProgramPhase.query.filter_by(program_id=program_id).all()
        phase_stats = []
        for phase in phases:
            phase_scheduled = [s for s in scheduled if s.phase_id == phase.id]
            phase_stats.append({
                'phase_name': phase.name,
                'difficulty': phase.difficulty_level,
                'status': phase.status,
                'emails_scheduled': len(phase_scheduled),
                'emails_sent': sum(1 for s in phase_scheduled if s.status == 'sent'),
                'click_rate': round((sum(1 for s in phase_scheduled if s.link_clicked) / len(phase_scheduled) * 100), 1) if phase_scheduled else 0
            })

        return {
            'program': program.to_dict(),
            'summary': {
                'total_emails': total,
                'sent': sent,
                'pending': pending,
                'failed': failed,
                'opened': opened,
                'clicked': clicked,
                'credentials_submitted': submitted,
                'reported_correctly': reported,
                'open_rate': round((opened / sent * 100), 1) if sent > 0 else 0,
                'click_rate': round((clicked / sent * 100), 1) if sent > 0 else 0,
                'submission_rate': round((submitted / sent * 100), 1) if sent > 0 else 0
            },
            'technique_effectiveness': technique_stats,
            'phase_stats': phase_stats
        }

    def get_employee_program_history(self, employee_id: str, program_id: str = None) -> List[Dict]:
        """Get an employee's campaign history within a program"""
        query = ScheduledCampaign.query.filter_by(employee_id=employee_id)

        if program_id:
            query = query.filter_by(program_id=program_id)

        campaigns = query.order_by(ScheduledCampaign.scheduled_for.desc()).all()

        return [c.to_dict() for c in campaigns]
