import smtplib
import ssl
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr, formatdate
import os
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """
    Email service that supports both global (.env) and user-specific SMTP settings.

    Usage:
        # Use global .env settings (legacy)
        service = EmailService()

        # Use user-specific settings from database
        service = EmailService.from_user_settings(user_settings)
    """

    def __init__(self, smtp_host=None, smtp_port=None, smtp_username=None,
                 smtp_password=None, smtp_from=None, smtp_from_name=None,
                 use_ssl=None, use_tls=None):
        """
        Initialize with provided settings or fall back to .env defaults.
        """
        # Use provided settings or fall back to environment variables
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(smtp_port or os.getenv('SMTP_PORT', 587))
        self.smtp_username = smtp_username or os.getenv('SMTP_USERNAME', '')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD', '')
        self.smtp_from = smtp_from or os.getenv('SMTP_FROM', 'noreply@phishvision.com')
        self.smtp_from_name = smtp_from_name or os.getenv('SMTP_FROM_NAME', '')

        # Handle SSL/TLS settings
        # use_ssl = True means use SMTP_SSL (port 465)
        # use_tls = True means use STARTTLS (port 587)
        if use_ssl is not None:
            self.use_ssl = use_ssl
        elif use_tls is not None:
            # If use_tls is specified, use_ssl is the opposite
            self.use_ssl = not use_tls
        else:
            self.use_ssl = os.getenv('SMTP_SSL', 'false').lower() == 'true'

        # Mock mode if no credentials configured
        self.mock_mode = not (self.smtp_username and self.smtp_password)

    @classmethod
    def from_user_settings(cls, settings, allow_env_fallback=False):
        """
        Create EmailService from user's Settings model instance.

        Args:
            settings: Settings model instance with SMTP configuration
            allow_env_fallback: If True, fall back to .env settings when user hasn't configured SMTP.
                               If False (default), return an unconfigured service that won't send emails.

        Returns:
            EmailService instance configured with user's settings
        """
        if not settings:
            if allow_env_fallback:
                return cls()
            # Return unconfigured service (will be in mock mode and is_configured() returns False)
            return cls(smtp_username=None, smtp_password=None)

        # Check if user has configured SMTP settings
        if not settings.smtp_host or not settings.smtp_username:
            if allow_env_fallback:
                return cls()
            # Return unconfigured service
            return cls(smtp_username=None, smtp_password=None)

        return cls(
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port or 587,
            smtp_username=settings.smtp_username,
            smtp_password=settings.smtp_password,
            smtp_from=settings.smtp_from_email or settings.smtp_username,
            smtp_from_name=settings.smtp_from_name,
            use_tls=settings.smtp_use_tls  # Settings model uses use_tls (True = STARTTLS)
        )

    def is_configured(self):
        """Check if SMTP is properly configured (not in mock mode)."""
        return not self.mock_mode

    def get_config_summary(self):
        """Return a summary of current SMTP configuration (for debugging)."""
        return {
            'host': self.smtp_host,
            'port': self.smtp_port,
            'username': self.smtp_username[:3] + '***' if self.smtp_username else None,
            'from': self.smtp_from,
            'from_name': self.smtp_from_name,
            'use_ssl': self.use_ssl,
            'mock_mode': self.mock_mode
        }

    def send_email(self, to_email, subject, html_content, from_name_override=None):
        """
        Send email via SMTP or mock mode.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            from_name_override: Optional sender display name (overrides instance default)

        Returns:
            True if sent successfully, False otherwise
        """
        # Use override if provided, otherwise use instance default
        from_name = from_name_override if from_name_override else self.smtp_from_name

        if self.mock_mode:
            print(f"[MOCK EMAIL] To: {to_email}")
            print(f"[MOCK EMAIL] Subject: {subject}")
            print(f"[MOCK EMAIL] From: {from_name} <{self.smtp_from}>")
            print(f"[MOCK EMAIL] Content length: {len(html_content)} chars")
            return True

        try:
            # Use simple MIMEText for HTML (not MIMEMultipart) - faster delivery
            msg = MIMEText(html_content, 'html', 'utf-8')
            msg['Subject'] = subject

            # Set From with simple format (like test email)
            if from_name:
                msg['From'] = f"{from_name} <{self.smtp_from}>"
            else:
                msg['From'] = self.smtp_from

            msg['To'] = to_email

            # Minimal headers - less suspicious to spam filters
            msg['Date'] = formatdate(localtime=True)
            msg['Message-ID'] = f"<{uuid.uuid4()}@{self.smtp_from.split('@')[1]}>"

            # Simple SMTP connection (like test email) - faster, less complex
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()

            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] To: {to_email}, Error: {e}")
            return False

    def send_email_with_inline_image(self, to_email, subject, html_content, image_path, image_cid, from_name_override=None):
        """
        Send email with an inline image attachment.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content (use cid:image_cid in img src)
            image_path: Path to the image file
            image_cid: Content-ID for the image (used in HTML as cid:image_cid)
            from_name_override: Optional sender display name

        Returns:
            True if sent successfully, False otherwise
        """
        from_name = from_name_override if from_name_override else self.smtp_from_name

        if self.mock_mode:
            print(f"[MOCK EMAIL] To: {to_email}")
            print(f"[MOCK EMAIL] Subject: {subject}")
            print(f"[MOCK EMAIL] From: {from_name} <{self.smtp_from}>")
            print(f"[MOCK EMAIL] Image: {image_path}")
            return True

        try:
            # Use MIMEMultipart('related') for inline images (required for CID)
            msg = MIMEMultipart('related')
            msg['Subject'] = subject

            # Simple From format (like test email) - faster delivery
            if from_name:
                msg['From'] = f"{from_name} <{self.smtp_from}>"
            else:
                msg['From'] = self.smtp_from

            msg['To'] = to_email

            # Minimal headers only
            msg['Message-ID'] = f"<{uuid.uuid4()}@{self.smtp_from.split('@')[1]}>"
            msg['Date'] = formatdate(localtime=True)

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Attach image
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                image = MIMEImage(img_data)
                image.add_header('Content-ID', f'<{image_cid}>')
                image.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
                msg.attach(image)

            # Simple SMTP connection (like test email) - faster
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()

            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] To: {to_email}, Error: {e}")
            return False

    def send_bulk_emails(self, recipients, subject, html_template_fn):
        """
        Send bulk emails to multiple recipients.

        Args:
            recipients: List of email addresses
            subject: Email subject
            html_template_fn: Function that takes email and returns HTML content

        Returns:
            List of results with email and success status
        """
        results = []
        for recipient in recipients:
            html_content = html_template_fn(recipient)
            success = self.send_email(recipient, subject, html_content)
            results.append({
                'email': recipient,
                'success': success
            })
        return results
