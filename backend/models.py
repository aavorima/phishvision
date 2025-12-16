from datetime import datetime
from database import db
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User model for authentication and account management"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), default='user')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name or ''} {self.last_name or ''}".strip() or self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }


class Settings(db.Model):
    """Application settings including SMTP configuration"""
    __tablename__ = 'settings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # SMTP Configuration
    smtp_host = db.Column(db.String(200), nullable=True)
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(200), nullable=True)
    smtp_password = db.Column(db.String(500), nullable=True)  # Should be encrypted in production
    smtp_use_tls = db.Column(db.Boolean, default=True)
    smtp_from_email = db.Column(db.String(200), nullable=True)
    smtp_from_name = db.Column(db.String(200), nullable=True)

    # General Settings
    notification_email = db.Column(db.String(200), nullable=True)
    timezone = db.Column(db.String(50), default='UTC')

    # AI Settings
    gemini_api_key = db.Column(db.String(500), nullable=True)

    # Twilio SMS Configuration
    twilio_account_sid = db.Column(db.String(500), nullable=True)
    twilio_auth_token = db.Column(db.String(500), nullable=True)
    twilio_phone_number = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref='settings', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'smtp_password': '********' if self.smtp_password else None,  # Don't expose password
            'smtp_use_tls': self.smtp_use_tls,
            'smtp_from_email': self.smtp_from_email,
            'smtp_from_name': self.smtp_from_name,
            'notification_email': self.notification_email,
            'timezone': self.timezone,
            'gemini_api_key': '********' if self.gemini_api_key else None,
            'gemini_api_key_set': bool(self.gemini_api_key),
            'twilio_account_sid': '********' if self.twilio_account_sid else None,
            'twilio_auth_token': '********' if self.twilio_auth_token else None,
            'twilio_phone_number': self.twilio_phone_number,
            'twilio_configured': bool(self.twilio_account_sid and self.twilio_auth_token and self.twilio_phone_number),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # 'bank_alert' or 'package_delivery'
    subject = db.Column(db.String(200), nullable=False)
    target_emails = db.Column(db.Text, nullable=False)  # JSON array of emails
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    landing_page_id = db.Column(db.String(36), db.ForeignKey('landing_pages.id'), nullable=True)
    program_id = db.Column(db.String(36), db.ForeignKey('campaign_programs.id'), nullable=True)

    # Relationships
    targets = db.relationship('CampaignTarget', backref='campaign', lazy=True, cascade='all, delete-orphan')
    landing_page = db.relationship('LandingPage', backref='email_campaigns', lazy=True)
    program = db.relationship('CampaignProgram', backref='email_campaigns', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_type': self.template_type,
            'subject': self.subject,
            'target_emails': self.target_emails,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'landing_page_id': self.landing_page_id,
            'landing_page_name': self.landing_page.name if self.landing_page else None,
            'total_targets': len(self.targets),
            'opened_count': sum(1 for t in self.targets if t.opened_at),
            'clicked_count': sum(1 for t in self.targets if t.clicked_at)
        }

class CampaignTarget(db.Model):
    __tablename__ = 'campaign_targets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    tracking_token = db.Column(db.String(100), unique=True, nullable=False)

    # Tracking data
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'sent_at': self.sent_at.isoformat(),
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

class CustomTemplate(db.Model):
    __tablename__ = 'custom_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='general')  # IT, HR, Finance, Banking, etc.
    subject = db.Column(db.String(500), nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    from_name = db.Column(db.String(200), nullable=True)  # Sender display name (e.g., "Zoom Support Team")
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    description = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(10), default='EN')  # EN, AZ, etc.
    is_builtin = db.Column(db.Boolean, default=False)  # True for pre-loaded templates
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Psychological technique tagging for vulnerability profiling
    technique_type = db.Column(db.String(50), nullable=True)  # 'urgency', 'authority', 'curiosity', 'fear', 'reward', 'social_proof'
    target_demographic = db.Column(db.String(100), nullable=True)  # Optional: 'executives', 'new_hires', 'IT', etc.

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'subject': self.subject,
            'html_content': self.html_content,
            'from_name': self.from_name,
            'difficulty': self.difficulty,
            'description': self.description,
            'language': self.language,
            'is_builtin': self.is_builtin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            # Technique tagging
            'technique_type': self.technique_type,
            'target_demographic': self.target_demographic
        }

class EmailAnalysis(db.Model):
    __tablename__ = 'email_analyses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email_from = db.Column(db.String(200), nullable=False)
    email_subject = db.Column(db.String(500), nullable=False)
    email_body = db.Column(db.Text, nullable=False)
    headers = db.Column(db.Text, nullable=True)  # JSON string

    # Analysis results (NLP-based)
    risk_score = db.Column(db.Float, nullable=False)  # 0-100
    classification = db.Column(db.String(20), nullable=False)  # safe, suspicious, malicious

    # Detailed checks
    spf_status = db.Column(db.String(20), nullable=True)  # pass, fail, none
    dkim_status = db.Column(db.String(20), nullable=True)
    dmarc_status = db.Column(db.String(20), nullable=True)

    # NLP Analysis
    suspicious_keywords = db.Column(db.Text, nullable=True)  # JSON array
    url_analysis = db.Column(db.Text, nullable=True)  # JSON object
    sentiment_score = db.Column(db.Float, nullable=True)
    urgency_score = db.Column(db.Float, nullable=True)

    # Explanation
    explanation = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text, nullable=True)  # JSON array

    # AI Analysis fields (Gemini)
    ai_risk_score = db.Column(db.Float, nullable=True)  # AI-determined score
    ai_classification = db.Column(db.String(20), nullable=True)  # AI classification
    ai_reasoning = db.Column(db.Text, nullable=True)  # AI explanation
    ai_tactics_detected = db.Column(db.Text, nullable=True)  # JSON array of tactics
    ai_confidence = db.Column(db.Float, nullable=True)  # 0-1 confidence score

    # Hybrid Analysis results
    hybrid_risk_score = db.Column(db.Float, nullable=True)  # Combined NLP + AI score
    hybrid_classification = db.Column(db.String(20), nullable=True)  # Final classification
    analysis_method = db.Column(db.String(20), default='nlp')  # nlp, ai, hybrid

    # Zero-day detection
    is_novel_pattern = db.Column(db.Boolean, default=False)  # AI detected new pattern
    novel_pattern_description = db.Column(db.Text, nullable=True)  # Description of novel pattern

    # Language detection
    detected_language = db.Column(db.String(10), nullable=True)  # en, tr, az, etc.

    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email_from': self.email_from,
            'email_subject': self.email_subject,
            'email_body': self.email_body,
            'risk_score': self.risk_score,
            'classification': self.classification,
            'spf_status': self.spf_status,
            'dkim_status': self.dkim_status,
            'dmarc_status': self.dmarc_status,
            'suspicious_keywords': self.suspicious_keywords,
            'url_analysis': self.url_analysis,
            'sentiment_score': self.sentiment_score,
            'urgency_score': self.urgency_score,
            'explanation': self.explanation,
            'recommendations': self.recommendations,
            # AI Analysis
            'ai_risk_score': self.ai_risk_score,
            'ai_classification': self.ai_classification,
            'ai_reasoning': self.ai_reasoning,
            'ai_tactics_detected': self.ai_tactics_detected,
            'ai_confidence': self.ai_confidence,
            # Hybrid results
            'hybrid_risk_score': self.hybrid_risk_score,
            'hybrid_classification': self.hybrid_classification,
            'analysis_method': self.analysis_method,
            # Zero-day
            'is_novel_pattern': self.is_novel_pattern,
            'novel_pattern_description': self.novel_pattern_description,
            'detected_language': self.detected_language,
            'analyzed_at': self.analyzed_at.isoformat()
        }


class Employee(db.Model):
    """Employee model for managing organization's users/employees"""
    __tablename__ = 'employees'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(200), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    manager_email = db.Column(db.String(200), nullable=True)
    employee_id = db.Column(db.String(50), nullable=True)  # Internal employee ID
    is_active = db.Column(db.Boolean, default=True)
    tags = db.Column(db.Text, nullable=True)  # JSON array for custom tags/groups
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Demographic fields for vulnerability profiling
    age_group = db.Column(db.String(20), nullable=True)  # '18-25', '26-35', '36-45', '46-55', '56+'
    hire_date = db.Column(db.DateTime, nullable=True)
    tenure_months = db.Column(db.Integer, nullable=True)  # Auto-calculated from hire_date
    job_level = db.Column(db.String(20), nullable=True)  # 'entry', 'mid', 'senior', 'manager', 'executive'
    previous_training = db.Column(db.Boolean, default=False)
    last_training_date = db.Column(db.DateTime, nullable=True)

    # Human Vulnerability Score (HVS)
    hvs_score = db.Column(db.Integer, default=0)  # 0-100
    hvs_last_updated = db.Column(db.DateTime, nullable=True)

    def calculate_tenure(self):
        """Calculate tenure in months from hire date"""
        if self.hire_date:
            delta = datetime.utcnow() - self.hire_date
            self.tenure_months = int(delta.days / 30)
        return self.tenure_months

    def update_hvs(self, event_type, increment=True):
        """
        Update Human Vulnerability Score based on events

        Args:
            event_type: Type of event (see HVS_SCORE_CHANGES)
            increment: True to add points (bad behavior), False to subtract (good behavior)

        Returns:
            new_score: Updated HVS score
        """
        HVS_SCORE_CHANGES = {
            'clicked_link': 25,
            'submitted_credentials': 40,
            'clicked_sms': 20,
            'opened_email': 5,
            'watched_training': -15,
            'reported_phishing': -25
        }

        change = HVS_SCORE_CHANGES.get(event_type, 0)

        if not increment:
            change = -change

        # Update score (ensure it stays within 0-100 range)
        new_score = self.hvs_score + change
        self.hvs_score = max(0, min(100, new_score))
        self.hvs_last_updated = datetime.utcnow()

        # Create HVS event record
        from database import db
        hvs_event = HVSEvent(
            employee_id=self.id,
            event_type=event_type,
            score_change=change,
            score_before=self.hvs_score - change,
            score_after=self.hvs_score,
            event_time=datetime.utcnow()
        )
        db.session.add(hvs_event)

        return self.hvs_score

    def get_hvs_level(self):
        """Get HVS risk level"""
        if self.hvs_score >= 75:
            return 'critical'
        elif self.hvs_score >= 50:
            return 'high'
        elif self.hvs_score >= 25:
            return 'medium'
        else:
            return 'low'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'department': self.department,
            'job_title': self.job_title,
            'phone': self.phone,
            'manager_email': self.manager_email,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'tags': self.tags,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            # Demographic fields
            'age_group': self.age_group,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'tenure_months': self.tenure_months,
            'job_level': self.job_level,
            'previous_training': self.previous_training,
            'last_training_date': self.last_training_date.isoformat() if self.last_training_date else None,
            # HVS fields
            'hvs_score': self.hvs_score,
            'hvs_level': self.get_hvs_level(),
            'hvs_last_updated': self.hvs_last_updated.isoformat() if self.hvs_last_updated else None
        }


class HVSEvent(db.Model):
    """Track Human Vulnerability Score change events"""
    __tablename__ = 'hvs_events'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=False)

    # Event details
    event_type = db.Column(db.String(50), nullable=False)  # clicked_link, submitted_credentials, clicked_sms, opened_email, watched_training, reported_phishing
    score_change = db.Column(db.Integer, nullable=False)  # Can be positive or negative
    score_before = db.Column(db.Integer, nullable=False)
    score_after = db.Column(db.Integer, nullable=False)

    # Metadata
    campaign_id = db.Column(db.String(36), nullable=True)  # Related campaign if applicable
    event_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Relationship
    employee = db.relationship('Employee', backref='hvs_events', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'event_type': self.event_type,
            'score_change': self.score_change,
            'score_before': self.score_before,
            'score_after': self.score_after,
            'campaign_id': self.campaign_id,
            'event_time': self.event_time.isoformat(),
            'notes': self.notes
        }


class SecurityIncident(db.Model):
    """SOC Security Incident model for tracking phishing incidents and response timeline"""
    __tablename__ = 'security_incidents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = db.Column(db.String(50), nullable=False)  # phishing_click, credential_entered, malware_download, reported_email
    severity = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, critical
    description = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(200), nullable=True)
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=True)

    # Timeline tracking
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    contained_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default='detected')  # detected, investigating, contained, resolved
    response_notes = db.Column(db.Text, nullable=True)
    assigned_to = db.Column(db.String(200), nullable=True)

    # Relationships
    campaign = db.relationship('Campaign', backref='incidents', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'severity': self.severity,
            'description': self.description,
            'user_email': self.user_email,
            'campaign_id': self.campaign_id,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'contained_at': self.contained_at.isoformat() if self.contained_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'status': self.status,
            'response_notes': self.response_notes,
            'assigned_to': self.assigned_to,
            'response_time_minutes': self._calculate_response_time()
        }

    def _calculate_response_time(self):
        """Calculate time from detection to resolution in minutes"""
        if self.resolved_at and self.detected_at:
            delta = self.resolved_at - self.detected_at
            return round(delta.total_seconds() / 60, 2)
        return None


class LandingPage(db.Model):
    """Landing page templates for credential harvesting simulations"""
    __tablename__ = 'landing_pages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='general')  # microsoft, google, banking, corporate, custom
    description = db.Column(db.Text, nullable=True)

    # Page content
    html_content = db.Column(db.Text, nullable=False)  # The fake login page HTML
    redirect_url = db.Column(db.String(500), nullable=True)  # Where to redirect after "login"
    capture_fields = db.Column(db.Text, default='["username", "password"]')  # JSON array of field names to track

    # Cloning info (if cloned from real site)
    cloned_from_url = db.Column(db.String(500), nullable=True)
    cloned_at = db.Column(db.DateTime, nullable=True)

    # Settings
    is_builtin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'html_content': self.html_content,
            'redirect_url': self.redirect_url,
            'capture_fields': self.capture_fields,
            'cloned_from_url': self.cloned_from_url,
            'cloned_at': self.cloned_at.isoformat() if self.cloned_at else None,
            'is_builtin': self.is_builtin,
            'is_active': self.is_active,
            'difficulty': self.difficulty,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class CredentialCapture(db.Model):
    """Track credential submission events (NOT actual credentials - just the event)"""
    __tablename__ = 'credential_captures'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False)
    target_id = db.Column(db.String(36), db.ForeignKey('campaign_targets.id'), nullable=False)
    landing_page_id = db.Column(db.String(36), db.ForeignKey('landing_pages.id'), nullable=True)

    # Track the event (NOT the actual credentials)
    email = db.Column(db.String(200), nullable=False)
    fields_submitted = db.Column(db.Text, nullable=True)  # JSON: ["username", "password"] - which fields were filled
    submission_count = db.Column(db.Integer, default=1)  # How many times they tried

    # Metadata
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    campaign = db.relationship('Campaign', backref='credential_captures', lazy=True)
    target = db.relationship('CampaignTarget', backref='credential_captures', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'target_id': self.target_id,
            'landing_page_id': self.landing_page_id,
            'email': self.email,
            'fields_submitted': self.fields_submitted,
            'submission_count': self.submission_count,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'submitted_at': self.submitted_at.isoformat()
        }


class QRCodeCampaign(db.Model):
    """QR Code Phishing (Quishing) campaigns"""
    __tablename__ = 'qrcode_campaigns'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # QR Code settings
    target_url = db.Column(db.String(500), nullable=False)  # The URL encoded in QR
    landing_page_id = db.Column(db.String(36), db.ForeignKey('landing_pages.id'), nullable=True)
    program_id = db.Column(db.String(36), db.ForeignKey('campaign_programs.id'), nullable=True)
    qr_image_path = db.Column(db.String(500), nullable=True)  # Path to generated QR image

    # Campaign settings
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    placement_location = db.Column(db.String(200), nullable=True)  # Where QR will be placed (office, poster, etc.)

    # Stats
    total_scans = db.Column(db.Integer, default=0)
    unique_scans = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    landing_page = db.relationship('LandingPage', backref='qr_campaigns', lazy=True)
    program = db.relationship('CampaignProgram', backref='qr_campaigns', lazy=True)
    scans = db.relationship('QRCodeScan', backref='campaign', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_url': self.target_url,
            'landing_page_id': self.landing_page_id,
            'qr_image_path': self.qr_image_path,
            'status': self.status,
            'placement_location': self.placement_location,
            'total_scans': self.total_scans,
            'unique_scans': self.unique_scans,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


class QRCodeScan(db.Model):
    """Track individual QR code scans"""
    __tablename__ = 'qrcode_scans'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('qrcode_campaigns.id'), nullable=False)

    # Scan info
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    device_type = db.Column(db.String(50), nullable=True)  # mobile, tablet, desktop

    # Optional user identification (if they proceed to login)
    email = db.Column(db.String(200), nullable=True)
    submitted_credentials = db.Column(db.Boolean, default=False)

    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_type': self.device_type,
            'email': self.email,
            'submitted_credentials': self.submitted_credentials,
            'scanned_at': self.scanned_at.isoformat()
        }


class SMSCampaign(db.Model):
    """SMS Phishing (Smishing) campaigns"""
    __tablename__ = 'sms_campaigns'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # SMS content
    message_template = db.Column(db.Text, nullable=False)  # SMS message with {{variables}}
    sender_id = db.Column(db.String(50), nullable=True)  # Sender name/number displayed

    # Target link
    target_url = db.Column(db.String(500), nullable=False)  # Shortened tracking URL
    landing_page_id = db.Column(db.String(36), db.ForeignKey('landing_pages.id'), nullable=True)
    program_id = db.Column(db.String(36), db.ForeignKey('campaign_programs.id'), nullable=True)

    # Campaign settings
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, active, completed
    scheduled_at = db.Column(db.DateTime, nullable=True)

    # Stats
    total_sent = db.Column(db.Integer, default=0)
    total_delivered = db.Column(db.Integer, default=0)
    total_clicked = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    targets = db.relationship('SMSTarget', backref='campaign', lazy=True, cascade='all, delete-orphan')
    program = db.relationship('CampaignProgram', backref='sms_campaigns', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'message_template': self.message_template,
            'sender_id': self.sender_id,
            'target_url': self.target_url,
            'landing_page_id': self.landing_page_id,
            'status': self.status,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'total_sent': self.total_sent,
            'total_delivered': self.total_delivered,
            'total_clicked': self.total_clicked,
            'target_count': len(self.targets),
            'sent_count': self.total_sent,
            'clicked_count': self.total_clicked,
            'created_at': self.created_at.isoformat()
        }


class SMSTarget(db.Model):
    """Individual SMS recipients"""
    __tablename__ = 'sms_targets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('sms_campaigns.id'), nullable=False)

    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(200), nullable=True)  # Optional, for linking to user
    tracking_token = db.Column(db.String(100), unique=True, nullable=False)

    # Status tracking
    sent_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)

    # Metadata
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'phone_number': self.phone_number,
            'email': self.email,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }


class UserRiskScore(db.Model):
    """User risk scoring based on phishing susceptibility"""
    __tablename__ = 'user_risk_scores'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(200), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=True)

    # Risk metrics
    risk_score = db.Column(db.Float, default=50.0)  # 0-100 (higher = more risky)
    risk_level = db.Column(db.String(20), default='medium')  # low, medium, high, critical

    # Campaign statistics
    campaigns_received = db.Column(db.Integer, default=0)
    campaigns_opened = db.Column(db.Integer, default=0)
    campaigns_clicked = db.Column(db.Integer, default=0)

    # Repeat Offender Tracking (NEW)
    is_repeat_offender = db.Column(db.Boolean, default=False)  # Flagged if clicked 3+ times
    consecutive_failures = db.Column(db.Integer, default=0)  # Track streak of failures
    total_credential_submissions = db.Column(db.Integer, default=0)  # Entered creds on fake page
    requires_training = db.Column(db.Boolean, default=False)  # Auto-assigned mandatory training
    manager_notified = db.Column(db.Boolean, default=False)  # Has manager been notified

    # Training statistics
    training_completed = db.Column(db.Integer, default=0)
    training_passed = db.Column(db.Integer, default=0)

    # Timestamps
    last_incident_at = db.Column(db.DateTime, nullable=True)
    last_training_at = db.Column(db.DateTime, nullable=True)
    last_click_at = db.Column(db.DateTime, nullable=True)  # Track most recent failure
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'department': self.department,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'campaigns_received': self.campaigns_received,
            'campaigns_opened': self.campaigns_opened,
            'campaigns_clicked': self.campaigns_clicked,
            # Repeat offender tracking
            'is_repeat_offender': self.is_repeat_offender,
            'consecutive_failures': self.consecutive_failures,
            'total_credential_submissions': self.total_credential_submissions,
            'requires_training': self.requires_training,
            'manager_notified': self.manager_notified,
            # Training stats
            'training_completed': self.training_completed,
            'training_passed': self.training_passed,
            'last_incident_at': self.last_incident_at.isoformat() if self.last_incident_at else None,
            'last_training_at': self.last_training_at.isoformat() if self.last_training_at else None,
            'last_click_at': self.last_click_at.isoformat() if self.last_click_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'open_rate': round((self.campaigns_opened / self.campaigns_received * 100), 1) if self.campaigns_received > 0 else 0,
            'click_rate': round((self.campaigns_clicked / self.campaigns_received * 100), 1) if self.campaigns_received > 0 else 0
        }

    def record_click(self):
        """Record a phishing click and update repeat offender status"""
        self.campaigns_clicked += 1
        self.consecutive_failures += 1
        self.last_click_at = datetime.utcnow()
        self.last_incident_at = datetime.utcnow()

        # Flag as repeat offender if clicked 3+ times
        if self.campaigns_clicked >= 3:
            self.is_repeat_offender = True
            self.requires_training = True

        self.calculate_risk_score()

    def record_credential_submission(self):
        """Record when user enters credentials on fake landing page"""
        self.total_credential_submissions += 1
        self.consecutive_failures += 1

        # Credential submission is severe - immediately flag
        if self.total_credential_submissions >= 2:
            self.is_repeat_offender = True
            self.requires_training = True

        self.calculate_risk_score()

    def record_training_pass(self):
        """Record successful training completion - reduces risk"""
        self.training_completed += 1
        self.training_passed += 1
        self.last_training_at = datetime.utcnow()
        self.consecutive_failures = 0  # Reset streak after training

        # Remove training requirement if completed
        if self.requires_training:
            self.requires_training = False

        self.calculate_risk_score()

    def calculate_risk_score(self):
        """Calculate risk score based on user behavior"""
        # Handle None or 0 values
        if not self.campaigns_received:
            self.risk_score = 50.0  # Neutral for new users
            self.risk_level = 'medium'
            return

        # Ensure values are not None before calculation
        clicked = self.campaigns_clicked or 0
        opened = self.campaigns_opened or 0

        # Calculate rates
        click_rate = (clicked / self.campaigns_received) * 100
        open_rate = (opened / self.campaigns_received) * 100

        # Weighted score (clicking is worse than just opening)
        base_score = (click_rate * 0.7) + (open_rate * 0.3)

        # REPEAT OFFENDER PENALTY: Add penalty for serial clickers
        if self.is_repeat_offender:
            base_score += 15  # +15 penalty for repeat offenders

        # Credential submission is severe
        total_creds = self.total_credential_submissions or 0
        if total_creds > 0:
            base_score += (total_creds * 10)  # +10 per submission

        # Consecutive failure streak penalty
        consecutive = self.consecutive_failures or 0
        if consecutive >= 3:
            base_score += (consecutive * 3)  # +3 per consecutive failure

        # Training bonus (reduce risk if user completed training)
        training_completed = self.training_completed or 0
        training_passed = self.training_passed or 0
        if training_completed > 0:
            training_factor = min(training_passed / training_completed, 1.0)
            base_score = base_score * (1 - (training_factor * 0.25))  # Up to 25% reduction

        # Clamp to 0-100
        self.risk_score = max(0, min(100, base_score))

        # Set risk level
        if self.risk_score < 25:
            self.risk_level = 'low'
        elif self.risk_score < 50:
            self.risk_level = 'medium'
        elif self.risk_score < 75:
            self.risk_level = 'high'
        else:
            self.risk_level = 'critical'


class AnalysisFeedback(db.Model):
    """User feedback on email analysis accuracy for self-learning system"""
    __tablename__ = 'analysis_feedback'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('email_analyses.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Original analysis result
    original_classification = db.Column(db.String(20), nullable=False)  # safe, suspicious, malicious
    original_risk_score = db.Column(db.Float, nullable=False)

    # User correction
    user_classification = db.Column(db.String(20), nullable=False)  # safe, suspicious, malicious
    feedback_type = db.Column(db.String(30), nullable=False)  # false_positive, false_negative, correct

    # Additional context
    user_notes = db.Column(db.Text, nullable=True)  # Why user thinks it's wrong
    confidence = db.Column(db.String(20), default='medium')  # low, medium, high

    # For learning
    is_processed = db.Column(db.Boolean, default=False)  # Has this been used for learning
    learned_pattern_id = db.Column(db.String(36), nullable=True)  # If a pattern was created from this

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    analysis = db.relationship('EmailAnalysis', backref='feedback', lazy=True)
    user = db.relationship('User', backref='feedback', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'user_id': self.user_id,
            'original_classification': self.original_classification,
            'original_risk_score': self.original_risk_score,
            'user_classification': self.user_classification,
            'feedback_type': self.feedback_type,
            'user_notes': self.user_notes,
            'confidence': self.confidence,
            'is_processed': self.is_processed,
            'learned_pattern_id': self.learned_pattern_id,
            'created_at': self.created_at.isoformat()
        }


class PhishingPattern(db.Model):
    """Learned phishing patterns for few-shot learning with Gemini AI"""
    __tablename__ = 'phishing_patterns'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Pattern identification
    pattern_type = db.Column(db.String(50), nullable=False)
    # Types: social_engineering, credential_theft, bec, spear_phishing,
    #        delivery_scam, tech_support_scam, reward_scam, brand_impersonation

    # Pattern content (for few-shot learning)
    example_subject = db.Column(db.String(500), nullable=True)
    example_body_snippet = db.Column(db.Text, nullable=True)  # Sanitized snippet (no PII)
    example_sender_pattern = db.Column(db.String(200), nullable=True)  # e.g., *@suspicious-domain.com

    # Pattern characteristics (JSON)
    indicators = db.Column(db.Text, nullable=False)  # JSON array of indicators
    # Example: ["urgency_tactics", "credential_request", "fake_deadline", "brand_spoof"]

    tactics = db.Column(db.Text, nullable=True)  # JSON: Social engineering tactics used
    # Example: {"authority": true, "urgency": true, "scarcity": false, "fear": true}

    # Classification hints for Gemini
    classification_hints = db.Column(db.Text, nullable=True)  # JSON hints for AI

    # Effectiveness tracking
    detection_count = db.Column(db.Integer, default=0)  # Times this pattern helped detect phishing
    false_positive_count = db.Column(db.Integer, default=0)  # Times it wrongly flagged safe email
    false_negative_count = db.Column(db.Integer, default=0)  # Times it missed phishing
    effectiveness_score = db.Column(db.Float, default=50.0)  # 0-100 (higher = more effective)

    # Source tracking
    source = db.Column(db.String(50), nullable=False)  # user_feedback, ai_generated, threat_intel, manual
    source_feedback_id = db.Column(db.String(36), nullable=True)  # Link to feedback that created it

    # Language support
    language = db.Column(db.String(10), default='multi')  # en, tr, az, multi (for any language)

    # Status
    is_active = db.Column(db.Boolean, default=True)
    confidence_level = db.Column(db.String(20), default='medium')  # low, medium, high

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pattern_type': self.pattern_type,
            'example_subject': self.example_subject,
            'example_body_snippet': self.example_body_snippet,
            'example_sender_pattern': self.example_sender_pattern,
            'indicators': self.indicators,
            'tactics': self.tactics,
            'classification_hints': self.classification_hints,
            'detection_count': self.detection_count,
            'false_positive_count': self.false_positive_count,
            'false_negative_count': self.false_negative_count,
            'effectiveness_score': self.effectiveness_score,
            'source': self.source,
            'source_feedback_id': self.source_feedback_id,
            'language': self.language,
            'is_active': self.is_active,
            'confidence_level': self.confidence_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def record_detection(self):
        """Record successful detection using this pattern"""
        self.detection_count += 1
        self._update_effectiveness()

    def record_false_positive(self):
        """Record false positive - pattern wrongly flagged safe email"""
        self.false_positive_count += 1
        self._update_effectiveness()

    def record_false_negative(self):
        """Record false negative - pattern missed phishing"""
        self.false_negative_count += 1
        self._update_effectiveness()

    def _update_effectiveness(self):
        """Recalculate effectiveness score based on performance"""
        total = self.detection_count + self.false_positive_count + self.false_negative_count
        if total == 0:
            self.effectiveness_score = 50.0
            return

        # Success rate with penalties for false positives/negatives
        success_rate = self.detection_count / total
        fp_penalty = (self.false_positive_count / total) * 0.3  # FPs are annoying
        fn_penalty = (self.false_negative_count / total) * 0.5  # FNs are dangerous

        self.effectiveness_score = max(0, min(100, (success_rate - fp_penalty - fn_penalty) * 100))

        # Deactivate very ineffective patterns
        if self.effectiveness_score < 10 and total > 10:
            self.is_active = False


# =============================================================================
# COMMUNITY THREAT INTELLIGENCE MODELS
# =============================================================================

class ThreatEntry(db.Model):
    """Public threat intelligence entry - contains extracted IOCs only (no PII)
    Similar to VirusTotal/URLScan.io for email phishing analysis
    """
    __tablename__ = 'threat_entries'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Unique threat hash for deduplication (SHA256 of normalized IOCs)
    threat_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)

    # Short ID for public URLs (like URLScan.io: "abc123def")
    short_id = db.Column(db.String(12), unique=True, nullable=False, index=True)

    # Link to original analysis (private, nullable for anonymous submissions)
    source_analysis_id = db.Column(db.String(36), db.ForeignKey('email_analyses.id'), nullable=True)
    submitter_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Submission metadata
    is_anonymous = db.Column(db.Boolean, default=False)
    submission_source = db.Column(db.String(50), default='web')  # web, extension, api

    # Classification (copied from analysis)
    risk_score = db.Column(db.Float, nullable=False)
    classification = db.Column(db.String(20), nullable=False)  # safe, suspicious, malicious

    # Redacted subject (brand names kept, personal info removed)
    sanitized_subject = db.Column(db.String(500), nullable=True)

    # Detected tactics/patterns
    detected_tactics = db.Column(db.Text, nullable=True)  # JSON array
    detected_brands = db.Column(db.Text, nullable=True)  # JSON array of impersonated brands
    threat_type = db.Column(db.String(50), nullable=True)  # credential_theft, bec, delivery_scam, etc.

    # Statistics
    view_count = db.Column(db.Integer, default=0)
    community_votes_phishing = db.Column(db.Integer, default=0)
    community_votes_safe = db.Column(db.Integer, default=0)
    similar_submissions = db.Column(db.Integer, default=1)  # Count of duplicate submissions

    # Timestamps
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    source_analysis = db.relationship('EmailAnalysis', backref='threat_entry', lazy=True)
    submitter = db.relationship('User', backref='threat_submissions', lazy=True)
    iocs = db.relationship('ThreatIOC', backref='threat_entry', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('ThreatVote', backref='threat_entry', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_iocs=False, include_submitter=False):
        """Convert to dictionary
        Args:
            include_iocs: Include full IOC list (for authenticated users)
            include_submitter: Include submitter info (for authenticated users, non-anonymous)
        """
        import json
        result = {
            'id': self.id,
            'short_id': self.short_id,
            'risk_score': self.risk_score,
            'classification': self.classification,
            'sanitized_subject': self.sanitized_subject,
            'threat_type': self.threat_type,
            'detected_brands': json.loads(self.detected_brands) if self.detected_brands else [],
            'ioc_count': len(self.iocs),
            'view_count': self.view_count,
            'community_votes': {
                'phishing': self.community_votes_phishing,
                'safe': self.community_votes_safe
            },
            'similar_count': self.similar_submissions,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'submitter': 'Anonymous'
        }

        if include_iocs:
            result['iocs'] = [ioc.to_dict() for ioc in self.iocs]
            result['detected_tactics'] = json.loads(self.detected_tactics) if self.detected_tactics else []

        if include_submitter and not self.is_anonymous and self.submitter:
            result['submitter'] = self.submitter.username

        return result

    def to_public_dict(self):
        """Minimal dict for public feed (unauthenticated users)"""
        import json
        return {
            'short_id': self.short_id,
            'classification': self.classification,
            'risk_score': self.risk_score,
            'sanitized_subject': self.sanitized_subject,
            'threat_type': self.threat_type,
            'detected_brands': json.loads(self.detected_brands) if self.detected_brands else [],
            'ioc_count': len(self.iocs),
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'submitter': 'Anonymous'
        }

    def increment_view(self):
        """Increment view count"""
        self.view_count += 1


class ThreatIOC(db.Model):
    """Individual IOC (Indicator of Compromise) extracted from threat entry"""
    __tablename__ = 'threat_iocs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    threat_entry_id = db.Column(db.String(36), db.ForeignKey('threat_entries.id'), nullable=False)

    # IOC details
    ioc_type = db.Column(db.String(30), nullable=False)  # domain, ip, url, email_pattern, sender_domain
    ioc_value = db.Column(db.String(2000), nullable=False)  # The actual IOC (defanged)
    ioc_hash = db.Column(db.String(64), nullable=False, index=True)  # SHA256 of ioc_value for fast lookups

    # Context
    context = db.Column(db.String(100), nullable=True)  # e.g., "found in body", "sender domain"
    is_defanged = db.Column(db.Boolean, default=True)  # hxxp:// instead of http://

    # Risk assessment for this specific IOC
    ioc_risk_score = db.Column(db.Float, nullable=True)

    # Frequency tracking
    global_occurrence_count = db.Column(db.Integer, default=1)  # How many times seen across all threats

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.ioc_type,
            'value': self.ioc_value,
            'context': self.context,
            'is_defanged': self.is_defanged,
            'risk_score': self.ioc_risk_score,
            'occurrence_count': self.global_occurrence_count
        }


class ThreatVote(db.Model):
    """Community votes on threat entries"""
    __tablename__ = 'threat_votes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    threat_entry_id = db.Column(db.String(36), db.ForeignKey('threat_entries.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    vote_type = db.Column(db.String(20), nullable=False)  # 'phishing' or 'safe'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='threat_votes', lazy=True)

    # Unique constraint - one vote per user per threat
    __table_args__ = (
        db.UniqueConstraint('threat_entry_id', 'user_id', name='unique_user_vote'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'threat_entry_id': self.threat_entry_id,
            'user_id': self.user_id,
            'vote_type': self.vote_type,
            'created_at': self.created_at.isoformat()
        }


# =============================================================================
# VULNERABILITY PROFILING MODELS
# =============================================================================

class CampaignProgram(db.Model):
    """
    Month-long vulnerability profiling program.
    Contains multiple phases with scheduled campaigns to systematically
    profile employee vulnerabilities across different techniques and vectors.
    """
    __tablename__ = 'campaign_programs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Program configuration
    duration_days = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, active, paused, completed

    # Techniques and vectors to test (JSON arrays)
    techniques_to_test = db.Column(db.Text, nullable=True)  # JSON: ['urgency', 'authority', 'fear', ...]
    vectors_to_test = db.Column(db.Text, nullable=True)  # JSON: ['email', 'qr', 'sms']
    difficulty_levels = db.Column(db.Text, nullable=True)  # JSON: ['easy', 'medium', 'hard', 'expert']

    # Scheduling configuration
    emails_per_week_per_user = db.Column(db.Integer, default=2)
    randomize_timing = db.Column(db.Boolean, default=True)
    min_days_between_emails = db.Column(db.Integer, default=2)  # Minimum spacing between emails to same user

    # Targeting
    target_all_employees = db.Column(db.Boolean, default=False)
    target_departments = db.Column(db.Text, nullable=True)  # JSON array of departments
    target_employee_ids = db.Column(db.Text, nullable=True)  # JSON array of specific employee IDs

    # Progressive difficulty
    use_progressive_difficulty = db.Column(db.Boolean, default=True)
    adapt_to_responses = db.Column(db.Boolean, default=True)  # Adjust future emails based on responses

    # Timing
    scheduled_start = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    ends_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Statistics (cached for performance)
    total_emails_scheduled = db.Column(db.Integer, default=0)
    total_emails_sent = db.Column(db.Integer, default=0)
    total_employees_targeted = db.Column(db.Integer, default=0)

    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    phases = db.relationship('ProgramPhase', backref='program', lazy=True, cascade='all, delete-orphan')
    scenarios = db.relationship('ProgramScenario', backref='program', lazy=True, cascade='all, delete-orphan')
    scheduled_campaigns = db.relationship('ScheduledCampaign', backref='program', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_programs', lazy=True)

    def to_dict(self, include_phases=False):
        import json
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration_days': self.duration_days,
            'status': self.status,
            'techniques_to_test': json.loads(self.techniques_to_test) if self.techniques_to_test else [],
            'vectors_to_test': json.loads(self.vectors_to_test) if self.vectors_to_test else [],
            'difficulty_levels': json.loads(self.difficulty_levels) if self.difficulty_levels else [],
            'emails_per_week_per_user': self.emails_per_week_per_user,
            'randomize_timing': self.randomize_timing,
            'min_days_between_emails': self.min_days_between_emails,
            'target_all_employees': self.target_all_employees,
            'target_departments': json.loads(self.target_departments) if self.target_departments else [],
            'use_progressive_difficulty': self.use_progressive_difficulty,
            'adapt_to_responses': self.adapt_to_responses,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ends_at': self.ends_at.isoformat() if self.ends_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_emails_scheduled': self.total_emails_scheduled,
            'total_emails_sent': self.total_emails_sent,
            'total_employees_targeted': self.total_employees_targeted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_phases:
            result['phases'] = [p.to_dict() for p in self.phases]
        return result


class ProgramScenario(db.Model):
    """
    Defines a specific phishing scenario within a program.
    A scenario represents a unique combination of attack vector, technique, and template.
    Multiple scenarios can be created for a single program, allowing different
    employees to receive different types of simulations.
    """
    __tablename__ = 'program_scenarios'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    program_id = db.Column(db.String(36), db.ForeignKey('campaign_programs.id'), nullable=False)

    # Scenario identification
    name = db.Column(db.String(200), nullable=False)  # e.g., "Finance Urgent CEO Request"
    description = db.Column(db.Text, nullable=True)

    # Scenario configuration
    channel = db.Column(db.String(20), nullable=False)  # email, sms, qr, voice
    technique = db.Column(db.String(50), nullable=False)  # urgency, authority, fear, curiosity, reward, social_proof
    template_id = db.Column(db.String(36), db.ForeignKey('custom_templates.id'), nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=True)  # easy, medium, hard, expert

    # Scheduling
    schedule_type = db.Column(db.String(20), default='immediate')  # immediate, specific_datetime, relative
    scheduled_datetime = db.Column(db.DateTime, nullable=True)  # For specific_datetime
    relative_days = db.Column(db.Integer, nullable=True)  # For relative (days from program start)
    relative_hours = db.Column(db.Integer, nullable=True)  # Additional hours offset

    # Statistics (cached)
    total_assigned = db.Column(db.Integer, default=0)  # How many employees assigned to this scenario
    total_sent = db.Column(db.Integer, default=0)
    total_opened = db.Column(db.Integer, default=0)
    total_clicked = db.Column(db.Integer, default=0)
    total_submitted = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = db.relationship('CustomTemplate', backref='program_scenarios', lazy=True)
    assignments = db.relationship('ScenarioAssignment', backref='scenario', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'program_id': self.program_id,
            'name': self.name,
            'description': self.description,
            'channel': self.channel,
            'technique': self.technique,
            'template_id': self.template_id,
            'difficulty_level': self.difficulty_level,
            'schedule_type': self.schedule_type,
            'scheduled_datetime': self.scheduled_datetime.isoformat() if self.scheduled_datetime else None,
            'relative_days': self.relative_days,
            'relative_hours': self.relative_hours,
            'total_assigned': self.total_assigned,
            'total_sent': self.total_sent,
            'total_opened': self.total_opened,
            'total_clicked': self.total_clicked,
            'total_submitted': self.total_submitted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ScenarioAssignment(db.Model):
    """
    Maps employees to specific scenarios.
    Allows fine-grained control over which employees receive which phishing scenarios.
    Supports assignment by individual employee, department, or rule-based criteria.
    """
    __tablename__ = 'scenario_assignments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id = db.Column(db.String(36), db.ForeignKey('program_scenarios.id'), nullable=False)

    # Assignment targeting (at least one must be set)
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=True)  # Specific employee
    department = db.Column(db.String(100), nullable=True)  # Department name

    # Rule-based assignment (JSON)
    # e.g., {"risk_level": "high"}, {"hvs_score_min": 70}, {"previous_failures": 3}
    assignment_rule = db.Column(db.Text, nullable=True)  # JSON criteria

    # Scheduling override (optional - overrides scenario schedule for this assignment)
    custom_scheduled_time = db.Column(db.DateTime, nullable=True)

    # Execution tracking
    status = db.Column(db.String(20), default='pending')  # pending, scheduled, sent, failed, cancelled
    scheduled_campaign_id = db.Column(db.String(36), db.ForeignKey('scheduled_campaigns.id'), nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = db.relationship('Employee', backref='scenario_assignments', lazy=True)
    scheduled_campaign = db.relationship('ScheduledCampaign', backref='scenario_assignment', lazy=True)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'scenario_id': self.scenario_id,
            'employee_id': self.employee_id,
            'department': self.department,
            'assignment_rule': json.loads(self.assignment_rule) if self.assignment_rule else None,
            'custom_scheduled_time': self.custom_scheduled_time.isoformat() if self.custom_scheduled_time else None,
            'status': self.status,
            'scheduled_campaign_id': self.scheduled_campaign_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ProgramPhase(db.Model):
    """
    A phase within a campaign program (e.g., Week 1 - Baseline, Week 2 - Intermediate).
    Each phase has specific difficulty and technique focus.
    """
    __tablename__ = 'program_phases'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    program_id = db.Column(db.String(36), db.ForeignKey('campaign_programs.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)  # e.g., "Week 1 - Baseline"
    description = db.Column(db.Text, nullable=True)
    phase_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4...

    # Phase configuration
    difficulty_level = db.Column(db.String(20), default='easy')  # easy, medium, hard, expert
    techniques_focus = db.Column(db.Text, nullable=True)  # JSON: techniques to test in this phase
    vectors_focus = db.Column(db.Text, nullable=True)  # JSON: vectors to use in this phase

    # Timing (relative to program start)
    start_day = db.Column(db.Integer, default=0)  # Day 0 = program start
    duration_days = db.Column(db.Integer, default=7)

    # Status
    status = db.Column(db.String(20), default='pending')  # pending, active, completed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'program_id': self.program_id,
            'name': self.name,
            'description': self.description,
            'phase_number': self.phase_number,
            'difficulty_level': self.difficulty_level,
            'techniques_focus': json.loads(self.techniques_focus) if self.techniques_focus else [],
            'vectors_focus': json.loads(self.vectors_focus) if self.vectors_focus else [],
            'start_day': self.start_day,
            'duration_days': self.duration_days,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class ScheduledCampaign(db.Model):
    """
    Individual scheduled email/campaign within a program.
    Links to the underlying Campaign/Template but tracks program-specific metadata.
    """
    __tablename__ = 'scheduled_campaigns'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    program_id = db.Column(db.String(36), db.ForeignKey('campaign_programs.id'), nullable=False)
    phase_id = db.Column(db.String(36), db.ForeignKey('program_phases.id'), nullable=True)
    scenario_id = db.Column(db.String(36), db.ForeignKey('program_scenarios.id'), nullable=True)  # Scenario-based scheduling
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=False)
    template_id = db.Column(db.String(36), db.ForeignKey('custom_templates.id'), nullable=False)

    # When linked to actual campaign (after sending)
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=True)
    target_id = db.Column(db.String(36), db.ForeignKey('campaign_targets.id'), nullable=True)

    # Scheduling
    scheduled_for = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, sent, failed, cancelled

    # Testing metadata
    technique_tested = db.Column(db.String(50), nullable=True)  # Which technique this tests
    vector_type = db.Column(db.String(20), default='email')  # email, qr, sms
    difficulty_level = db.Column(db.String(20), default='medium')

    # Results (populated after interaction)
    email_opened = db.Column(db.Boolean, default=False)
    link_clicked = db.Column(db.Boolean, default=False)
    credentials_submitted = db.Column(db.Boolean, default=False)
    reported_as_phishing = db.Column(db.Boolean, default=False)  # Good behavior!

    # Timing metrics
    time_to_open_seconds = db.Column(db.Integer, nullable=True)
    time_to_click_seconds = db.Column(db.Integer, nullable=True)
    time_to_submit_seconds = db.Column(db.Integer, nullable=True)

    # Context when interaction occurred
    interaction_device = db.Column(db.String(20), nullable=True)  # desktop, mobile, tablet
    interaction_time_of_day = db.Column(db.String(20), nullable=True)  # morning, afternoon, evening, night
    interaction_day_of_week = db.Column(db.String(10), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    employee = db.relationship('Employee', backref='scheduled_campaigns', lazy=True)
    template = db.relationship('CustomTemplate', backref='scheduled_campaigns', lazy=True)
    campaign = db.relationship('Campaign', backref='scheduled_entries', lazy=True)
    target = db.relationship('CampaignTarget', backref='scheduled_entry', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'program_id': self.program_id,
            'phase_id': self.phase_id,
            'employee_id': self.employee_id,
            'template_id': self.template_id,
            'campaign_id': self.campaign_id,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'technique_tested': self.technique_tested,
            'vector_type': self.vector_type,
            'difficulty_level': self.difficulty_level,
            'email_opened': self.email_opened,
            'link_clicked': self.link_clicked,
            'credentials_submitted': self.credentials_submitted,
            'reported_as_phishing': self.reported_as_phishing,
            'time_to_open_seconds': self.time_to_open_seconds,
            'time_to_click_seconds': self.time_to_click_seconds,
            'time_to_submit_seconds': self.time_to_submit_seconds,
            'interaction_device': self.interaction_device,
            'interaction_time_of_day': self.interaction_time_of_day,
            'interaction_day_of_week': self.interaction_day_of_week,
            'created_at': self.created_at.isoformat()
        }


class VulnerabilityProfile(db.Model):
    """
    Comprehensive vulnerability profile for an employee.
    Tracks susceptibility to different attack vectors and psychological techniques.
    Updated after each campaign interaction.
    """
    __tablename__ = 'vulnerability_profiles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=False, unique=True)

    # Overall vulnerability score (0-100, higher = more vulnerable)
    overall_vulnerability_score = db.Column(db.Float, default=50.0)
    risk_level = db.Column(db.String(20), default='medium')  # low, medium, high, critical

    # Attack vector vulnerability scores (0-100 each)
    email_phishing_score = db.Column(db.Float, default=50.0)
    spear_phishing_score = db.Column(db.Float, default=50.0)
    qr_phishing_score = db.Column(db.Float, default=50.0)
    sms_phishing_score = db.Column(db.Float, default=50.0)

    # Psychological technique susceptibility scores (0-100 each)
    urgency_susceptibility = db.Column(db.Float, default=50.0)      # "Act now!" tactics
    authority_susceptibility = db.Column(db.Float, default=50.0)    # "CEO needs this"
    curiosity_susceptibility = db.Column(db.Float, default=50.0)    # "You won't believe..."
    fear_susceptibility = db.Column(db.Float, default=50.0)         # "Account suspended"
    reward_susceptibility = db.Column(db.Float, default=50.0)       # "You've won!"
    social_proof_susceptibility = db.Column(db.Float, default=50.0) # "Everyone is doing..."

    # Behavioral metrics
    avg_click_time_seconds = db.Column(db.Float, nullable=True)  # How fast they click (faster = more impulsive)
    avg_response_time_seconds = db.Column(db.Float, nullable=True)  # Average time to any interaction

    # Cumulative statistics
    total_campaigns_received = db.Column(db.Integer, default=0)
    total_emails_opened = db.Column(db.Integer, default=0)
    total_links_clicked = db.Column(db.Integer, default=0)
    total_credentials_submitted = db.Column(db.Integer, default=0)
    total_reported_correctly = db.Column(db.Integer, default=0)  # Reported phishing correctly

    # Improvement tracking
    improvement_trend = db.Column(db.String(20), default='stable')  # improving, stable, declining
    last_incident_date = db.Column(db.DateTime, nullable=True)
    consecutive_passes = db.Column(db.Integer, default=0)  # Campaigns passed without clicking
    consecutive_failures = db.Column(db.Integer, default=0)

    # Profile confidence (based on data points)
    profile_confidence = db.Column(db.Float, default=0.0)  # 0-100, increases with more data
    data_points_count = db.Column(db.Integer, default=0)

    # Temporal vulnerability patterns (JSON)
    temporal_patterns = db.Column(db.Text, nullable=True)  # JSON: {day_of_week: score, time_of_day: score}

    # Weakest areas (cached for quick access)
    weakest_technique = db.Column(db.String(50), nullable=True)
    weakest_technique_score = db.Column(db.Float, nullable=True)
    weakest_vector = db.Column(db.String(20), nullable=True)
    weakest_vector_score = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = db.relationship('Employee', backref=db.backref('vulnerability_profile', uselist=False), lazy=True)
    data_points = db.relationship('ProfileDataPoint', backref='profile', lazy=True, cascade='all, delete-orphan')

    def calculate_risk_level(self):
        """Calculate risk level from overall score"""
        if self.overall_vulnerability_score < 25:
            self.risk_level = 'low'
        elif self.overall_vulnerability_score < 50:
            self.risk_level = 'medium'
        elif self.overall_vulnerability_score < 75:
            self.risk_level = 'high'
        else:
            self.risk_level = 'critical'

    def calculate_profile_confidence(self):
        """Calculate confidence based on amount of data"""
        # Confidence increases with more data points, techniques tested, vectors tested
        base_confidence = min(self.data_points_count * 5, 50)  # Up to 50% from data points

        # Add confidence for technique coverage (check how many techniques tested)
        techniques_tested = 0
        for tech in ['urgency', 'authority', 'curiosity', 'fear', 'reward', 'social_proof']:
            score = getattr(self, f'{tech}_susceptibility', 50.0)
            if score != 50.0:  # Changed from default
                techniques_tested += 1
        technique_confidence = (techniques_tested / 6) * 25  # Up to 25% from technique coverage

        # Add confidence for vector coverage
        vectors_tested = 0
        for vector in ['email_phishing', 'spear_phishing', 'qr_phishing', 'sms_phishing']:
            score = getattr(self, f'{vector}_score', 50.0)
            if score != 50.0:
                vectors_tested += 1
        vector_confidence = (vectors_tested / 4) * 25  # Up to 25% from vector coverage

        self.profile_confidence = min(base_confidence + technique_confidence + vector_confidence, 100)

    def find_weakest_areas(self):
        """Identify weakest technique and vector"""
        techniques = {
            'urgency': self.urgency_susceptibility,
            'authority': self.authority_susceptibility,
            'curiosity': self.curiosity_susceptibility,
            'fear': self.fear_susceptibility,
            'reward': self.reward_susceptibility,
            'social_proof': self.social_proof_susceptibility
        }
        vectors = {
            'email': self.email_phishing_score,
            'spear': self.spear_phishing_score,
            'qr': self.qr_phishing_score,
            'sms': self.sms_phishing_score
        }

        self.weakest_technique = max(techniques, key=techniques.get)
        self.weakest_technique_score = techniques[self.weakest_technique]
        self.weakest_vector = max(vectors, key=vectors.get)
        self.weakest_vector_score = vectors[self.weakest_vector]

    def to_dict(self, include_data_points=False):
        import json
        result = {
            'id': self.id,
            'employee_id': self.employee_id,
            'overall_vulnerability_score': self.overall_vulnerability_score,
            'risk_level': self.risk_level,
            'attack_vector_scores': {
                'email_phishing': self.email_phishing_score,
                'spear_phishing': self.spear_phishing_score,
                'qr_phishing': self.qr_phishing_score,
                'sms_phishing': self.sms_phishing_score
            },
            'technique_susceptibility': {
                'urgency': self.urgency_susceptibility,
                'authority': self.authority_susceptibility,
                'curiosity': self.curiosity_susceptibility,
                'fear': self.fear_susceptibility,
                'reward': self.reward_susceptibility,
                'social_proof': self.social_proof_susceptibility
            },
            'behavioral_metrics': {
                'avg_click_time_seconds': self.avg_click_time_seconds,
                'avg_response_time_seconds': self.avg_response_time_seconds,
                'total_campaigns': self.total_campaigns_received,
                'total_opened': self.total_emails_opened,
                'total_clicked': self.total_links_clicked,
                'total_credentials_submitted': self.total_credentials_submitted,
                'total_reported_correctly': self.total_reported_correctly,
                'open_rate': round((self.total_emails_opened / self.total_campaigns_received * 100), 1) if self.total_campaigns_received > 0 else 0,
                'click_rate': round((self.total_links_clicked / self.total_campaigns_received * 100), 1) if self.total_campaigns_received > 0 else 0
            },
            'improvement_trend': self.improvement_trend,
            'last_incident_date': self.last_incident_date.isoformat() if self.last_incident_date else None,
            'consecutive_passes': self.consecutive_passes,
            'consecutive_failures': self.consecutive_failures,
            'profile_confidence': self.profile_confidence,
            'data_points_count': self.data_points_count,
            'temporal_patterns': json.loads(self.temporal_patterns) if self.temporal_patterns else {},
            'weakest_areas': {
                'technique': self.weakest_technique,
                'technique_score': self.weakest_technique_score,
                'vector': self.weakest_vector,
                'vector_score': self.weakest_vector_score
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_data_points:
            result['data_points'] = [dp.to_dict() for dp in self.data_points]
        return result


class ProfileDataPoint(db.Model):
    """
    Individual data point recording an employee's response to a phishing test.
    Used to build and refine the vulnerability profile over time.
    """
    __tablename__ = 'profile_data_points'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(36), db.ForeignKey('vulnerability_profiles.id'), nullable=False)
    employee_id = db.Column(db.String(36), db.ForeignKey('employees.id'), nullable=False)
    program_id = db.Column(db.String(36), db.ForeignKey('campaign_programs.id'), nullable=True)
    scheduled_campaign_id = db.Column(db.String(36), db.ForeignKey('scheduled_campaigns.id'), nullable=True)

    # What was tested
    technique_tested = db.Column(db.String(50), nullable=True)
    vector_type = db.Column(db.String(20), nullable=False)  # email, qr, sms
    difficulty_level = db.Column(db.String(20), nullable=False)

    # Results
    email_opened = db.Column(db.Boolean, default=False)
    link_clicked = db.Column(db.Boolean, default=False)
    credentials_submitted = db.Column(db.Boolean, default=False)
    reported_as_phishing = db.Column(db.Boolean, default=False)

    # Timing
    time_to_open_seconds = db.Column(db.Integer, nullable=True)
    time_to_click_seconds = db.Column(db.Integer, nullable=True)
    time_to_submit_seconds = db.Column(db.Integer, nullable=True)

    # Context
    device_type = db.Column(db.String(20), nullable=True)
    time_of_day = db.Column(db.String(20), nullable=True)  # morning, afternoon, evening, night
    day_of_week = db.Column(db.String(10), nullable=True)

    # Calculated impact on profile scores
    score_impact = db.Column(db.Float, nullable=True)  # How much this changed the profile score

    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    employee = db.relationship('Employee', backref='profile_data_points', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'employee_id': self.employee_id,
            'program_id': self.program_id,
            'technique_tested': self.technique_tested,
            'vector_type': self.vector_type,
            'difficulty_level': self.difficulty_level,
            'email_opened': self.email_opened,
            'link_clicked': self.link_clicked,
            'credentials_submitted': self.credentials_submitted,
            'reported_as_phishing': self.reported_as_phishing,
            'time_to_open_seconds': self.time_to_open_seconds,
            'time_to_click_seconds': self.time_to_click_seconds,
            'device_type': self.device_type,
            'time_of_day': self.time_of_day,
            'day_of_week': self.day_of_week,
            'score_impact': self.score_impact,
            'recorded_at': self.recorded_at.isoformat()
        }


class DepartmentVulnerability(db.Model):
    """
    Aggregated vulnerability metrics for a department.
    Calculated from individual employee profiles.
    """
    __tablename__ = 'department_vulnerabilities'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    department = db.Column(db.String(100), nullable=False, unique=True)

    # Aggregate scores
    avg_vulnerability_score = db.Column(db.Float, default=50.0)
    employee_count = db.Column(db.Integer, default=0)
    profiled_employee_count = db.Column(db.Integer, default=0)  # Employees with profile data
    high_risk_count = db.Column(db.Integer, default=0)  # Employees with score > 70

    # Attack vector breakdown
    email_phishing_avg = db.Column(db.Float, default=50.0)
    spear_phishing_avg = db.Column(db.Float, default=50.0)
    qr_phishing_avg = db.Column(db.Float, default=50.0)
    sms_phishing_avg = db.Column(db.Float, default=50.0)

    # Technique breakdown
    urgency_avg = db.Column(db.Float, default=50.0)
    authority_avg = db.Column(db.Float, default=50.0)
    curiosity_avg = db.Column(db.Float, default=50.0)
    fear_avg = db.Column(db.Float, default=50.0)
    reward_avg = db.Column(db.Float, default=50.0)
    social_proof_avg = db.Column(db.Float, default=50.0)

    # Weakest areas for department
    weakest_technique = db.Column(db.String(50), nullable=True)
    weakest_technique_score = db.Column(db.Float, nullable=True)
    weakest_vector = db.Column(db.String(20), nullable=True)
    weakest_vector_score = db.Column(db.Float, nullable=True)

    # Campaign metrics
    total_campaigns = db.Column(db.Integer, default=0)
    overall_click_rate = db.Column(db.Float, default=0.0)
    overall_submission_rate = db.Column(db.Float, default=0.0)

    # Trend
    trend = db.Column(db.String(20), default='stable')  # improving, stable, declining
    previous_avg_score = db.Column(db.Float, nullable=True)  # For trend calculation

    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'department': self.department,
            'avg_vulnerability_score': self.avg_vulnerability_score,
            'employee_count': self.employee_count,
            'profiled_employee_count': self.profiled_employee_count,
            'high_risk_count': self.high_risk_count,
            'attack_vector_scores': {
                'email_phishing': self.email_phishing_avg,
                'spear_phishing': self.spear_phishing_avg,
                'qr_phishing': self.qr_phishing_avg,
                'sms_phishing': self.sms_phishing_avg
            },
            'technique_scores': {
                'urgency': self.urgency_avg,
                'authority': self.authority_avg,
                'curiosity': self.curiosity_avg,
                'fear': self.fear_avg,
                'reward': self.reward_avg,
                'social_proof': self.social_proof_avg
            },
            'weakest_areas': {
                'technique': self.weakest_technique,
                'technique_score': self.weakest_technique_score,
                'vector': self.weakest_vector,
                'vector_score': self.weakest_vector_score
            },
            'campaign_metrics': {
                'total_campaigns': self.total_campaigns,
                'click_rate': self.overall_click_rate,
                'submission_rate': self.overall_submission_rate
            },
            'trend': self.trend,
            'last_calculated': self.last_calculated.isoformat() if self.last_calculated else None
        }


class AgeGroupVulnerability(db.Model):
    """
    Vulnerability analysis by age group.
    Identifies patterns and effective techniques for different demographics.
    """
    __tablename__ = 'age_group_vulnerabilities'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    age_group = db.Column(db.String(20), nullable=False, unique=True)  # '18-25', '26-35', '36-45', '46-55', '56+'

    # Aggregate metrics
    employee_count = db.Column(db.Integer, default=0)
    avg_vulnerability_score = db.Column(db.Float, default=50.0)

    # Attack vector effectiveness for this age group
    email_susceptibility = db.Column(db.Float, default=50.0)
    qr_susceptibility = db.Column(db.Float, default=50.0)
    sms_susceptibility = db.Column(db.Float, default=50.0)

    # Technique effectiveness
    urgency_effectiveness = db.Column(db.Float, default=50.0)
    authority_effectiveness = db.Column(db.Float, default=50.0)
    curiosity_effectiveness = db.Column(db.Float, default=50.0)
    fear_effectiveness = db.Column(db.Float, default=50.0)
    reward_effectiveness = db.Column(db.Float, default=50.0)
    social_proof_effectiveness = db.Column(db.Float, default=50.0)

    # Most effective attack methods for this age group
    most_effective_technique = db.Column(db.String(50), nullable=True)
    technique_effectiveness_score = db.Column(db.Float, nullable=True)
    most_effective_vector = db.Column(db.String(20), nullable=True)
    vector_effectiveness_score = db.Column(db.Float, nullable=True)

    # Behavioral patterns
    avg_response_time_seconds = db.Column(db.Float, nullable=True)
    click_rate = db.Column(db.Float, default=0.0)
    credential_submission_rate = db.Column(db.Float, default=0.0)

    # Time-based patterns (JSON)
    peak_vulnerability_times = db.Column(db.Text, nullable=True)  # JSON: {day: time ranges}

    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'age_group': self.age_group,
            'employee_count': self.employee_count,
            'avg_vulnerability_score': self.avg_vulnerability_score,
            'vector_susceptibility': {
                'email': self.email_susceptibility,
                'qr': self.qr_susceptibility,
                'sms': self.sms_susceptibility
            },
            'technique_effectiveness': {
                'urgency': self.urgency_effectiveness,
                'authority': self.authority_effectiveness,
                'curiosity': self.curiosity_effectiveness,
                'fear': self.fear_effectiveness,
                'reward': self.reward_effectiveness,
                'social_proof': self.social_proof_effectiveness
            },
            'most_effective': {
                'technique': self.most_effective_technique,
                'technique_score': self.technique_effectiveness_score,
                'vector': self.most_effective_vector,
                'vector_score': self.vector_effectiveness_score
            },
            'behavioral_patterns': {
                'avg_response_time_seconds': self.avg_response_time_seconds,
                'click_rate': self.click_rate,
                'credential_submission_rate': self.credential_submission_rate
            },
            'peak_vulnerability_times': json.loads(self.peak_vulnerability_times) if self.peak_vulnerability_times else {},
            'last_calculated': self.last_calculated.isoformat() if self.last_calculated else None
        }
